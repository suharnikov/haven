#!/usr/bin/env bash

pip3 install --user pdm pdm-venv

pdm venv create

# Hack to make sure that the venv is activated
pdm config
rm .pdm.toml

pdm install
