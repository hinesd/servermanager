# ServerManager

This project streamlines Minecraft server deployment and uses discord bot integration for seamless server management.

## Table of Contents
- [Features](#features)
- [System Configurations](#System-Configurations)
- [Installation](#installation)
- [Usage](#usage)

## Features
- Containerized deployment using docker to ensure the application works on all Operating Systems
- Discord bot for managing server operations

## System Configurations
| <h5>**Configuration Step**     | <h5>**Required Configurations**                                                                                                                                                                                                                                                                                                                         |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Configure Minecraft Server  | - Place Minecraft server.jar in the `servermanager/server` directory for a barebones minecraft server. https://www.minecraft.net/en-us/download/server<br/><br>- If using a modpack, extract the modpack's content into `servermanager/server` and make sure the server.jar and start scripts are present.                                              |
| 2. Configure Local Environment | - Install Docker Desktop https://www.docker.com/products/docker-desktop/<br/><br/>- If the Minecraft Server requires custom configurations, create `.env` file and place it in the `servermanager` directory. Copy the content of `.sample-env` into your newly created `.env` file.<br/>ie. specifying different `JAVA_VERSION`(Default version is 21) |

| <h>**Configuration Step**      | <h5>**Optional Configurations**                                                                                                                                                       |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Configure Local Environment | create `.env` file and place it in the `servermanager` directory. Copy the content of `.sample-env` into your newly created `.env` file.<br/>If file already exists, ignore this step |
| 2. Configure Discord Bot       | If using a discord bot for server manager controls, generate a bot token and place it in the `DISCORD_TOKEN` attribute in the `servermanager/.env` file to keep it private            |



## Installation
To get started with ServerManager, follow these steps:

1. **Clone the repository:**
    ```sh
    git clone https://github.com/hinesd/servermanager.git
    cd servermanager
    ```
2. **Configure System:**<br/> Follow [System Configurations](#System-Configurations) instructions

3. **Build System:**
    ```sh
    make build
    ```
4. **Run System:**
    ```sh
    make run
    ```

## Usage
### Bot commands
1. **Running the server** - `$server_start`
2. **Getting server status** - `$server_status`
3. **Stopping the server** - `$server_stop`

### API calls
1. **Running the server** - http://0.0.0.0/server/start
2. **Getting server status** - http://0.0.0.0/server/status
3. **Stopping the server** - http://0.0.0.0/server/stop
