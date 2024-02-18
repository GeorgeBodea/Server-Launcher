FROM python:3.10-alpine
WORKDIR /app
COPY ./src /app
RUN pip install -r ./env_server_launcher/requirements.txt
EXPOSE 5000
CMD python ./main.py