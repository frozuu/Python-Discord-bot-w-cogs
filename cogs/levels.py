import discord
from discord.ext import commands
import json
import os
import typing

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = {}
        self.levels_file = 'levels.json'
        self.load_levels()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Levels cog loaded')

    def load_levels(self):
        if not os.path.exists(self.levels_file):
            with open(self.levels_file, 'w') as f:
                json.dump({}, f)
        with open(self.levels_file, 'r') as f:
            self.levels = json.load(f)
            for guild_id, users in self.levels.items():
                for user_id, data in users.items():
                    if 'xp' not in data:
                        data['xp'] = 0
                    if 'level' not in data:
                        data['level'] = 0

    def save_levels(self):
        with open(self.levels_file, 'w') as f:
            json.dump(self.levels, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {'xp': 0, 'level': 0}
        self.levels[guild_id][user_id]['xp'] += 1
        if self.levels[guild_id][user_id]['xp'] >= 5 * (self.levels[guild_id][user_id]['level'] + 1) ** 2:
            self.levels[guild_id][user_id]['level'] += 1
            self.levels[guild_id][user_id]['xp'] = 0  # Reset the XP to 0 after leveling up
            await message.channel.send(
                f'Congrats {message.author.mention}, you reached level {self.levels[guild_id][user_id]["level"]}! <a:DJ:1088552688540713022> ')
        next_level_xp = 5 * (self.levels[guild_id][user_id]['level'] ** 2) + 50 * self.levels[guild_id][user_id][
            'level'] + 100
        self.save_levels()

    @commands.command(aliases=['lvl', 'level', 'leaderboard'])
    async def rank(self, ctx, member: typing.Optional[discord.Member] = None):
        if not member:
            member = ctx.author
        else:
            member = member
        level = self.levels.get(str(ctx.guild.id), {}).get(str(member.id), {}).get("level", 0)
        xp = self.levels.get(str(ctx.guild.id), {}).get(str(member.id), {}).get("xp", 0)


        embed = discord.Embed(title=f"{member.display_name}'s Rank", color=member.color)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="XP", value=xp, inline=True)

        # get top 10 users by level on the server
        top_users = sorted(self.levels.get(str(ctx.guild.id), {}).items(), key=lambda x: x[1]["level"], reverse=True)[
                    :10]
        top_users_str = ""
        for i, (user_id, user_data) in enumerate(top_users):
            user = ctx.guild.get_member(int(user_id))
            if user:
                top_users_str += f"{i + 1}. {user.display_name}: Level {user_data['level']} ({user_data['xp']} XP)\n"

        if top_users_str:
            embed.add_field(name="Top 10 Users by Level", value=top_users_str, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Levels(bot))
    return None