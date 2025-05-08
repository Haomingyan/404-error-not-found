#!/bin/bash

export FLASK_ENV=development
export PROJ_DIR=$PWD
export DEBUG=1  # 1 is cloud MongoDB, 0 is local MongoDB
export GAME_MONGO_PW=goodpassword

# run our server locally:
PYTHONPATH=$(pwd):$PYTHONPATH
FLASK_APP=server.endpoints flask run --debug --host=127.0.0.1 --port=8000
