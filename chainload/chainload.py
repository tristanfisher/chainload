import os
import yaml

basedir = os.path.abspath(os.path.dirname(__file__))

# allows for a NoneType object to exist as a value without intentionally discarding it in the lookup precedence
_ABSENT_VALUE_ = type("ChainloadAbsentValue", (object,), {})


def load_file(file_name="config.yaml", yaml_loader=yaml.Loader):
    """Try to load a file from the current directory first, failing that,
    try to load the file_name as an absolute path.

    @param file_name: The YAML or JSON file to read the variable from.
                             Anything that passes a yaml.load() is appropriate here.
    @param yaml_loader: the YAML loader to be used with PyYAML.
                        See PyYaml documentation for how to write constructors to a Loader if needed.
    @return: the file object as a dict if yaml.load() succeeded or an empty dict
    """
    try:
        with open(os.path.join(basedir, file_name), "r") as _cf:
            return yaml.load(_cf, Loader=yaml_loader)
    except IOError:
        try:
            with open(os.path.abspath(file_name)) as _cf:
                return yaml.load(_cf, Loader=yaml_loader)
        except:
            raise Warning("Failed to parse as valid YAML (or JSON): %s" % file_name)
            return {}


def get_option_file(dict_object, var, default=None):
    """Get an option from a dict-type file object.

    @param dict_object: the file object represented as a dict
    @param var: the variable key we want to pull from the file object
    @return: the value of the key or None
    """
    if dict_object:
        return dict_object.get(var, default)
    return None


def get_env_value(environment_variable, default=None):
    """Get a value or a default from an environmental variable, catching TypeError exceptions on an attempt to \
    retreive None.

    @param environment_variable: the environment variable to try to retrieve
    @param default: if the environment variable cannot be retrieved, the value to use
    @return: environment_variable if exists, else default
    """
    # 'TypeError: str expected, not NoneType' if environment_variable is None.
    # uses try/except instead of a magic string, which makes this more verbose, but avoids longer str compares.
    # also needs to tolerate 'environment_variable is None', but we're told to default to the file option
    try:
        return os.getenv(environment_variable, default)
    except TypeError:
        _env = default

    return _env


def chain_load_variable(file_option,
                       environment_variable=None,
                       default=None,
                       file_object=None,
                       attempt_getenv_on_load_file_option_on_missing_envvar_kwarg=True,
                       environment_variable_prefix=_ABSENT_VALUE_
                       ):
    """Load a setting from a precedence-hierarchy.

    Make sure to pass in a file_object instead of loading the file each time, otherwise you'll end up
    with N-file-opens for each setting.

    Setting response order (last wins)
        1. Default
        2. Settings file object
        3a. Env var
        3b. If env var is None, and the specified file option name exists in the env, and this behavior is
        enabled, the alternate env var

    In the near future (2016), this will be:
        1. Default
        2. Remote settings URL
        3. Settings file object
        4. Call to a specified function
            e.g. admin_email = chain_load_setting(..., function=session.query(Admin).filter_by(name='root').email)
        5a. Environment variable
        5b. file option environment-variable if 5a is None and this behavior is enabled


    @param file_option: the variable to load from a file
    @param environment_variable: the environment variable to try to load
    @param default: the default value to set if file object name and environment_variable loading fail
    @param file_object: the file dictionary object to search for variables
    @param attempt_getenv_on_load_file_option_on_missing_envvar_kwarg: if environment_variable is absent or
        otherwise not present, attempt to get an environment variable of the same name as file_option
    @param environment_variable_prefix: if specified, prefix any call to an environment variable with this string
    @return: chain-loaded variable value
    """

    # *specifically* None. Our load_file() returns {} on a failed load. We're doing this for improved messaging:
    if file_object is None:
        raise EnvironmentError("Expected to receive a dictionary to search for settings.  "
                               "Pass file_object={} to this function to skip file loading.")

    # 1
    value = default

    # 2
    _conf_value = get_option_file(file_object, file_option)
    if _conf_value is not None:  # valid _conf_value could be coerced to False
        value = _conf_value

    # 3a
    # prefix the envvar (if exists in class setup) unless we've been explicitly told not to
    if environment_variable_prefix is not _ABSENT_VALUE_:
        environment_variable = "%s%s" % (environment_variable_prefix, environment_variable)

    _env = get_env_value(environment_variable, _ABSENT_VALUE_)

    if _env is not _ABSENT_VALUE_:
        value = _env
    # 3b - either _env was None or we tried a getenv(None) and threw an exception
    elif _env is _ABSENT_VALUE_ and attempt_getenv_on_load_file_option_on_missing_envvar_kwarg:
        if environment_variable_prefix is not _ABSENT_VALUE_:
            file_option = "%s%s" % (environment_variable_prefix, file_option)

        value = os.getenv(file_option, value)

    return value


