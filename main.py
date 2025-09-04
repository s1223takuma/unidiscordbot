import discord
from discord.utils import get
from os import getenv
import tkn
from pdf2image import convert_from_path
import os
from math import ceil

from bot_setup import intents, client,invite
from mycommands import help as hc, create_url as cu ,contact as ct, manage_category as cc ,observe_manager as ob
from games.jinro.setup import setup as jinro_setup
from automation import pdf_handler

TOKEN = getenv('Discord_TOKEN')

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
    await pdf_handler.open_pdf(message)




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