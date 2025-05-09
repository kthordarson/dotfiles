#!/bin/bash
cd ~ || exit
git clone https://github.com/ReFirmLabs/binwalk.git
cd binwalk || exit
sudo ./deps.sh
sudo python ./setup.py install
sudo -H pip install git+https://github.com/ahupp/python-magic
sudo -H pip install git+https://github.com/sviehb/jefferson
sudo apt-get install -y postgresql

