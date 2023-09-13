import asyncio

import discord
import json
import random
from datetime import datetime, timedelta
from discord.ext import commands


class Jobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

        # Load money from money.json
        with open("money.json", "r") as f:
            self.money = json.load(f)

        # Load inventory from inventory.json
        with open("inventory.json", "r") as f:
            self.inventory = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Jobs cog loaded')

    @commands.command(aliases=['job', 'work'])
    async def jobs(self, ctx):
        job_info = {
            "Fisherman": "Requires Fishing Bait and basic fishing rod",
            "Timberman": "Requires Basic Axe",
            "Taxi": "Requires Taxi car and Driver license"
        }

        embed = discord.Embed(title="Available Jobs", description="Here are the available jobs:")
        for job, info in job_info.items():
            embed.add_field(name=job, value=info, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['fish'])
    async def fishing(self, ctx):
        with open('inventory.json', 'r') as f:
            inventory = json.load(f)

        user_id = str(ctx.author.id)
        if user_id not in inventory:
            await ctx.send("You don't have an inventory yet. Use the `.shop` and `.daily` command to create one.")
            return

        user_items = inventory[user_id]['items']

        required_items = ["Basic_Fishing_Rod", "Fishing_Bait"]

        for item in required_items:
            if item not in user_items or user_items[item]['quantity'] < 1:
                await ctx.send(f"You don't have a {item}.")
                return

        bait_item = user_items['Fishing_Bait']
        bait_durability = bait_item.get('durability', 10)

        # Cooldown time for fishing
        cooldown_time = timedelta(minutes=5)
        last_fishing_time = datetime.now() - cooldown_time
        if 'last_fishing_time' in inventory[user_id]:
            last_fishing_time = datetime.fromisoformat(inventory[user_id]['last_fishing_time'])
            if last_fishing_time + cooldown_time > datetime.now():
                remaining_time = last_fishing_time + cooldown_time - datetime.now()
                minutes, seconds = divmod(remaining_time.seconds, 60)
                if remaining_time.days == 0:
                    if minutes == 0:
                        embed = discord.Embed(title="On Cooldown",
                                              description=f"You can fish again in **{seconds}** seconds.",
                                              color=0xbc2222)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title="On Cooldown",
                                              description=f"You can fish again in **{minutes}** minutes and **{seconds}** seconds.",
                                              color=0xbc2222)
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="On Cooldown", description="You can fish again in more than a day.",
                                          color=0xbc2222)
                    await ctx.send(embed=embed)
                return

        # Successful catch rates
        basic_fish_rate = 0.35
        golden_fish_rate = 0.02

        # Determine catch result
        catch_result = random.choices(
            ['Basic_Fish', 'Golden_Fish', 'Failed'],
            weights=[basic_fish_rate, golden_fish_rate, 1 - basic_fish_rate - golden_fish_rate],
            k=1
        )[0]

        embed = discord.Embed(title="Fishing Result")

        if catch_result != 'Failed':
            if catch_result in user_items:
                user_items[catch_result]['quantity'] += 1
            else:
                user_items[catch_result] = {'quantity': 1, 'price': 10}
            bait_durability -= 1

            if catch_result == 'Golden Fish':
                embed.add_field(name="You caught a :tropical_fish: Golden Fish!", value="Congratulations!",
                                inline=False)
            else:
                embed.add_field(name="You caught a :fish: Basic Fish!", value="Good job!", inline=False)
        else:
            embed.add_field(name="You didn't catch anything.", value=f"You can fish again in {cooldown_time}.",
                            inline=False)

        # Check if bait has run out
        if bait_durability <= 0:
            del user_items['Fishing_Bait']
            embed.add_field(name="Your Fishing Bait has run out!", value="Be sure to restock soon.", inline=False)
        else:
            bait_item['durability'] = bait_durability

        # Save last fishing time and updated inventory to file
        inventory[user_id]['last_fishing_time'] = datetime.now().isoformat()
        with open('inventory.json', 'w') as f:
            json.dump(inventory, f, indent=4)

        await ctx.send(embed=embed)

    @commands.command(aliases=['timebrman', 'timber', 'timberman', 'wood', 'tree', 'chop'])
    @commands.cooldown(1, 240, commands.BucketType.user)
    async def timebr_man(self, ctx):
        with open('inventory.json', 'r') as f:
            inventory = json.load(f)

        user_id = str(ctx.author.id)
        if user_id not in inventory:
            await ctx.send("You don't have an inventory yet. Use the `.shop` and `.daily` command to create one.")
            return

        user_items = inventory[user_id]['items']

        required_items = ["Basic_Axe"]

        for item in required_items:
            if item not in user_items or user_items[item]['quantity'] < 1:
                await ctx.send(f"You don't have a {item}.")
                return

        axe_durability = user_items[required_items[0]].get('durability', 25)
        if axe_durability <= 0:
            await ctx.send("Your axe is broken. You need to repair it with `.repair_axe`.")
            return
        else:
            user_items[required_items[0]]['durability'] = axe_durability - 1

        # Successful job rates
        wood_sticks_rate = 0.7
        golden_wood_rate = 0.1

        # Determine job result
        job_result = random.choices(
            ['Wood_Sticks', 'Golden_Wood', 'Failed'],
            weights=[wood_sticks_rate, golden_wood_rate, 1 - wood_sticks_rate - golden_wood_rate],
            k=1
        )[0]

        embed = discord.Embed(title="Timebrman Result")

        if job_result != 'Failed':
            if job_result in user_items:
                user_items[job_result]['quantity'] += 1
            else:
                user_items[job_result] = {'quantity': 1, 'price': 5 if job_result == 'Wood_Sticks' else 350}

            if job_result == 'Golden_Wood':
                embed.add_field(name="You collected a :wood: Golden Wood!", value="Congratulations!", inline=False)
            else:
                embed.add_field(name="You collected some :wood: Wood Sticks!", value="Good job!", inline=False)
        else:
            await ctx.send("You didn't collect anything.")
            return

        # Save updated inventory to file
        inventory[user_id]['items'] = user_items
        with open('inventory.json', 'w') as f:
            json.dump(inventory, f, indent=4)

        await ctx.send(embed=embed)

    @timebr_man.error
    async def timebr_man_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_seconds = round(error.retry_after, 2)
            minutes = cooldown_seconds // 60
            seconds = cooldown_seconds % 60
            message = f"You are on cooldown. Try again in {int(minutes)}m {int(seconds)}s."
            await ctx.send(embed=discord.Embed(title="Cooldown", description=message, color=discord.Color.red()))
        else:
            await self.bot.handle_error(ctx, error)

    @commands.command(aliases=['taxi', 'car', 'drive', 'driver'])
    async def start_driving(self, ctx):
        with open('inventory.json', 'r') as f:
            inventory = json.load(f)
        with open('money.json', 'r') as f:
            money_data = json.load(f)
        user_id = str(ctx.author.id)

        # Check if user has inventory, create one if not
        if user_id not in inventory:
            inventory[user_id] = {'items': {}, 'last_drive_time': ''}
            with open('inventory.json', 'w') as f:
                json.dump(inventory, f, indent=4)

        # Check if flat_tire key exists in user's inventory, set to 0 if it doesn't exist
        if 'flat_tire' not in inventory[user_id]:
            inventory[user_id]['flat_tire'] = 0

        # Check if the user has a flat tire
        flat_tire = bool(inventory[user_id].get('flat_tire', 0))
        if flat_tire:
            # Display message indicating flat tire and prompt user to fix it
            embed = discord.Embed(title="Flat Tire",
                                  description="Your tire is flat. Use `.fix_tire` to fix it for 50 money.",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            return

        # Check if the user has the required items
        required_items = ["Taxi_car", "Driver_license"]
        for item in required_items:
            if item not in inventory[user_id]['items'] or inventory[user_id]['items'][item]['quantity'] < 1:
                await ctx.send(f"You don't have a {item}.")
                return

        # Cooldown time for driving
        cooldown_time = timedelta(minutes=5)
        last_drive_time = datetime.now() - cooldown_time
        if 'last_drive_time' in inventory[user_id]:
            last_drive_time = datetime.fromisoformat(inventory[user_id]['last_drive_time'])
            if last_drive_time + cooldown_time > datetime.now():
                remaining_time = last_drive_time + cooldown_time - datetime.now()
                minutes, seconds = divmod(remaining_time.seconds, 60)
                if remaining_time.days == 0:
                    if minutes == 0:
                        embed = discord.Embed(title="On Cooldown",
                                              description=f"You can drive again in **{seconds}** seconds.",
                                              color=0xbc2222)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title="On Cooldown",
                                              description=f"You can drive again in **{minutes}** minutes and **{seconds}** seconds.",
                                              color=0xbc2222)
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="On Cooldown", description="You can drive again in more than a day.",
                                          color=0xbc2222)
                    await ctx.send(embed=embed)
                return

        # Update the last drive time
        inventory[user_id]['last_drive_time'] = datetime.now().isoformat()
        with open('inventory.json', 'w') as f:
            json.dump(inventory, f, indent=4)

        # Calculate earnings
        earnings = random.randint(10, 55)

        # Update user's money
        money_data[user_id] += earnings
        with open('money.json', 'w') as f:
            json.dump(money_data, f, indent=4)

        # Update last drive time
        inventory[user_id]['last_drive_time'] = datetime.now().isoformat()
        with open('inventory.json', 'w') as f:
            json.dump(inventory, f, indent=4)

        # Display earnings message
        embed = discord.Embed(title="Successful drive! <a:8103_monkaWheel:1089258532488101968> ",
                              description=f"You earned {earnings} money.",
                              color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(aliases=['fix_car', 'fix_wheel', 'fix'])
    async def fix_tire(self, ctx):
        with open('inventory.json') as f:
            data = json.load(f, )
        flat_tire = data[str(ctx.author.id)]['flat_tire']
        if flat_tire == 0:
            embed = discord.Embed(title="Cannot Fix Tire",
                                  description="You don't have a flat tire.",
                                  color=0xff0000)
        else:
            with open('money.json') as f:
                money_data = json.load(f)
            cost = 50
            if money_data[str(ctx.author.id)] < cost:
                embed = discord.Embed(title="Cannot Fix Tire",
                                      description=f"You don't have enough money to fix the flat tire. It costs {cost} credits.",
                                      color=0xff0000)
            else:
                money_data[str(ctx.author.id)] -= cost
                data[str(ctx.author.id)]['flat_tire'] = 0
                with open('money.json', 'w') as f:
                    json.dump(money_data, f, indent=4)
                with open('inventory.json', 'w') as f:
                    json.dump(data, f, indent=4)
                embed = discord.Embed(title="Tire Fixed",
                                      description=f"{ctx.author.mention} has fixed their flat tire for {cost} credits.",
                                      color=0x00ff00)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Jobs(bot))
    return None
