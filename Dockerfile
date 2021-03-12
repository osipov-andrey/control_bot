FROM python:3.8.1-slim
WORKDIR /app
COPY . .
RUN pip install .
EXPOSE 8082
CMD ["sh", "startup.sh"]
