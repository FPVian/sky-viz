#!/bin/bash
cd ..
sudo apt install python3.11 -y &&
sudo apt install python3-pip -y &&
sudo apt install python3.11-venv -y &&
python3.11 -m venv .venv --upgrade-deps &&
source .venv/bin/activate &&
pip install --editable . &&
