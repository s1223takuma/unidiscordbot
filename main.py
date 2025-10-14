import discord
from os import getenv
import asyncio
from collections import deque

from bot_setup import client,tree
from games.mystery.setup import setup as mystery_setup
import tkn
from mycommands import category_manager as cc, help as hc, create_url as cu ,contact as ct, observe_manager as ob, search as sr,voice as vc,randomnum as rm, delete_category as dc,mention as mt,create_dashboard as cd
from games.jinro.setup import setup as jinro_setup
from games.jinro.status import gamestatus as jinro_status
import games.filegacha.gacha as gc
from games.mystery.status import gamestatus as mystery_status
from automation import pdf_handler, observe as observemessage
from Voicebot.voicebot import speak_text, read_channels,set_speaker,speakers_list,admin_set_speaker,check_speaker,random_speaker
from Voicebot.clean_text import add_word,add_words

TOKEN = getenv('Discord_TOKEN')

message_queue = deque()
is_speaking = False

@client.event
async def on_message(message):
    await pdf_handler.open_pdf(message)
    await observemessage.send_observe_message(message)
    if message.author.bot:
        return
    await client.process_commands(message)
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
            if not member.bot:
                await speak_text(after.channel, f"{member.display_name}さんこんにちは。私は読み上げbotです。", 0)
        except discord.errors.ConnectionClosed:
            print("⚠️ ボイス接続が切断されました。再試行します…")
            await asyncio.sleep(5)
            try:
                await vc.auto_join(after.channel)
            except Exception as e:
                print(f"再接続に失敗: {e}")
    elif before.channel is not None and after.channel is None:
        if before.channel and len(before.channel.members) == 1:
            await vc.auto_leave(before.channel)
        elif not member.bot:
            await speak_text(before.channel, f"{member.display_name}さんが退出しました", 0)
    elif before.channel != after.channel:
        if not member.bot:
            world_category = mystery_status.get(member.guild.id, {}).get("world_category")
            wolf_category = jinro_status.get(member.guild.id,{}).get("category")
            if before.channel and len(before.channel.members) == 1 and after.channel not in world_category.channels and after.channel not in wolf_category.channels:
                await vc.auto_leave(before.channel)
                await vc.auto_join(after.channel)

