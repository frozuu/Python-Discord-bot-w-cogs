from discord.ext import commands
import discord

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        print('example cog loaded')

    @commands.command(name='ex')
    async def ex(self, ctx):
        print('ex')


async def setup(bot):
    await bot.add_cog(Example(bot))
    return None
