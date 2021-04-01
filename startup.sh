#! /bin/sh

cd core/repository
../../venv/bin/alembic upgrade head
cd ../..

rabbit=0
for attempt in 1 2 3
	do
	if $( ! nc -zvw3 "${RABBIT_HOST}" "${RABBIT_PORT}" ); then 
		sleep 3
	else 
		echo "Connected to RabbitMQ"
		rabbit=1
		break
        fi
        done
if [ $rabbit -eq 0 ]; then
	echo "Can not connect to RabbitMQ!"
	exit 1
fi

./venv/bin/python3 -m core run
