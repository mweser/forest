Requires python3.9

## Bootstrapping Forestbot 

Use pipenv install to install deps. Install notes for Ubuntu Hirsuite in INSTALL.md

you'll need to grab [https://github.com/forestcontact/signal-cli], check out the stdio-generalized `./gradlew installDist`, and add a symlink from signal-cli/build/install/signal-cli/bin/signal-cli to the working directory. `default-jre` should work for signal-cli. 

you also need to register an account -- you can use https://github.com/forestcontact/go_ham/blob/main/register.py or https://github.com/forestcontact/message-in-a-bottle as a starting point. you can also grab one from the DB if you have access to secrets.

you can use `python3.9 -m forest.datastore upload --number` or `python3.9 -m forest.datastore sync --number` to mess with the DB. your secrets file should be named {prod,staging,dev}_secrets. 

you can use `ENV=prod python3.9 -m forest.datastore` to select said file accordingly. <- deprecated? "ENV=x" alone in the pipenv seems to do the right thing.

## Running Forestbot Locally

You'll need your signal-cli symlinked to the forest-draft directory. `ln -s ~/signal-cli/build/install/signal-cli/bin/signal-cli .`

If you have secrets, `python3.9 -m forest.datastore list_accounts` should show your available accounts. Then you can start it with an available number: `python3.9 contactbot.py +5555555555`

## Running in Docker Locally

`docker build -t contactbot .` then `docker run --env-file dev_secrets contactbot` should work?

## Running Forestbot on fly.io

We use fly.io for hosting. You'll need flyctl: `curl -L https://fly.io/install.sh | sh`. Ask for an invite to our fly organization, or add a payment method to your personal fly account. Use `fly auth` to login.

Create a fly app with `fly launch`. Use a unique-ish name. This is supposed to create a fly.toml. Don't deploy just yet, we still need to add secrets.

Before deploying for the first time, and afterwords to update secrets, run `cat dev_secrets | flyctl secrets import`. If you're managing multiple environments like prod and staging, make multiple secrets files with their own `BOT_NUMBER`, `DATABASE_URL`, etc. Name those files `staging_secrets`, `prod_secrets`, etc. Afterwords, if you want to run stuff locally using a different set of secrets, use e.g. `ENV=prod python3.9 contactbot.py`

Finally, run `fly deploy`. This will build the docker image, upload it to the fly registry, and actually deploy it to fly. After the first time, deploys generally should be `--strategy immediate` to not risk the old instance receiving messages and advancing the ratchet after the new instance has already downloaded the state.

> flyctl deploy [<workingdirectory>] [flags]
>  --strategy string      The strategy for replacing running instances. Options are canary, rolling, bluegreen, or immediate. Default is canary

`fly logs` will give you forestbot's output.

If things seem wrong, you can use `fly suspend`, the above to sync, use signal-cli locally to receive/send --endsession/trust identities/whatever, then `fly resume`


# Options and secrets

- `ENV`: which {ENV}_secrets to use and optionally set as profile family name 
- `BOT_NUMBER`: signal account being used
- `ADMIN`: primarily fallback recipient for invalid webhooks; may also be used to send error messages
- `DATABASE_URL`: Postgres DB
- `TELI_KEY`: token to authenticate with teli
 
## Flags
- `NO_DOWNLOAD`: don't download a datastore, use pwd 
- `NO_MEMFS`: don't autosave. if not `NO_DOWNLOAD`, also create an equivalent tmpdir at /tmp/local-signal and symlink signal-cli process and avatar
- `MONITOR_WALLET`: monitor transactions from full-service. has bugs 
- `SIGNAL_CLI_PATH`: executable to use. useful for running graalvm tracing agent
- `MIGRATE`: run db migrations and set teli sms webhooks
- `LOGFILES`: create a debug.log 
- `ORDER`: allow users to buy phonenumbers
- `GROUPS`: use group routes

## Other stuff

Code style: `mypy *py` and `pylint *py` should not have errors when you push. run `black`. prefer verbose, easier to read names over conciser ones.

TODO: elaborate on

- things we hold evident
- design considerations
- experiments tried

