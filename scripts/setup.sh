#!/bin/bash
cd ..
apt install python3.10 -y
apt install python3-pip -y
apt install python3-venv -y
python3 -m venv .venv --upgrade-deps
source .venv/bin/activate
pip install --editable .