@tree.command(name="search", description="検索を行います")
async def search_slash(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await sr.search(ctx, query=query)

@tree.command(name="searchnews", description="ニュース検索を行います")
async def searchnews_slash(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await sr.searchnews(ctx, query=query)

@tree.command(name="searchimage", description="画像検索を行います")
async def searchimage_slash(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await sr.searchimage(ctx, query=query)

@tree.command(name="random", description="ランダムな数値を生成します")
async def random_slash(interaction: discord.Interaction, min: int, max: int):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await rm.randomnum(ctx, min=min, max=max)

@tree.command(name="speaker", description="話者を設定します")
async def speaker_slash(interaction: discord.Interaction, speaker_id: int = None):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await set_speaker(ctx, speaker_id=speaker_id)

@tree.command(name="adminspeaker", description="他のユーザーの話者を設定します")
async def adminspeaker_slash(interaction: discord.Interaction, member: discord.Member, speaker_id: int = None):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await admin_set_speaker(ctx, member_id=member.id, speaker_id=speaker_id)

@tree.command(name="filegacha", description="ファイルガチャを実行します")
async def filegacha_slash(interaction: discord.Interaction):
    if interaction.guild.id not in tkn.miuchi_ID:
        await interaction.response.send_message("このコマンドは特定のサーバーでのみ使用できます。", ephemeral=True)
        return
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await gc.filegacha(ctx)

@tree.command(name="checkspeaker", description="現在の話者を確認します")
async def checkspeaker_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await check_speaker(ctx)

@tree.command(name="speakers", description="利用可能な話者一覧を表示します")
async def speakers_slash(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    ctx = await client.get_context(interaction)
    await speakers_list(ctx)

@tree.command(name="randomspeaker", description="ランダムな話者を設定します")
async def randomspeaker_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await random_speaker(ctx)

@tree.command(name="addword", description="単語を辞書に追加します")
async def addword_slash(interaction: discord.Interaction, word: str, kana: str):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await add_word(ctx, word=word, kana=kana)

@tree.command(name="addwords", description="複数の単語を辞書に追加します")
async def addwords_slash(interaction: discord.Interaction, kana: str, words: str):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    words_list = words.split()
    await add_words(ctx, kana, words_list)

@tree.command(name="join", description="ボイスチャンネルに参加します")
async def join_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await vc.join(ctx)

@tree.command(name="leave", description="ボイスチャンネルから退出します")
async def leave_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await vc.leave(ctx)

@tree.command(name="監視", description="メッセージを監視します")
async def observe_slash(interaction: discord.Interaction, mode: str = "server"):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await ob.observe(ctx, mode=mode)

@tree.command(name="カテゴリ作成", description="カテゴリを作成します")
async def create_category_slash(interaction: discord.Interaction, content: str):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await cc.create_category(ctx, content=content)

@tree.command(name="url", description="URLを取得します")
async def geturl_slash(interaction: discord.Interaction, day: int = 1):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await cu.geturl(ctx, day=day)

@tree.command(name="お問い合わせ", description="お問い合わせを送信します")
async def contact_slash(interaction: discord.Interaction, content: str):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await ct.contact(ctx, inquiry=content)

@tree.command(name="help", description="ヘルプを表示します")
async def help_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await hc.help(ctx)

@tree.command(name="人狼", description="人狼ゲームをセットアップします")
async def jinro_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await jinro_setup(ctx)

@tree.command(name="ミステリー", description="ミステリーゲームをセットアップします")
async def mystery_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await mystery_setup(ctx)

@tree.command(name="mention",description="特定の人をメンションします。")
async def mention_slash(interaction: discord.Interaction,cnt: int, member: discord.Member):
    await interaction.response.defer()
    await interaction.edit_original_response(content="メンションを送信します。")
    await mt.mention_slash(interaction,cnt,member)

@tree.command(name="clean", description="ゲームデータをクリーンアップします")
async def clean_slash(interaction: discord.Interaction):
    if interaction.user.id not in tkn.developer_id:
        await interaction.response.send_message("あなたはこのコマンドを実行できません。", ephemeral=True)
        return
    await interaction.response.defer()
    from games.mystery.status import gamestatus
    from games.mystery.cleanup import cleanup_category, cleanup_channels
    ctx = await client.get_context(interaction)
    await cleanup_category(ctx)
    await cleanup_channels(ctx)
    del gamestatus[ctx.guild.id]

@tree.command(name="pdf-dashboard", description="ダッシュボードを作成します")
async def dashboard_slash(interaction: discord.Interaction):
    if interaction.user.id not in tkn.developer_id:
        await interaction.response.send_message("あなたはこのコマンドを実行できません。", ephemeral=True)
        return
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await cd.dashboard(ctx)

@tree.command(name="カテゴリ削除", description="カテゴリーとチャンネルを削除します")
async def clean_category(interaction: discord.Interaction, name: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "管理者権限を持っていないため、このコマンドは実行できません。",
            ephemeral=True
        )
        return
    await interaction.response.defer()
    ctx = await client.get_context(interaction)
    await dc.delete_category(ctx,name=name)


@tree.command(name="sync", description="コマンドを同期します。")
async def sync_command(interaction: discord.Interaction):
    guild = interaction.guild
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "管理者権限を持っていないため、このコマンドは実行できません。", 
            ephemeral=True
        )
        return
    tree.clear_commands(guild=guild)
    await tree.sync(guild=guild)
    await interaction.response.send_message("コマンドを同期しました。", ephemeral=True)


client.run(TOKEN)