# pique-banserver
Server for syncing bans between several piqueserver instances.

This is very much WIP, functionality is very limited.

Piqueserver includes the `banpublish` and `bansubscribe` options, but this is strictly peer to peer. Centrally collecting bans will
allow a number of possible enhancements.

## setup
If the following makes no sense for you, this is not the project for you (yet), check back later :/

Requirements: python3.5+, virtualenv or pyvenv, pip

1. Create and enter a virtualenv
2. `pip install -r requirements.txt`
3. `python run.py add_server servername`
4. `python main.py run`

You can now do the following:

`GET /` – Get the list of bans

`POST /publish?token=[your token]` – submit a ban. Submit the ban data as JSON-encoded body.

You can submit any data you want, but the following are required fields:
```
{"ip": "0.0.0.0", "server": "localhost", "expires": 0, "timestamp": 0}
```
