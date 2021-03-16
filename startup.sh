#! /bin/sh

cd core/repository
../../venv/bin/alembic upgrade head
cd ../..
./venv/bin/python3 -m core run
