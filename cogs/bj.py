import discord
from discord.ext import commands
import json
import random
from discord import Embed
import typing

class Deck:
    def __init__(self):
        self.cards = []
        for rank in range(1, 14):
            for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
                self.cards.append((rank, suit))



    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()




def get_hand_value(hand):
    value = 0
    num_aces = 0
    for rank, suit in hand:
        if rank == 1:
            num_aces += 1
            value += 11
        elif rank >= 10:
            value += 10
        else:
            value += rank
    while num_aces > 0 and value > 21:
        value -= 10
        num_aces -= 1
    return value


async def get_hit_or_stand_reaction(ctx):
    hit_emoji = "👊"
    stand_emoji = "🛑"
    reactions = [hit_emoji, stand_emoji]
    for reaction in reactions:
        await ctx.message.add_reaction(reaction)

    def check(reaction, user):
        return reaction.message.id == ctx.message.id and user == ctx.author and str(reaction.emoji) in reactions

    reaction, _ = await ctx.bot.wait_for('reaction_add', check=check)
    return str(reaction.emoji)


class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Blackjack cog loaded')

    async def get_money(self, user_id):
        with open('money.json', 'r') as f:
            money = json.load(f)
        return money.get(str(user_id), 0)

    async def update_money(self, user_id, amount):
        with open('money.json', 'r') as f:
            money = json.load(f)
        money[str(user_id)] = money.get(str(user_id), 0) + amount
        with open('money.json', 'w') as f:
            json.dump(money, f)

    @commands.command()
    async def bj(self, ctx, bet: typing.Optional[int] = None):
        """
        Play blackjack with the given bet amount.
        """
        money = await self.get_money(ctx.author.id)
        if bet is None:
            embed = discord.Embed(title="Blackjack", description="Please specify a bet amount.",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        elif bet > money:
            embed = discord.Embed(title="Blackjack", description="You don't have enough money.",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        deck = Deck()
        deck.shuffle()
        player_hand = [deck.draw(), deck.draw()]
        dealer_hand = [deck.draw(), deck.draw()]

        # Player's turn
        while True:
            player_total = get_hand_value(player_hand)
            if player_total > 21:
                embed = discord.Embed(title="Blackjack", description="Bust! You lose.", color=discord.Color.red())
                await ctx.send(embed=embed)
                await self.update_money(ctx.author.id, -bet)
                return
            embed = discord.Embed(title="Blackjack", description=f"Your hand: {player_hand} ({player_total})",
                                  color=discord.Color.gold())
            message = await ctx.send(embed=embed)
            reaction = await get_hit_or_stand_reaction(ctx)
            if reaction == "👊":
                player_hand.append(deck.draw())
            else:
                break
            await message.delete()

        # Dealer's turn
        while True:
            dealer_total = get_hand_value(dealer_hand)
            if dealer_total > 21:
                embed = discord.Embed(title="Blackjack", description="Dealer busts! You win!",
                                      color=discord.Color.green())
                await ctx.send(embed=embed)
                await self.update_money(ctx.author.id, bet)
                return
            elif dealer_total >= 17:
                break
            else:
                dealer_hand.append(deck.draw())

        # Determine the winner
        player_total = get_hand_value(player_hand)
        dealer_total = get_hand_value(dealer_hand)
        if player_total > dealer_total:
            embed = discord.Embed(title="Blackjack", color=discord.Color.green())
            embed.add_field(name="Result", value=f"You win!")
            embed.add_field(name="Your hand", value=f"{player_hand} ({player_total})", inline=False)
            embed.add_field(name="Dealer's hand", value=f"{dealer_hand} ({dealer_total})", inline=False)
            await ctx.send(embed=embed)
            await self.update_money(ctx.author.id, bet)
        elif player_total < dealer_total:
            embed = discord.Embed(title="Blackjack", color=discord.Color.red())
            embed.add_field(name="Result", value=f"You lose.")
            embed.add_field(name="Your hand", value=f"{player_hand} ({player_total})", inline=False)
            embed.add_field(name="Dealer's hand", value=f"{dealer_hand} ({dealer_total})", inline=False)
            await ctx.send(embed=embed)
            await self.update_money(ctx.author.id, -bet)
        else:
            embed = discord.Embed(title="Blackjack", color=discord.Color.gold())
            embed.add_field(name="Result", value=f"It's a tie.")
            embed.add_field(name="Your hand", value=f"{player_hand} ({player_total})", inline=False)
            embed.add_field(name="Dealer's hand", value=f"{dealer_hand} ({dealer_total})", inline=False)
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Blackjack(bot))
    return None
