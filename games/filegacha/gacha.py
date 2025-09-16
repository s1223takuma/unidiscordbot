import random
import discord
import os
path = "games/filegacha/files/"
async def filegacha(ctx):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    selected_file = random.choice(files)
    await ctx.send(f"おめでとう{selected_file[0]}ランクが当たりました\nダウンロードして実行してみよう！\n足りないモジュールがあったら``pip install モジュール名``でインストールしよう！",file=discord.File(path + selected_file))