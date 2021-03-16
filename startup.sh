#! /bin/sh

cd core/repository
../../venv/bin/alembic upgrade head
cd ../..
while ! nc -z "${RABBIT_HOST}" "${RABBIT_PORT}"; do sleep 3; done
./venv/bin/python3 -m core run
