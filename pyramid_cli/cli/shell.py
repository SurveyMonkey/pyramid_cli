import click
from pyramid_cli.cli import main
from montague import load_app
from pyramid.scripting import prepare


@main.command()
@click.option(
    '--shell', default='ipython', type=click.Choice(['ipython', 'bpython'])
)
@click.pass_obj
def shell(obj, shell):
    app = load_app(obj.config_file, name=obj.app_env)
    env = prepare()
    env['app'] = app

    values = {
        'app': 'The WSGI application',
        'registry': 'Active Pyramid registry',
        'request': 'Active request object',
    }
    banner = 'Environment:'

    for key in sorted(values.keys()):
        banner += '\n %-12s %s' % (key, values[key])

    if shell == 'ipython':
        from IPython.terminal.embed import InteractiveShellEmbed
        InteractiveShellEmbed(banner2=banner, user_ns=env)()
    elif shell == 'bpython':
        from bpython import embed
        embed(locals_=env, banner=banner)()
