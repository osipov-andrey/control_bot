FROM alpine:latest as build

RUN apk update \
    && apk --no-cache add gcc musl-dev \
    && apk add py3-pip python3-dev \
    && pip3 install virtualenv

WORKDIR /app
COPY . .
RUN pip install virtualenv
RUN virtualenv venv && ./venv/bin/pip3 install wheel && ./venv/bin/pip3 install .

RUN sh find_deps.sh ./venv/ > deps.txt

FROM alpine:latest 
WORKDIR /app

COPY --from=build /app/core/ /app/core/
COPY --from=build /app/deps.txt .
COPY --from=build /app/venv/ /app/venv/
COPY --from=build /app/startup.sh /app/startup.sh

RUN apk update \
    && apk add python3
RUN cat deps.txt \
    && cat deps.txt | xargs apk add

EXPOSE 8082
CMD ["sh", "startup.sh"]
