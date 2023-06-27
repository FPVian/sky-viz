#!/bin/bash
cd ..
sudo apt install python3-pip -y &&
sudo apt install python3-venv -y &&
python3 -m venv .venv --upgrade-deps &&
source .venv/bin/activate &&
pip install --editable . &&
cp ../.env.template ../.env
