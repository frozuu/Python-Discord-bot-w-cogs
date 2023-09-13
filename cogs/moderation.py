import sys
import traceback
import discord
import psutil
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @commands.Cog.listener()
    async def on_ready(self):
        print('moderation cog loaded')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kicked. Reason: {reason}')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned.')

    @commands.command(aliases=['c'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        max_amount = 90
        if int(amount) > max_amount:
            await ctx.send(f"Sorry, you can only clear up to {max_amount} messages at once.")
            return

        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{amount} messages have been cleared.', delete_after=5)

    @clear.error
    async def clear_error(self, ctx, error, *args):
        if isinstance(error, commands.CommandOnCooldown):
            remaining = error.retry_after
            message = f'This command is on cooldown. Please try again in {remaining:.2f} seconds.'
            await ctx.send(message)

    @commands.command()
    @commands.is_owner()
    async def debug(self, ctx):
        """Displays debug information about the bot."""

        # Get process information for memory usage
        process = psutil.Process()
        mem_info = process.memory_info()

        embed = discord.Embed(title="Bot Debug Information", color=0x194D33)
        embed.add_field(name="Guild Count", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="Uptime", value=f"{datetime.datetime.utcnow() - self.start_time}", inline=True)
        embed.add_field(name="Latency", value=f"{self.bot.latency * 1000:.2f} ms", inline=True)
        embed.add_field(name="Memory Usage", value=f"{mem_info.rss / (1024 * 1024):.2f} MB", inline=True)
        embed.add_field(name="Number of Commands Loaded", value=f"{len(self.bot.commands)}", inline=True)
        embed.add_field(name="Number of Cogs Loaded", value=f"{len(self.bot.cogs)}", inline=True)

        # Get the traceback information for the last exception
        last_traceback = traceback.format_exception(*sys.exc_info())
        if last_traceback:
            traceback_text = "".join(last_traceback)
            if len(traceback_text) > 1024:
                traceback_text = traceback_text[:1020] + "..."
            embed.add_field(name="Last Exception", value=f"```{traceback_text}```", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
