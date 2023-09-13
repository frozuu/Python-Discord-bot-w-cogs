import os
import json
import discord
from discord.ext import commands
import asyncio
import time


class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Load money from money.json
        with open("money.json", "r") as f:
            self.money = json.load(f)

        # Load inventory from inventory.json
        with open("inventory.json", "r") as f:
            self.inventory = json.load(f)

        # Define the products available in the shop
        self.products = {
            1: {"name": "Basic_Fishing_Rod", "description": "A simple fishing rod for catching fish", "price": 100},
            2: {"name": "Fishing_Bait", "description": "A pack of fishing bait to attract fish", "price": 50},
            3: {"name": "Basic_Axe", "description": "A basic axe for chopping wood", "price": 300},
            4: {"name": "Taxi_car", "description": "A reliable taxi car for transporting passengers", "price": 800},
            5: {"name": "Driver_license", "description": "A license to legally operate a taxi car", "price": 1000}
        }

    async def buy_product(self, user_id, product):
        with open("money.json", "r") as f:
            money = json.load(f)

        @commands.Cog.listener()
        async def on_ready(self):
            print('Shop cog loaded')

        # Check if the user has enough money to make the purchase
        credits = money.get(str(user_id), 0)
        if credits < product['price']:
            return "You do not have enough money to buy this product."

        # Subtract the cost from their money balance
        money[str(user_id)] = credits - product['price']

        # Add the product to the user's inventory
        with open("inventory.json", "r") as f:
            inventory = json.load(f)

        if str(user_id) in inventory:
            # If the user already has an inventory, add the product to it
            if product['name'] in inventory[str(user_id)]["items"]:
                inventory[str(user_id)]["items"][product['name']]["quantity"] += 1
            else:
                inventory[str(user_id)]["items"][product['name']] = {"quantity": 1, "price": product['price']}
            inventory[str(user_id)]["credits"] -= product['price']
        else:
            # If the user doesn't have an inventory, create one for them
            inventory[str(user_id)] = {"items": {product['name']: {"quantity": 1, "price": product['price']}},
                                       "credits": -product['price']}

        # Save the updated inventory and money balance to JSON files
        with open("inventory.json", "w") as f:
            json.dump(inventory, f, indent=4)
        with open("money.json", "w") as f:
            json.dump(money, f)

        return "Product purchased successfully."

    @commands.command(name="shop", aliases=["buy", 'store'])
    async def shop(self, ctx):
        with open("money.json", "r") as f:
            money = json.load(f)

        embed = discord.Embed(title="Shop", description="React with the corresponding number to purchase an item")
        for product_id, product in self.products.items():
            embed.add_field(
                name=f"{product_id}. {product['name'].replace('_', ' ')}",
                value=f"{product['description']} - {product['price']} ¥",
                inline=False,
            )

        message = await ctx.send(embed=embed)

        for product_id in self.products.keys():
            await message.add_reaction(f"{product_id}\N{COMBINING ENCLOSING KEYCAP}")

        user_id = str(ctx.author.id)
        items_to_purchase = {}
        with open("money.json", "r") as f:
            money = json.load(f)

        def check(reaction, user):
            return (
                    user == ctx.author
                    and str(reaction.emoji) in [f"{product_id}\N{COMBINING ENCLOSING KEYCAP}" for product_id in
                                                self.products.keys()]
                    and reaction.message.id == message.id
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=300.0, check=check)
            except asyncio.TimeoutError:
                break

            with open("money.json", "r") as f:
                money = json.load(f)
            credits = money.get(str(user.id), 0)
            product = self.products[int(reaction.emoji[0])]

            if credits < product["price"]:
                await ctx.send(
                    f"{ctx.author.mention} You do not have enough money to buy {product['name'].replace('_', ' ')}.")

                continue

            # Subtract the cost of the product from the user's money balance
            money[str(user.id)] = credits - product['price']
            with open("money.json", "w") as f:
                json.dump(money, f, indent=4)

            # Add the product to the user's inventory
            if str(user.id) in self.inventory:
                if product['name'] in self.inventory[str(user.id)]["items"]:
                    self.inventory[str(user.id)]["items"][product['name']]["quantity"] += 1
                else:
                    self.inventory[str(user.id)]["items"][product['name']] = {"quantity": 1, "price": product['price']}
                self.inventory[str(user.id)]["credits"] -= product['price']
            else:
                self.inventory[str(user.id)] = {"items": {product['name']: {"quantity": 1, "price": product['price']}},
                                                "credits": -product['price']}

            with open("inventory.json", "w") as f:
                json.dump(self.inventory, f, indent=4)

            await ctx.send(
                f"{ctx.author.mention} purchased {product['name'].replace('_', ' ')} for {product['price']} ¥")


async def setup(bot):
    await bot.add_cog(ShopCog(bot))
    return None
