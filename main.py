import discord
from discord.utils import get
from os import getenv
from pdf2image import convert_from_path
import os
from math import ceil

import tkn
from bot_setup import intents, client,invite
from mycommands import category_manager as cc, help as hc, create_url as cu ,contact as ct, observe_manager as ob, search as sr
from games.jinro.setup import setup as jinro_setup
from automation import pdf_handler, observe as observemessage


TOKEN = getenv('Discord_TOKEN')

@client.event
async def on_message(message):
    await observemessage.send_observe_message(message, admin_id=tkn.admin_id)
    if message.author.bot:
        return
    await client.process_commands(message)
    await pdf_handler.open_pdf(message)


@client.command()
async def search(ctx, *, query: str):
    await sr.search(ctx, query=query)

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