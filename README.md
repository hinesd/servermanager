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
#### todo: automate away the need to copy sample files if hosting barebones minecraft server and not using optional configurations 

| <h5>**Configuration Step**     | <h5>**Required Configurations**                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Configure Minecraft Server  | - Place Minecraft server.jar in the `servermanager/server` directory for a barebones minecraft server. https://www.minecraft.net/en-us/download/server<br/><br>- Copy files from `servermanager/sample_files` into `servermanager/server` if hosting barebones minecraft server <br/><br/>- If using a modpack, extract the modpack's content into `servermanager/server` and make sure the server.jar and start scripts are present.                                                                                                       |
| 2. Configure Local Environment | - Install Docker Desktop https://www.docker.com/products/docker-desktop/<br/><br/>- If the Minecraft Server requires custom configurations (Using a modpack or Optional Configurations) Create a `.env` file and place it in the `servermanager` directory. Default configurations exist in `.sample-env`<br/><br/>ie. specifying different `JAVA_VERSION`(Default version is 21)<br/> ie. specifying modpacks start script(Default uses `start_script.sh` located in `sample_files`) |

| <h>**Configuration Step** | <h5>**Optional Configurations**                                                                                                                                                       |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Configure Discord Bot  | If using a discord bot for server manager controls, generate a bot token and place it in the `DISCORD_TOKEN` attribute in the `servermanager/.env` file to keep it private            |



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
