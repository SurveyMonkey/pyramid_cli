import click
from pyramid_cli.cli import main
from montague import load_app, load_server


@main.command()
@click.pass_obj
def serve(obj):
    app = load_app(obj.config_file, name=obj.app_env)
    server = load_server(obj.config_file, name=obj.server_env)
    server(app)
