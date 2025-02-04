# ServerManager

This project will be used to gain experience with containerization, networking, and process management.

## Table of Contents
- [Features](#features)
- [Pre-Install Configurations](#System-Configurations)
- [Installation](#installation)
- [Usage](#usage)

## Introduction
ServerManager is an application that can be used to manage a minecraft server seamlessly with a discord bot.
## Features
- Containerization using Docker
- Networking setup and management through Tailnet
- Discord bot for managing server operations

## System Configurations

1. **Install Java:**
https://www.oracle.com/java/technologies/javase/jdk21-archive-downloads.html
2. **Download Minecraft server jar and place it in `servermanager/src/server_controller/testserver`:** https://www.minecraft.net/en-us/download/server
3. **Add Device to Tailscale and configure Tags/ACL's:** https://tailscale.com/
4. **create a `.env` file in `servermanager` using `.sample-env` as an example**
4. **Generate Tailscale Oauth token and place it in `TS_AUTHKEY` in `.env`**
5. **Take the Tag associated with the Oauth token and place it in `TAILSCALE_TAG`**
6. **Create Discord Bot and add it to Discord Server:** https://discord.com/developers/applications
7. **Generate Discord Bot Token and place it in `DISCORD_TOKEN` in `.env`**


## Installation
To get started with ServerManager, follow these steps:

1. **Clone the repository:**
    ```sh
    git clone https://github.com/hinesd/servermanager.git
    cd servermanager
    ```

2. **Install the required Python packages:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run local Minecraft server:**
    ```sh
    python src/main.py
    ```

4. **Build/Run Discord Bot Docker container:**
    ```sh
    docker compose up --build
    ```

## Usage

1. **Start server with discord bot command:**
    ```sh
    $start_server
    ```

2. **Stop server with discord bot command:**
    ```sh
    $stop_server
    ```
