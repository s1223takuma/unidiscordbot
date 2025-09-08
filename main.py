import discord
from discord.utils import get
from os import getenv
from pdf2image import convert_from_path
import os
from math import ceil

import tkn
from bot_setup import intents, client,invite
from mycommands import category_manager as cc, help as hc, create_url as cu ,contact as ct, observe_manager as ob, search as sr,voice as vc
from games.jinro.setup import setup as jinro_setup
from automation import pdf_handler, observe as observemessage
from Voicebot.voicebot import speak_text, read_channels



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
        print(f"{member} が {after.channel} に参加しました")
        print(after.channel.id)
        await vc.auto_join(after.channel)
    elif before.channel is not None and after.channel is None:
        if member.bot:
            return
        if len(before.channel.members) == 1:
            print(f"{member} が {before.channel} から退出しました")
            await vc.auto_leave(before.channel)



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
async def set_speaker(ctx, speaker_id: int = None):
    await vc.set_speaker(ctx, speaker_id=speaker_id)

@client.command(name="speakers")
async def list_speakers(ctx):
    await vc.list_speakers(ctx)

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