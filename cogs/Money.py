from discord.ext import commands
import discord
import json
import datetime
import asyncio

class Money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_money_data()
        super().__init__()

    def load_money_data(self):
        try:
            with open("money.json", "r") as f:
                self.money_data = json.load(f)
        except FileNotFoundError:
            self.money_data = {}

    def save_money_data(self):
        with open("money.json", "w") as f:
            json.dump(self.money_data, f)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Money cog loaded')

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """Gives you 100 money every 24 hours"""
        user_id = str(ctx.author.id)
        if user_id not in self.money_data:
            self.money_data[user_id] = 0
        last_claimed = self.money_data[user_id]
        now = datetime.datetime.now().timestamp()
        if last_claimed + 86400 > now:
            remaining_time = last_claimed + 86400 - now
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(
                f"{ctx.author.mention}, you can claim your daily reward again in {int(hours)}h {int(minutes)}m {int(seconds)}s.")
        else:
            self.money_data[user_id] += 150
            self.save_money_data()
            await ctx.send(embed=discord.Embed(
                description=f"💰 {ctx.author.mention}, you have claimed your daily reward of **150 ¥**! Your new balance is **{self.money_data[user_id]} ¥**."))

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            hours, remainder = divmod(error.retry_after, 3600)
            minutes, seconds = divmod(remainder, 60)
            embed = discord.Embed(
                title=":clock10: Command on Cooldown",
                description=f"{ctx.author.mention}, you are on cooldown. Try again in **{int(hours)}h {int(minutes)}m {int(seconds)}s.**",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(aliases=['bal'])
    async def balance(self, ctx):
        user_id = str(ctx.author.id)

        self.load_money_data()  # Load the current money data from money.json
        if user_id not in self.money_data:
            self.money_data[user_id] = 0

        balance = self.money_data[user_id]
        formatted_balance = '{:,.0f}'.format(balance)  # format balance with commas

        embed = discord.Embed(
            title="Your Balance",
            description=f"{ctx.author.mention}, your current balance is **{formatted_balance} ¥** 💰.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['inventory'])
    async def inv(self, ctx, member: discord.Member = None):
        """Displays the inventory of the specified user or the author if no member is specified"""
        if not member:
            member = ctx.author

        with open("inventory.json", "r") as f:
            inventory_data = json.load(f)

        if str(member.id) not in inventory_data:
            inventory_data[str(member.id)] = {}

        inventory = inventory_data[str(member.id)]

        items_list = []
        for item, item_data in inventory.get("items", {}).items():
            quantity = item_data.get("quantity", 0)
            if quantity > 0:
                item_name = item.replace("_", " ")  # replace underscores with spaces in item name
                items_list.append((item_name, quantity))

        if items_list:
            embed = discord.Embed(
                title=f"{member.name}'s Inventory",
                color=discord.Color.green()
            )

            for item_name, quantity in items_list:
                embed.add_field(name=item_name, value=f"Quantity {quantity}", inline=True)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{member.name} has no items in their inventory.")

    @commands.command()
    async def sell(self, ctx, items: str = None, quantity: int = None):
        """Sell a certain quantity of an item from the inventory"""
        if not items or not quantity:
            embed = discord.Embed(
                title="Incorrect Usage",
                description=f"Please use `.sell <item_name> <quantity>` to sell items.\nExample: `.sell Basic_Fish 5`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        with open("inventory.json", "r") as f:
            inventory_data = json.load(f)

        if str(ctx.author.id) not in inventory_data:
            inventory_data[str(ctx.author.id)] = {}

        inventory = inventory_data[str(ctx.author.id)]

        if "items" not in inventory:
            embed = discord.Embed(
                title="Error",
                description=f"{ctx.author.mention} has no items in their inventory.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if items not in inventory["items"]:
            embed = discord.Embed(
                title="Error",
                description=f"{ctx.author.mention} does not have `{items.replace('_', ' ')}` in their inventory.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        item_data = inventory["items"][items]
        item_quantity = item_data.get("quantity", 0)
        if item_quantity < quantity:
            embed = discord.Embed(
                title="Error",
                description=f"{ctx.author.mention} does not have enough `{items.replace('_', ' ')}` to sell.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        item_price = item_data.get("price", 0)
        total_price = item_price * quantity * 0.5
        inventory["credits"] = inventory.get("credits", 0) + total_price
        item_data["quantity"] = item_quantity - quantity

        # Update the money balance in money.json
        with open("money.json", "r") as f:
            money_data = json.load(f)

        if str(ctx.author.id) not in money_data:
            money_data[str(ctx.author.id)] = 0

        money_data[str(ctx.author.id)] += total_price

        with open("money.json", "w") as f:
            json.dump(money_data, f, indent=4)

        with open("inventory.json", "w") as f:
            json.dump(inventory_data, f, indent=4)

        items = items.replace("_", " ")
        embed = discord.Embed(
            title="Sell Successful!",
            description=f"{ctx.author.mention} sold **{quantity}** `{items}`(s) for **{total_price}** ¥.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)




async def setup(bot):
    await bot.add_cog(Money(bot))
    return None
