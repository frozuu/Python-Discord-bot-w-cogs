import discord
import requests
from discord.ext import commands
import numpy as np
import cv2
from urllib.request import urlopen
import os
from PIL import Image, ImageEnhance, UnidentifiedImageError
from io import BytesIO

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Fun cog loaded')

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        avatar_url = member.avatar.url
        embed = discord.Embed(title=f"{member.name}'s Avatar")
        embed.set_image(url=avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    async def deepfry(self, ctx, sharpness: int = 10000000, saturation: int = 5):
        """
        **Deepfrys an image.** \n
        Params: \n
        **optional** int `sharpness`: Sharpness of image. Turn up if you want your image more deepfried. \n
        **optional** int `saturation`: Sharpness of image. Turn up if you want your image more deepfried. \n
        Returns `discord.File`.
        """
        user = ctx.author
        avatar_url = user.avatar_url_as(static_format='png')

        try:
            response = requests.get(avatar_url)
            img = Image.open(BytesIO(response.content))
        except requests.exceptions.RequestException:
            raise Exception("Error fetching image from URL.")
        except UnidentifiedImageError:
            raise Exception("File is not an image.")

        img2 = ImageEnhance.Sharpness(img).enhance(sharpness)
        img3 = ImageEnhance.Color(img2).enhance(saturation)

        with BytesIO() as image_binary:
            img3.save(image_binary, 'PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='deepfry.png')

        await ctx.send(file=file)


async def setup(bot):
    await bot.add_cog(Fun(bot))
    return None
