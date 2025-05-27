#!/bin/sh
pip install pylint
pip install -r requirements.txt
pylint --fail-under=8 application/src/