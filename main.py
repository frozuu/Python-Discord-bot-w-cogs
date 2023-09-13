import discord
import asyncio
import configparser
from discord.ext import commands
import os

intents = discord.Intents.all()
intents.message_content = True

config = configparser.ConfigParser()
config.read('settings.ini')

bot_token = config['BOT']['TOKEN']
prefix_ini = config['BOT']['PREFIX']

if not bot_token:
    bot_token = input("ZAPOMNIALES PODAC TOKEN BOTA MOZESZ GO PODAC TUTAJ JEDNORAZOWO\npodaj TOKEN bota: ")

if not prefix_ini:
    prefix_ini = input("ZAPOMNIALES PODAC PREFIX BOTA MOZESZ GO PODAC TUTAJ JEDNORAZOWO\npodaj prefix bota: ")
bot = commands.Bot(command_prefix=prefix_ini, intents=intents)  # BOT PREFIX


@bot.event
async def on_ready():
    activity = discord.Game(name=f"{prefix_ini}help", type=3)
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print(f'\n\nLogged in as: {bot.user.name} \nID: {bot.user.id}\nDiscord Version: {discord.__version__}\n')


@bot.command(aliases=['r'])
async def reload(ctx, cog):
    # Check that the user invoking the command has the correct ID
    if ctx.author.id != 706829012693155892:
        return await ctx.send("You are not authorized to use this command.")

    # Attempt to unload the cog
    try:
        await bot.unload_extension(f"cogs.{cog}")
    except Exception as e:
        await ctx.send(f"Failed to unload cog: {cog}\n```{e}```")

    # Attempt to load the cog
    try:
        await bot.load_extension(f"cogs.{cog}")
    except Exception as e:
        await ctx.send(f"Failed to load cog: {cog}\n```{e}```")

    # Handle the MissingRequiredArgument error
    except discord.ext.commands.errors.MissingRequiredArgument:
        return await ctx.send("Please specify which cog to reload. Usage: `!reload <cog>`")

    await ctx.send(f"{cog} reloaded!")


async def load():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def main():
    await load()


asyncio.run(main())
bot.run(bot_token)
