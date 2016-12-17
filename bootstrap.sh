#!/usr/bin/env bash

apt-get update

# install python
apt-get install python-dev python3-pip -q -y
pip3 install -U pip
pip3 install -r requirements.txt

cd /vagrant

