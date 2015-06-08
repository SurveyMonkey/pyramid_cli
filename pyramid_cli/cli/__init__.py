import importlib
import pkgutil

import click


class Config(object):
    def __init__(self, config_file, app_env, server_env):
        self.config_file = config_file
        self.app_env = app_env
        self.server_env = server_env


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--config", "-c",
    type=click.Path(resolve_path=True),
    required=True
)
@click.option(
    "--app-env", "-a",
    required=False,
    default='main'
)
@click.option(
    "--server-env", "-s",
    required=False,
    default='main'
)
@click.pass_context
def main(ctx, config, app_env, server_env):
    obj = Config(config, app_env, server_env)
    ctx.obj = obj


# We want to automatically import all of the pyramid_cli.cli.* modules so that
# any commands registered in any of them will be discovered.
for _, name, _ in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    importlib.import_module(name)
