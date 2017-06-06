import json
import logging
import os

from aiohttp import web
from tinydb import TinyDB, Query
import click

db = TinyDB("db.json")

bans = db.table("bans")
servers = db.table("servers")

logging.basicConfig(level=logging.INFO)

def authorize(token):
    if token is None:
        return False

    server = Query()
    result = servers.search(server.token == token)
    print(result)
    if len(result) == 0:
        return False
    return True

def validate(data):
    return all(key in data for key in ["ip", "server", "expires", "timestamp"])

async def get_banlist(request):
    return web.json_response(bans.all())

async def publish_ban(request):
    token = request.query.get("token", None)

    if not authorize(token):
        return web.json_response(
            {"ok": "false", "error": "unauthorized"}, status=403)

    data = await request.json()
    if not validate(data):
        return web.json_response(
            {"ok": "false", "error": "invalid data"}, status=400)

    bans.insert(data)
    logging.info("ban added: %s", data)
    return web.json_response({"ok": True})

app = web.Application()
app.router.add_get('/', get_banlist)
app.router.add_post('/publish', publish_ban)
# app.router.add_get('/{name}', handle)

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

@click.group()
def cli():
    pass

@cli.command()
def run():
    """
    Run the banpublish server
    """
    web.run_app(app, host="0.0.0.0", port=8080)

@cli.command()
@click.argument("name")
@click.option('--token',
    help='set a specific token. It is recommended you leave this unset')
def add_server(name, token):
    """
    Add new server and allow it to publish bans
    """
    if token is None:
        token = os.urandom(20).hex()

    if len(servers.search(Query().token == token)):
        raise click.BadParameter("token is already in use")

    if len(servers.search(Query().name == name)):
        raise click.BadParameter("name is already in use")

    servers.insert({"name": name, "token": token})
    click.echo("New Server '{}' successfully added!".format(name))
    click.echo("token: {}".format(token))

@cli.command()
def list_servers():
    """
    List servers allowed to publish bans
    """
    click.echo("NAME   TOKEN")
    for i in servers.all():
        click.echo("{} {}".format(i["name"], i["token"]))

@cli.command()
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to delete all servers?')
def clear_servers():
    db.purge_table("servers")
    click.echo("cleared all servers")

if __name__ == '__main__':
    cli()
