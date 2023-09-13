import discord
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)  # BOT PREFIX
bot.remove_command('help')
@bot.event
async def on_ready():
    activity = discord.Game(name=".help", type=3)
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print(f'\n\nLogged in as: {bot.user.name} \nID: {bot.user.id}\nDiscord Version: {discord.__version__}\n')

@bot.command()
async def help(ctx):
    commands_list = [f"`{command.name}` - {command.help}" for command in bot.commands]
    message = "\n".join(commands_list)
    await ctx.send(f"**Available commands:**\n{message}")

@bot.command(name="ping", pass_context=True, aliases=["latency"])
async def ping(ctx):
    embed = discord.Embed(title="__**✅ PING**__", colour=discord.Color.green(), timestamp=ctx.message.created_at)
    embed.add_field(name="Bot latency :", value=f"`{round(bot.latency * 1000)} ms`")

    await ctx.send(embed=embed)

bot.run("NzUxNTQ1MjA3MTE5NTQ0Mzcx.G8z691.Sn8uV-Tud__cu0oODrFpbtYb3MKENK-IVAoEIU")