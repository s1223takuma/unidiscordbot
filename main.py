import discord
from discord.ui import View, Button
from discord.ext import commands
from discord.utils import get
from os import getenv
import tkn
from pdf2image import convert_from_path
import os
from math import ceil
from mycommands import help as hc, create_url as cu ,contact as ct, manage_category as cc ,observe_manager as ob
from games.jinro.setup import setup as jinro_setup
from bot_setup import intents, client,invite

TOKEN = getenv('Discord_TOKEN')

# 接続に必要なオブジェクトを生成





# 起動時に動作する処理
@client.event
async def on_ready():
    print('ログインしました')
    await client.tree.sync()

@client.event
async def on_command_error(ctx, error):
    await ctx.send(f"エラーが発生しました: {error}")

@client.event
async def on_message(message):
    user = client.get_user(tkn.admin_id)
    if not message.author.bot:
        if message.guild and (message.guild.id in ob.observe_guild or message.channel.id in ob.observe_guild):
            if not message.content.startswith("!"):
                await user.send(
                    f"「{message.guild.name}」で{message.author.mention}が発言:{message.content}"
                )
    if message.author.id == 1083313772258676786:
        return
    await client.process_commands(message)
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith(".pdf"):
                file_path = f"./{attachment.filename}"
                await attachment.save(file_path)
                images = convert_from_path(file_path)
                paths = []
                for i, img in enumerate(images):
                    img_path = f"page_{i+1}.png"
                    img.save(img_path, "PNG")
                    paths.append(img_path)
                chunk_size = 10
                total_chunks = ceil(len(paths) / chunk_size)
                if message.content == "":
                    await message.channel.send(f"# {attachment.filename}")
                else:
                    await message.channel.send(f"# {message.content}")
                for chunk_index in range(total_chunks):
                    chunk_paths = paths[chunk_index*chunk_size : (chunk_index+1)*chunk_size]
                    files = [discord.File(p) for p in chunk_paths]
                    await message.channel.send(
                        content=f"{chunk_index*chunk_size+1}p ~ {chunk_index*chunk_size+len(files)}p",
                        files=files
                    )
                for path in paths:
                    os.remove(path)
                os.remove(file_path)




# @client.command(name="join")
# async def join(ctx):
#     if ctx.author.voice is None:
#         await ctx.reply("ボイスチャンネルに参加してからコマンドを実行してください。")
#         return
#     voice_channel = ctx.author.voice.channel
#     if ctx.voice_client is None:
#         await voice_channel.connect()
#         await ctx.reply(f"{voice_channel.name}に参加しました。")
#     else:
#         await ctx.voice_client.move_to(voice_channel)
#         await ctx.reply(f"{voice_channel.name}に移動しました。")


# @client.command(name="leave")
# async def leave(ctx):
#     if ctx.voice_client is None:
#         await ctx.reply("ボイスチャンネルに参加していません。")
#     else:
#         await ctx.voice_client.disconnect()
#         await ctx.reply("ボイスチャンネルから退出しました。")



@client.command(name="監視")
async def observe(ctx, mode="server"):
    await ob.observe(ctx, mode=mode)

@client.command(name="カテゴリ作成")
async def create_category(ctx, *, content):
    await cc.create_category(ctx, content=content)

@client.command(name='url')
async def geturl(ctx,day=1):
    await cu.geturl(ctx, day=day)

@client.command(name="お問い合わせ")
async def contact(ctx,*,inquiry):
    await ct.contact(ctx, inquiry=inquiry)

@client.command(name="h")
async def help_command(ctx):
    await hc.help(ctx)

@client.command(name="人狼")
async def setup(ctx):
    await jinro_setup(ctx)


client.run(TOKEN)