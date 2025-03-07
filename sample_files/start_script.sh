#!/bin/sh
# These sample files can be used to host a barebones minecraft server
# Read the settings.
. ./settings.sh

# Start the server.
start_server() {
    java -server -Xms${MIN_RAM} -Xmx${MAX_RAM} -jar ${SERVER_JAR} nogui
}

echo "Starting Server..."
start_server