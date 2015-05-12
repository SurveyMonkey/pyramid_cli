import click
from pyramid_cli.cli import main
from montague import load_app, load_server


@main.command()
@click.pass_obj
def serve(config):
    app = load_app(config)
    server = load_server(config)
    server(app)
