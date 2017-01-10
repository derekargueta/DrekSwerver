#!/usr/bin/env bash

apt-get update
apt-get upgrade -y

# install python
apt-get install python3 python3-pip -q -y
pip3 install -U pip
pip3 install -r /vagrant/requirements.txt

cd /vagrant

