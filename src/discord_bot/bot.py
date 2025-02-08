import discord
import httpx
from discord.ext import commands
from config import DISCORD_TOKEN, SERVER_DNS

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

safe_commands = {
        'minecraft': ['server_start'],
        'admin': True
    }

def check_channel_permissions(channel, command):

    permission = safe_commands.get(channel)
    return permission is True or (permission and command in permission)

@bot.command()
async def server_start(ctx):
    channel_name = ctx.channel.name.lower()
    if not check_channel_permissions(channel_name, 'server_start'):
        if channel_name in safe_commands:
            await ctx.send(f"This channel doesn't have permissions to use this command.")
        return
    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            await ctx.send(f"Attempting to start server")
            response = await client.get(f"http://{SERVER_DNS}/server/start")
            data = response.json()
            await ctx.send(f"Status Code: {data['status_code']}, Detail: {data['detail']}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


@bot.command()
async def server_stop(ctx):
    channel_name = ctx.channel.name.lower()
    if not check_channel_permissions(channel_name, 'server_stop'):
        if channel_name in safe_commands:
            await ctx.send(f"This channel doesn't have permissions to use this command.")
        return
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            await ctx.send(f"Attempting to stop server")
            response = await client.get(f"http://{SERVER_DNS}/server/stop")
            data = response.json()
            await ctx.send(f"Status Code: {data['status_code']}, Detail: {data['detail']}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


@bot.command()
async def server_status(ctx):
    channel_name = ctx.channel.name.lower()
    if not check_channel_permissions(channel_name, 'server_status'):
        if channel_name in safe_commands:
            await ctx.send(f"This channel doesn't have permissions to use this command.")
        return
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"http://{SERVER_DNS}/server/status")
            data = response.json()
            await ctx.send(f"Status Code: {data['status_code']}, Detail: {data['detail']}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


bot.run(DISCORD_TOKEN)