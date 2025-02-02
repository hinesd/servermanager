import discord
import httpx
from discord.ext import commands
from config import DISCORD_TOKEN, SERVER_DOMAIN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def start_server(ctx):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_DOMAIN}/server/start")
        if response.status_code == 200:
            await ctx.send('Minecraft server started successfully!')
        else:
            await ctx.send(f'Failed to start server: {response.json()["detail"]}')

@bot.command()
async def stop_server(ctx):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_DOMAIN}/server/stop")
        if response.status_code == 200:
            await ctx.send('Minecraft server stopped successfully!')
        else:
            await ctx.send(f'Failed to stop server: {response.json()["detail"]}')

bot.run(DISCORD_TOKEN)