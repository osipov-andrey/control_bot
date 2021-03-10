FROM python:3.8.1-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt && pip install .
EXPOSE 8082
#ENTRYPOINT ["python", "-m", "core"]
CMD ["sh", "startup.sh"]
