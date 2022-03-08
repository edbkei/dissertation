#!/bin/sh
cd ~/dissertation/Flask/ledgerserver
export FLASK_ENV=development
export FLASK_APP=server
flask run --host=0.0.0.0
