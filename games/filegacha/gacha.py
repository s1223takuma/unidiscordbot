import random
import discord
path = "games/filegacha/filelist/"
async def filegacha(ctx):
    files = ["A.py","B.py","C.py"]
    selected_file = random.choice(files)
    await ctx.send(file=discord.File(path + selected_file))