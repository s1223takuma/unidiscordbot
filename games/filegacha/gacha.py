import random
import discord
path = "games/filegacha/files/"
async def filegacha(ctx):
    files = ["a.py","b.php","c.swift"]
    selected_file = random.choice(files)
    await ctx.send(file=discord.File(path + selected_file))