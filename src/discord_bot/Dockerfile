FROM python:3.12

WORKDIR /app

COPY src/discord_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/discord_bot /app/discord_bot
COPY src/settings /app/discord_bot/settings

CMD ["python", "discord_bot/bot.py"]