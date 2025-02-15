FROM python:3.12

WORKDIR /app
COPY src/server_controller/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/server_controller /app/server_controller
COPY settings /app/server_controller/servermanager/settings
COPY server /app/server_controller/servermanager/server

CMD ["python", "server_controller/main.py"]