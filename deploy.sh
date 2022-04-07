#!/bin/bash
set -o xtrace -o pipefail -o errexit
git clone https://github.com/mobilecoinofficial/full-service-cert-pinning
cd full-service-cert-pinning
./create_app.sh
cd ..
git clone https://github.com/mobilecoinofficial/forestbot-template
cd forestbot-template
cat ../full-service-cert-pinning/*.client_secrets >> dev_secrets
# i guess you have to copy the code you actually want here?
sed 's/template/myotherbot/g' -i Dockerfile
# get fly org interactively
echo "What fly.io organization to use?"
read FLY_ORG
echo "App name?"
read APPNAME
sed "s/<your app here>/$APPNAME/g" -i fly.toml
flyctl create --org $FLY_ORG --name $APPNAME
echo "Bot number?"
read BOT_NUMBER
sed "s/<your number here>/$BOT_NUMBER/g" -i fly.toml
# you've set up a database and
# you've registered and uploaded with wizard.py or something
cat dev_secrets|fly secrets import
fly deploy
