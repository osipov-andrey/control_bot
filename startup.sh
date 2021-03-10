#! /bin/sh

cd core/repository
alembic upgrade head
cd ../..
python -m core run
