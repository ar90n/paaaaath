#!/usr/bin/env bash

echo "----- install poetry -----"
pip install poetry

echo -e "\n\n----- install packages -----"
poetry install

echo -e "\n\n----- install pre-push hook -----"
poetry run pre-commit install -t pre-push
