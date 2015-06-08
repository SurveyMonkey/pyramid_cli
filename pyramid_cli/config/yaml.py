# encoding: utf-8
import copy
from montague.interfaces import IConfigLoader, IConfigLoaderFactory
from montague.structs import LoadableConfig, DEFAULT
from montague.vendor import reify
from zope.interface import directlyProvides, implementer
from jinja2 import Environment
from jinja2 import StrictUndefined

import yaml
import os
import re
import logging
import sys

logger = logging.getLogger(__name__)

config_keys_re = re.compile(r'\{\{(?P<name>[\w\d\s]*)\}\}', re.IGNORECASE)
env = Environment(undefined=StrictUndefined)


class MissingEnvironmentKey(Exception):
    def __init__(self, key):
        super(MissingEnvironmentKey, self).__init__(
            'missing environment variable: %s' % key
        )


class MissingEnvironmentKeys(Exception):
    def __init__(self, missing_keys):
        csv = ', '.join(sorted(missing_keys))
        msg = 'missing environment variables: %s' % csv
        super(MissingEnvironmentKeys, self).__init__(msg)


def verify_and_replace_vars(raw_yaml, env_vars):
    missing_keys = set()
    matches = config_keys_re.findall(raw_yaml)

    for key_name in matches:
        key_name = key_name.strip()
        if key_name not in env_vars:
            missing_keys.add(key_name)

    if missing_keys:
        raise MissingEnvironmentKeys(missing_keys)

    rendered = env.from_string(raw_yaml).render(**env_vars)
    return rendered


def load_yaml(filename):
    """
    Load yaml from file object or filename.
    """
    cfg = {}

    with open(filename, 'rb') as f:
        results = yaml.load_all(f, Loader)

        for result in results:
            cfg.update(result)

    return cfg


class Loader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        self.env_vars = os.environ.copy()
        raw_yaml = stream.read().decode('utf-8')
        rendered = verify_and_replace_vars(raw_yaml, self.env_vars)

        super(Loader, self).__init__(rendered)

        Loader.add_constructor('!include', Loader.include)
        Loader.add_constructor('!env', Loader.load_env)

    def load_env(self, node):
        """
        Allows to use an environment variable

        database_url = !env DATABASE_URL
        """
        if isinstance(node, yaml.ScalarNode):
            key_name = self.construct_scalar(node)
            if key_name in self.env_vars:
                return self.env_vars[key_name]
            raise MissingEnvironmentKey(key_name)
        else:
            msg = 'Unrecognized node type in !env statement'
            raise yaml.constructor.ConstructorError(msg)

    def include(self, node):
        """
        Allows loading relatives paths within the YAML:

        logging: !include logging.yaml
        """
        if isinstance(node, yaml.ScalarNode):
            return self.extract_file(self.construct_scalar(node))
        else:
            msg = 'Unrecognized node type in !include statement'
            raise yaml.constructor.ConstructorError(msg)

    def extract_file(self, filename):
        file_path = os.path.join(self._root, filename)
        return load_yaml(file_path)


@implementer(IConfigLoader)
class YAMLConfigLoader:
    directlyProvides(IConfigLoaderFactory)

    def __init__(self, path):
        self.path = path

    @reify
    def _config(self):
        return load_yaml(self.path)

    def config(self):
        config = {}
        for section, vals in self._config.items():
            if 'main' in vals:
                vals = copy.deepcopy(vals)
                vals[DEFAULT] = vals.pop('main')
            config[section] = vals
        return config

    def app_config(self, name):
        if name is DEFAULT:
            name = 'main'
        # Obviously this will throw a KeyError if the config isn't there.
        # A real implementation would have error handling here.
        if name not in self._config['application']:
            logger.error(
                '%s is not defined in your application config' % name
            )
            sys.exit(-1)

        config = self._config['application'][name]
        return LoadableConfig.app(name=name, config=config, global_config={})

    def server_config(self, name):
        if name is DEFAULT:
            name = 'main'

        config = self._config['server'][name]

        return LoadableConfig.server(
            name=name, config=config, global_config={}
        )
