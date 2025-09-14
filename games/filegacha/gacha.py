import random
import discord
import os
path = "games/filegacha/files/"
async def filegacha(ctx):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    selected_file = random.choice(files)
    await ctx.send(file=discord.File(path + selected_file))