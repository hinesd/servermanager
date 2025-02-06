import discord
import httpx
from discord.ext import commands
from config import DISCORD_TOKEN, SERVER_DNS

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.command()
async def start_server(ctx):
    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            response = await client.get(f"http://{SERVER_DNS}/server/start")
            data = response.json()
            await ctx.send(f"Status Code: {data['status_code']}, Detail: {data['detail']}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


@bot.command()
async def stop_server(ctx):
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"http://{SERVER_DNS}/server/stop")
            data = response.json()
            await ctx.send(f"Status Code: {data['status_code']}, Detail: {data['detail']}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


bot.run(DISCORD_TOKEN)