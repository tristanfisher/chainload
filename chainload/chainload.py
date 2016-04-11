import os
import yaml

basedir = os.path.abspath(os.path.dirname(__file__))


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
            return {}


def get_option_file(dict_object, var):
    """Get an option from a dict-type file object.

    @param dict_object: the file object represented as a dict
    @param var: the variable key we want to pull from the  file object
    @return: the value of the key or None
    """
    if dict_object:
        return dict_object.get(var, None)
    return None


def chain_load_variable(file_option,
                       environmental_variable=None,
                       default=None,
                       file_object=None,
                       attempt_getenv_on_load_file_option_on_missing_envvar_kwarg=True
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
        5a. Environmental variable
        5b. file option environmental-variable if 5a is None and this behavior is enabled


    @param file_option: the variable to load from a file
    @param environmental_variable: the environmental variable to try to load
    @param default: the default value to set if file object name and environmental_variable loading fail
    @param file_object: the file dictionary object to search for variables
    @param attempt_getenv_on_load_file_option_on_missing_envvar_kwarg: if environmental_variable is absent or
        otherwise not present, attempt to get an environmental variable of the same name as file_option
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
    # 'TypeError: str expected, not NoneType' if environmental_variable is None.
    # uses try/except instead of a magic string, which makes this more verbose, but avoids longer str compares.
    # also needs to tolerate 'environmental_variable is None', but we're told to default to the file option
    try:
        _env = os.getenv(environmental_variable, None)
        if _env is not None:
            return _env
    except TypeError:
        pass

    # 3b - either _env was None or we tried a getenv(None) and threw an exception
    if attempt_getenv_on_load_file_option_on_missing_envvar_kwarg:
        return os.getenv(file_option, value)

    return value