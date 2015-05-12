import importlib
import pkgutil

import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--config", "-c",
    type=click.Path(resolve_path=True),
    required=True
)
@click.pass_context
def main(ctx, config):
    ctx.obj = config


# We want to automatically import all of the pyramid_cli.cli.* modules so that
# any commands registered in any of them will be discovered.
for _, name, _ in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    importlib.import_module(name)
