FROM python:3.12

WORKDIR /app

COPY src/discord_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/discord_bot /app
COPY settings /app/servermanager/settings

CMD ["python", "bot.py"]