# explicit object inheritence for Python 2's sake
class ChainloadSetup(object):
    """The base setup of fetching a variable from a hierarchy of sources.

    @param filename: the filename containing the variables desired to load
    @param attempt_getenv_on_file_option: if environment_variable is absent or otherwise not present, attempt to \
    get an environment variable of the same name as file_option
    @param environment_variable_prefix: if specified, prefix any call to an environment variable with this string
    @param yaml_loader: the yaml_loader to employ with yaml.load. the default is typically desired.
    @param extra_options_dict: extra options for the
    """

    def __init__(self,
                 filename=None,
                 attempt_getenv_on_file_option=True,
                 environment_variable_prefix="",
                 yaml_loader = yaml.Loader,
                 extra_options_dict=None):

        self.filename = filename
        self.attempt_getenv_on_file_option = attempt_getenv_on_file_option
        self.environment_variable_prefix = environment_variable_prefix
        self.yaml_loader = yaml_loader
        self.extra_options_dict = extra_options_dict

        self._file_object = None
        self._response = None

        # allows arbitrary setting of options for future use without changing the call signature
        if isinstance(self.extra_options_dict, dict):

            for candidate_key in self.extra_options_dict:
                if candidate_key in self.__dict__:
                    raise ValueError("Key: %s is reserved for use in ChainloadSetup.")

            self.__dict__.update(self.extra_options_dict)


    # no need as a setter as we don't want to support hot-patching the file_object
    @property
    def file_object(self):
        """Returns the file object from the specified file for use with chain_load_variable.

        If this has already been called, the file object will simply be returned.
        Otherwise:
            if self.filename is a string, this will load the file
            if self.filename is a dict, this will simply bind the dict to the instantiation of ChainloadSetup
            else, an empty dictionary will be returned

        @return: a dictionary representation of the intended file object
        """
        if self._file_object is not None:
            return self._file_object
        elif isinstance(self.filename, str):
            _loaded_fo = load_file(file_name=self.filename, yaml_loader=self.yaml_loader)
            self._file_object = _loaded_fo
            return self._file_object
        elif isinstance(self.filename, dict):
            self._file_object = self.filename
            return self._file_object
        else:
            return {}


    def get_value(self, file_option=None, environment_variable=None, default=None, override_prefix=_ABSENT_VALUE_, *args, **kwargs):
        """

        @param file_option: the variable key we want to pull from the file object
        @param environment_variable: the environment variable to try to retrieve
        @param default: if the environment variable cannot be retrieved, the value to use
        @param override_prefix: for this value, if desired, set the prefix to the provided string
        @param args: *args
        @param kwargs: **kwargs
        @return: the value from the environment_variable if exists, else the file option, else default
        """

        self._response = chain_load_variable(
                file_option=file_option,
                environment_variable=environment_variable,
                default=default,
                file_object=self.file_object,
                attempt_getenv_on_load_file_option_on_missing_envvar_kwarg=self.attempt_getenv_on_file_option,
                environment_variable_prefix=self.environment_variable_prefix
            )

        return self._response

    __call__ = get_value
