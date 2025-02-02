FROM python:3.12
# CURRENTLY WE ARE ONLY RUNNING THE DISCORD BOT FROM DOCKER
# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/discord_bot /app

# Copy the config.py file
COPY config.py /app

# Command to run your application
CMD ["python", "bot.py"]