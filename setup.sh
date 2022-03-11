#/bin/bash
echo "Installing dependencies.."
sudo apt update
sudo apt install python3.9 python3.9-dev python3-pip
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
poetry install
wget https://github.com/AsamK/signal-cli/releases/download/v0.10.3/signal-cli-0.10.3-Linux.tar.gz
tar -xvf signal-cli-0.10.3-Linux.tar.gz
ln -s ./signal-cli-0.10.3/bin/signal-cli .
poetry add InquirerPy
poetry add rich
poetry run python3 wizard.py

