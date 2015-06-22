import click
from pyramid_cli.cli import main
from montague import load_server


@main.command()
@click.pass_obj
def serve(obj):
    server = load_server(obj.config_file, name=obj.server_env)
    server(obj.app)
