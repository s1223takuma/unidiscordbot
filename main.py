import discord
from discord.utils import get
from os import getenv
from pdf2image import convert_from_path
import os
from math import ceil
import asyncio

import tkn
from bot_setup import intents, client,invite
from mycommands import category_manager as cc, help as hc, create_url as cu ,contact as ct, observe_manager as ob, search as sr,voice as vc
from games.jinro.setup import setup as jinro_setup
from automation import pdf_handler, observe as observemessage
from Voicebot.voicebot import speak_text, read_channels,set_speaker,list_speakers

TOKEN = getenv('Discord_TOKEN')

@client.event
async def on_message(message):
    await observemessage.send_observe_message(message)
    if message.author.bot:
        return
    await client.process_commands(message)
    await pdf_handler.open_pdf(message)
    if message.author.bot:
            return
            
    guild_id = message.guild.id if message.guild else None
    
    if guild_id not in read_channels:
        return
        
    if message.channel.id != read_channels[guild_id]:
        return
        
    if message.content.startswith('!'):
        return
    await speak_text(message, message.content, message.author.id)

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        try:
            await vc.auto_join(after.channel)
        except discord.errors.ConnectionClosed as e:
            print("⚠️ ボイス接続が切断されました。再試行します…")
            await asyncio.sleep(5)
            try:
                await vc.auto_join(after.channel)
            except Exception as e:
                print(f"再接続に失敗: {e}")
    elif before.channel is not None and after.channel is None:
        if member.bot:
            return
        if len(before.channel.members) == 1:
            await vc.auto_leave(before.channel)
    elif before.channel != after.channel:
        if member.bot:
            return
        if len(before.channel.members) == 1:
            await vc.auto_leave(before.channel)
            await vc.auto_join(after.channel)



@client.command()
async def search(ctx, *, query: str):
    await sr.search(ctx, query=query)

@client.command()
async def searchnews(ctx, *, query: str):
    await sr.searchnews(ctx, query=query)

@client.command()
async def searchimage(ctx, *, query: str):
    await sr.searchimage(ctx, query=query)

@client.command(name="speaker",aliases=['sp'])
async def speaker(ctx, speaker_id: int = None):
    await set_speaker(ctx, speaker_id=speaker_id)

@client.command(name="speakers")
async def speakers(ctx):
    await list_speakers(ctx)

@client.command(name="join")
async def join(ctx):
    await vc.join(ctx)

@client.command(name="leave")
async def leave(ctx):
    await vc.leave(ctx)

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