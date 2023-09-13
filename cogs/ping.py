import discord
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ping cog loaded.')

    @commands.command(name='ping', pass_context=True, aliases=['latency'])
    async def ping(self, ctx):
        embed = discord.Embed(
            title="__**✅ PING**__",
            colour=discord.Color.green(),
            timestamp=ctx.message.created_at
        )
        embed.add_field(name='Bot latency :', value=f'`{round(self.bot.latency * 1000)} ms`')
        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Ping(bot))
    return None
