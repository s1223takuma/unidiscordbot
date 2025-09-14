import discord
from os import getenv
import asyncio
from collections import deque

from bot_setup import client
from mycommands import category_manager as cc, help as hc, create_url as cu ,contact as ct, observe_manager as ob, search as sr,voice as vc,randomnum as rm
from games.jinro.setup import setup as jinro_setup
from automation import pdf_handler, observe as observemessage
from Voicebot.voicebot import speak_text, read_channels,set_speaker,list_speakers,admin_set_speaker,check_speaker,random_speaker
from Voicebot.clean_text import add_word

TOKEN = getenv('Discord_TOKEN')

message_queue = deque()
is_speaking = False

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
    
    message_queue.append((message, message.content, message.author.id))
    
    await process_queue()

async def process_queue():
    global is_speaking
    
    if is_speaking or not message_queue:
        return
        
    is_speaking = True
    
    while message_queue:
        message, content, author_id = message_queue.popleft()
        await speak_text(message, content, author_id)
    is_speaking = False

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        try:
            await vc.auto_join(after.channel)
            if member.bot:
                return
            await speak_text(after.channel, f"{member.display_name}さんこんにちは。私は読み上げbotです。よろしくお願いします。",0)
        except discord.errors.ConnectionClosed as e:
            print("⚠️ ボイス接続が切断されました。再試行します…")
            await asyncio.sleep(5)
            try:
                await vc.auto_join(after.channel)
            except Exception as e:
                print(f"再接続に失敗: {e}")
    elif before.channel is not None and after.channel is None:
        if len(before.channel.members) == 1:
            await vc.auto_leave(before.channel)
            return
        if not member.bot:
            await speak_text(before.channel, f"{member.display_name}さん楽しかったよ。またね",0)
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

@client.command(name="random",aliases=['rand'])
async def randomnum(ctx,min:int,max:int):
    await rm.randomnum(ctx,min=min,max=max)

@client.command(name="speaker",aliases=['sp'])
async def speaker(ctx, speaker_id: int = None):
    await set_speaker(ctx, speaker_id=speaker_id)

@client.command(name="adminspeaker",aliases=['asp'])
async def speaker(ctx, member_id,speaker_id: int = None):
    await admin_set_speaker(ctx,member_id=member_id,speaker_id=speaker_id)

@client.command(name="checkspeaker",aliases=['csp'])
async def checkspeaker(ctx):
    await check_speaker(ctx)

@client.command(name="speakers")
async def speakers(ctx):
    await list_speakers(ctx)

@client.command(name="randomspeaker",aliases=['rsp'])
async def randomspeaker(ctx):
    await random_speaker(ctx)

@client.command(name="addword",aleiases=['aw'])
async def addword(ctx,word,kana):
    await add_word(ctx,word=word,kana=kana)

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