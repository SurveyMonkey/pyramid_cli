import pytest
import os

here = os.path.dirname(__file__)


@pytest.mark.unit
def test_loading_simple_yaml():
    from pyramid_cli.config.yaml import load_yaml

    result = load_yaml(os.path.join(here, '../fixtures/logging.yaml'))
    assert result['handlers']['console']['class'] == 'logging.StreamHandler'


@pytest.mark.unit
def test_including_yaml():
    from pyramid_cli.config.yaml import load_yaml
    result = load_yaml(os.path.join(here, '../fixtures/server.yaml'))
    assert result['handlers']['console']['class'] == 'logging.StreamHandler'
    baz = result['foo']['bar']['baz']
    assert baz['handlers']['console']['class'] == 'logging.StreamHandler'


@pytest.mark.unit
def test_including_bad_yaml():
    from pyramid_cli.config.yaml import load_yaml
    import yaml

    with pytest.raises(yaml.constructor.ConstructorError):
        result = load_yaml(os.path.join(here, '../fixtures/bad_include.yaml'))


@pytest.mark.unit
def test_verify_vars_exist(monkeypatch):
    from pyramid_cli.config.yaml import MissingEnvironmentKey
    from pyramid_cli.config.yaml import load_yaml

    monkeypatch.setenv('ANSVC_DB_URL', 'sqlite://:memory:')
    monkeypatch.setenv('MAIN_DB_USER', 'sontek')
    monkeypatch.setenv('MAIN_DB_PASSWORD', 'is awesome')
    monkeypatch.setenv('DB_1234', 'sm_AccountsNew')

    result = load_yaml(os.path.join(here, '../fixtures/env_vars.yaml'))

    assert result['smlib']['smsqlalchemy']['url'] == 'sqlite://:memory:'
    assert result['smlib']['mongodb']['url'] == 'sontek:is awesome/sm_AccountsNew'


@pytest.mark.unit
def test_verify_env_vars_dont_exist(monkeypatch):
    from pyramid_cli.config.yaml import MissingEnvironmentKeys
    from pyramid_cli.config.yaml import load_yaml

    monkeypatch.setenv('ANSVC_DB_URL', 'sqlite://:memory:')

    with pytest.raises(MissingEnvironmentKeys) as e:
        result = load_yaml(os.path.join(here, '../fixtures/env_vars.yaml'))

    assert str(e.value) == 'missing environment variables: DB_1234, MAIN_DB_PASSWORD, MAIN_DB_USER'


@pytest.mark.unit
def test_verify_env_var_directive_dont_exist(monkeypatch):
    from pyramid_cli.config.yaml import MissingEnvironmentKey
    from pyramid_cli.config.yaml import load_yaml

    monkeypatch.setenv('MAIN_DB_USER', 'sontek')
    monkeypatch.setenv('MAIN_DB_PASSWORD', 'is awesome')
    monkeypatch.setenv('DB_1234', 'sm_AccountsNew')

    with pytest.raises(MissingEnvironmentKey) as e:
        result = load_yaml(os.path.join(here, '../fixtures/env_vars.yaml'))

    assert str(e.value) == 'missing environment variable: ANSVC_DB_URL'


@pytest.mark.unit
def test_bad_env_directive_type():
    from pyramid_cli.config.yaml import load_yaml
    from yaml.constructor import ConstructorError

    with pytest.raises(ConstructorError) as e:
        result = load_yaml(os.path.join(here, '../fixtures/bad_env_var_directive.yaml'))

    assert str(e.value) == 'Unrecognized node type in !env statement'

