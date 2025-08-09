import discord
import traceback
from discord.ext import commands,tasks
from discord.utils import get
from os import getenv
from datetime import time,datetime
import pytz
import requests
import tkn
import asyncio
import random

# 接続に必要なオブジェクトを生成
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents)
invite = None


# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')




@client.event
async def on_message(message):
    print(message.content)
    if message.author.id == 1083313772258676786:
        return
    await client.process_commands(message)
    # alert_role = discord.utils.get(message.guild.roles, name="ちゅうがくせい")
    # post_time = message.created_at
    # jst = pytz.timezone('Asia/Tokyo')
    # post_time_jst = post_time.astimezone(jst)
    # str_time = int(post_time_jst.strftime("%H%M"))
    # if str_time <= 800 or str_time >= 2200:
    #     if alert_role in message.author.roles:
    #         if message.author.guild.name == 'botお試し':
    #             embed = discord.Embed(title="中学生の発言検知", description=f'{message.content}\n該当メッセージリンク {message.jump_url}')
    #             adminchannel = client.get_channel(1194279786357465239)
    #             await adminchannel.send(embed=embed)
    #             embed = discord.Embed(title="あなたの発言が検知されました")
    #             await message.author.send(embed=embed)
    #             print(str_time)
    #             print('けんち')
    # else:
    #     print(str_time)


@client.command(name="カテゴリ作成")
async def create_category(ctx, *, content):
    category = await ctx.guild.create_category(content)

    text_channels = [f'{content}{category_type}' for category_type in ["雑談", "募集", "解説動画、情報"]]
    voice_channels = [f'{content}VC{vc_number}' for vc_number in range(1, 3)]

    for channel_name in text_channels:
        await category.create_text_channel(channel_name)

    # Add 聞き専チャットvc1 and 聞き専チャットvc2
    await category.create_text_channel(f'聞き専チャットvc1')
    await category.create_text_channel(f'聞き専チャットvc2')

    for channel_name in voice_channels:
        await category.create_voice_channel(channel_name, user_limit=99)

    await ctx.reply(f'「{content}」のカテゴリーとチャンネルが作成されました。')


@client.command(name='url')
async def geturl(ctx,day=1):

    if day >= 30:
        await ctx.send('30日を超える招待URLは発行できません')
        return
    channels = client.get_channel(ctx.channel.id)
    invite = await channels.create_invite(max_age = int(day) * 24 * 3600)
    print(invite.url)
    await ctx.reply(f'招待URLを発行しました。\n{invite.url}\n有効期限は{day}日です。')



@client.command(name="お問い合わせ")
async def contact(ctx,*,inquiry):
    print(inquiry)
    managementrole = discord.utils.get(ctx.guild.roles, name='officers (example)')
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
        managementrole: discord.PermissionOverwrite(read_messages=True),
    }
    channel = await ctx.guild.create_text_channel(f'お問い合わせ- {ctx.author.name}', overwrites=overwrites)

    embed = discord.Embed(title="新規お問い合わせ", description=inquiry)
    await channel.send(embed=embed)
    await channel.send(f"こんにちは！\n{ctx.author.mention}さんのお問い合わせを受け付けました。{managementrole.mention}よりご連絡いたします。")

gamestatus = {}
@client.command(name="人狼スタート")
async def setup(ctx):
    if ctx.guild.id in gamestatus:
        await ctx.send("すでにゲームが進行中です。")
        return
    gamestatus[ctx.guild.id] = {"players": [], "roles": {}, "status": "募集"}
    await ctx.send("🎯 人狼ゲームを開始します！ \n30秒間参加者を募集します。参加者は`!参加`と入力してください")
    print(gamestatus)
    await asyncio.sleep(30)
    # if len(gamestatus[ctx.guild.id]["players"]) < 3:
    #     await ctx.send("参加者が3人未満のため、ゲームを中止します。")
    #     del gamestatus[ctx.guild.id]
    #     return
    await ctx.send(f"ゲームを開始します！役職を配布します。")
    await start_game(ctx)

@client.command(name="参加")
async def join_game(ctx):
    if ctx.guild.id not in gamestatus or gamestatus[ctx.guild.id]["status"] != "募集":
        await ctx.send("現在、ゲームは募集していません。")
        return

    if ctx.author in gamestatus[ctx.guild.id]["players"]:
        await ctx.send("すでに参加しています！")
    else:
        gamestatus[ctx.guild.id]["players"].append(ctx.author)
        await ctx.reply(f"{ctx.author.display_name} が参加しました！")
        print(gamestatus)

async def start_game(ctx):
    guild_id = ctx.guild.id
    gamestatus[guild_id]["status"] = "配役"

    # 役職リスト（必要に応じて増やせる）
    roles_list = ["人狼", "占い師"]
    for i in range(len(gamestatus[guild_id]["players"]) - 2):
        roles_list.append("村人")

    
    # 役職シャッフル
    players = gamestatus[guild_id]["players"]
    random.shuffle(roles_list)
    assigned_roles = random.sample(roles_list, len(players))

    # 各プレイヤーに役職をDM
    for player, role in zip(players, assigned_roles):
        gamestatus[guild_id]["roles"][player] = role
        try:
            await player.send(f"あなたの役職は **{role}** です。")
        except:
            await ctx.send(f"{player.mention} さんにDMが送れません！")
            await ctx.send(f"役職を配布することができないため、ゲームを中止します。")
            del gamestatus[guild_id]
            return
    # await ctx.send(gamestatus)
    await asyncio.sleep(2)
    await ctx.send("役職の配布が完了しました。ゲームを開始します...")
    await night_phase(ctx)


async def night_phase(ctx):
    await ctx.send("夜がはじましました。みなさんDMの指示に従って行動してください。")
    guild_id = ctx.guild.id
    gamestatus[guild_id]["status"] = "夜ターン"

    for user, role in gamestatus[guild_id]["roles"].items():
        if role == "人狼":
            await send_target_selection(user, gamestatus[guild_id]["players"], "襲撃")
        elif role == "占い師":
            await send_target_selection(user, gamestatus[guild_id]["players"], "占い")
            await user.send(f"占ったユーザーの役職は、{gamestatus[guild_id]['roles'][gamestatus[guild_id]['占い_target']]}です。")
        else:
            await user.send("夜ターンです。村人は何もできません。")
    await ctx.send("全員の夜アクション受付が完了しました。")
    await ctx.send(gamestatus[guild_id])



async def send_target_selection(user, players, action_name):
    """夜ターンの選択肢をDMで送って番号入力を待つ"""
    await user.send(f"夜ターンです。誰を{action_name}しますか？")

    # 選択肢表示
    selectable = [p for p in players if p != user]
    for idx, player in enumerate(selectable, start=1):
        await user.send(f"{idx}. {player.display_name}({player.name})")

    await user.send(f"番号で選んでください（例: `1`）")

    def check(m):
        return (
            m.author == user and
            m.content.isdigit() and
            1 <= int(m.content) <= len(selectable)
        )

    try:
        msg = await client.wait_for("message", check=check, timeout=60)  # 60秒待機
        target_idx = int(msg.content) - 1
        target_player = selectable[target_idx]
        await user.send(f"あなたは {target_player.display_name} を{action_name}しました。")

        # 選択結果をゲーム状態に保存
        gamestatus[user.guild.id][f"{action_name}_target"] = target_player

    except asyncio.TimeoutError:
        await user.send("時間切れです。行動できませんでした。")




client.run(tkn.TOKEN)