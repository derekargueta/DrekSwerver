#!/usr/bin/env bash

apt-get update

# install python
apt-get install python-dev python-pip -q -y
pip install -U pip
pip install http-parser

