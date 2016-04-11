import os
import chainload

test_settings_from_file = chainload.load_file("tests/test_settings.yaml")


def test_file_loaded():
    """test that a file object is correctly loaded as a dictionary"""
    assert isinstance(test_settings_from_file, dict)


def test_default_only():
    """test that when only given a default, we get our default value"""
    _ = chainload.chain_load_variable("__missing", "__missing", 1, test_settings_from_file)
    assert _ == 1

def test_file():
    """test that a value is loaded from our file if file and default are set"""
    _ = chainload.chain_load_variable("environment", "environment", "debug", test_settings_from_file)
    assert _ == "production"


def test_file_and_envvar():
    """test that a value is loaded from our env var if present in the file and a default is provided"""
    os.environ["environment"] = "testing"
    _ = chainload.chain_load_variable("environment", "environment", "debug", test_settings_from_file)
    assert _ == "testing"


def test_file_envvar_and_default():
    """test that if an env var and a default are present, the env var is loaded"""
    os.environ["environment"] = "testing"
    _  = chainload.chain_load_variable("__missing", "environment", "debug", test_settings_from_file)
    assert _ == "testing"


def test_envvar_default_config_option_envvar():
    """test that if an env var, value in file, and default are present, but the env var only exists as specified \
for the file, and the option to default to this value is enabled, the env var default-to-file-option is picked"""
    os.environ["environment"] = "testing"
    _ = chainload.chain_load_variable("environment", "chain_environment", "debug", test_settings_from_file,
                                      # implicit but specify to make test obvious
                                      attempt_getenv_on_load_file_option_on_missing_envvar_kwarg=True)
    assert _ == "testing"


def test_envvar_no_default_config_option_envvar():
    """test that if an env var, value in file, and default are present, but the env var only exists as specified for \
the file, and the option to default to this value is not enabled, the precedence selects the file value"""
    os.environ["environment"] = "testing"
    _  = chainload.chain_load_variable("environment", "chain_environment", "debug", test_settings_from_file,
                                      attempt_getenv_on_load_file_option_on_missing_envvar_kwarg=False)
    assert _ == "production"


def test_envvar_of_None_no_default_config_option_envvar():
    """test that if an env var, value in file, and default are present, but the env var is a None type, \
the value is loaded from file"""
    _  = chainload.chain_load_variable("environment", None, "debug", test_settings_from_file,
                                      attempt_getenv_on_load_file_option_on_missing_envvar_kwarg=False)
    assert _ == "production"


def test_envvar_of_None_file_of_None_no_default_config_option_envvar():
    """test that if an env var, value in file, and default are present, but the env var is a None type, \
the value is loaded from file"""
    _  = chainload.chain_load_variable(None, None, "debug", test_settings_from_file,
                                      attempt_getenv_on_load_file_option_on_missing_envvar_kwarg=False)
    assert _ == "debug"