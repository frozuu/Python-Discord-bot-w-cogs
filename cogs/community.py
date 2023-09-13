import json
import discord
from discord.ext import commands


class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 820752797238558720
        self.channel_id = 1087795568199335996

    @commands.Cog.listener()
    async def on_ready(self):
        print('Community cog loaded')


    @commands.command()
    async def feedback(self, ctx, *, message=None):
        if message is None:
            feedback_embed = discord.Embed(
                title="Error",
                description="Please provide a feedback message after the command. This message will be sent to the bot owner. You can use this command to report issues with the bot or suggest new ideas.\n`.feedback your feedback`",
                color=discord.Color.red()
            )
            await ctx.send(embed=feedback_embed)
            return

        guild = self.bot.get_guild(self.guild_id)
        channel = guild.get_channel(self.channel_id)

        user_id = str(ctx.author.id)
        user_tag = str(ctx.author)

        feedback_embed = discord.Embed(
            title=f"Feedback from {user_tag}",
            description=f"{message}\n\nUser ID: {user_id}",
            color=discord.Color.green()
        )

        await channel.send(embed=feedback_embed)

        await ctx.send("Thank you for your feedback! Your message has been sent to the bot owner for review.")

    @commands.command()
    async def great(self, ctx, user_id: int, amount: float):
        if str(ctx.author.id) != '706829012693155892':
            await ctx.send(f"Only bot owner can use this command.")
            return

        with open('money.json', 'r') as f:
            money = json.load(f)

        if str(user_id) in money:
            money[str(user_id)] += amount
        else:
            money[str(user_id)] = amount

        with open('money.json', 'w') as f:
            json.dump(money, f)

        user = await self.bot.fetch_user(user_id)
        await user.send(f"Thank you for your feedback! The bot owner has sent you {amount} money as a reward.<:giftt:1088553916171550751>")

        await ctx.send(f"{amount} money has been sent to <@{user_id}> as a reward for their feedback.")

    @commands.command(aliases=['new'])
    async def news(self, ctx):
        # Set your news text here
        news_text = "**Added!\n<:starico:1088974712744448121> +news\n<:starico:1088974712744448121>" \
                    " currency is now ¥" \
                    "\n<:starico:1088974712744448121> +New Job and new items in shop\n<:starico:1088974712744448121>Updated the appearance of the .jobs command\n\tFixed:\n<:goldbug:1088974715449782272> .shop and jobs\n<:goldbug:1088974715449782272> " \
                    "fixed the issue where the `.shop` was not loading the amount of money for new users.**\n<:goldbug:1088974715449782272> **Fixed shop even more**"

        # Create a new embed with the news text as the description
        embed = discord.Embed(title="Latest News", description=news_text, color=0x00ff00)
        embed.set_footer(text="23.03.2023 23:45 - 30.03.2023 23:45 GMT+1")


        # Send the embed to the channel where the command was called
        await ctx.send(embed=embed)




async def setup(bot):
    await bot.add_cog(Community(bot))
    return None
