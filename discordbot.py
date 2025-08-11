import discord
import traceback
from discord.ext import commands,tasks
from discord.utils import get
from os import getenv
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
    gamestatus[ctx.guild.id] = {
        "players": [],
        "roles": {},
        "status": "募集",
        "襲撃_target": [],
        "vote": {},
        "dead_players": []
    }
    await ctx.send("人狼ゲームを開始します！ \n30秒間参加者を募集します。参加者は`!参加`と入力してください")
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



async def start_game(ctx):
    guild_id = ctx.guild.id
    gamestatus[guild_id]["status"] = "配役"

    roles_list = ["人狼", "占い師"] + ["村人"] * (len(gamestatus[guild_id]["players"]) - 2)
    random.shuffle(roles_list)

    for player, role in zip(gamestatus[guild_id]["players"], roles_list):
        gamestatus[guild_id]["roles"][player] = role
        try:
            await player.send(f"あなたの役職は **{role}** です。")
        except:
            await ctx.send(f"{player.mention} さんにDMが送れません！ ゲーム中止。")
            del gamestatus[guild_id]
            return

    await asyncio.sleep(2)
    await ctx.send("役職配布完了。夜ターン開始...")
    await night_phase(ctx)

async def night_phase(ctx):
    guild_id = ctx.guild.id
    gamestatus[guild_id]["status"] = "夜ターン"
    await ctx.send("夜が始まりました。各自DMで行動してください。")

    tasks = []
    for user, role in gamestatus[guild_id]["roles"].items():
        if user in gamestatus[guild_id]["dead_players"]:
            continue
        if role == "人狼":
            tasks.append(send_target_selection(guild_id, user, gamestatus[guild_id]["players"], "襲撃"))
        elif role == "占い師":
            gamestatus[guild_id][f'占い{user}_target'] = []
            tasks.append(send_target_selection(guild_id, user, gamestatus[guild_id]["players"], f"占い{user}"))
        else:
            tasks.append(user.send("夜ターンです。村人は何もできません。"))

    await asyncio.gather(*tasks)

    # 占い結果送信
    for user, role in gamestatus[guild_id]["roles"].items():
        if role == "占い師":
            targets = gamestatus[guild_id].get(f'占い{user}_target', [])
            if targets:
                target_player = targets[0]
                if gamestatus[guild_id]["roles"][target_player] == "人狼":
                    await user.send(f"占ったユーザー {target_player.display_name} は **人狼** です。")
                else:
                    await user.send(f"占ったユーザー {target_player.display_name} は **人間** です。")
            else:
                await user.send("占いは行われませんでした。")

    # 襲撃処理
    for victim in gamestatus[guild_id]["襲撃_target"]:
        if victim not in gamestatus[guild_id]["dead_players"]:
            gamestatus[guild_id]["dead_players"].append(victim)
            gamestatus[guild_id]["players"].remove(victim)
            await victim.send("あなたは人狼に襲撃されました。死亡しました。")
    gamestatus[guild_id]["襲撃_target"] = []

    await asyncio.sleep(2)
    await judge_phase(ctx)
    if gamestatus[guild_id]["status"] != "勝敗判定":
        await day_phase(ctx)

async def day_phase(ctx):
    guild_id = ctx.guild.id
    gamestatus[guild_id]["status"] = "昼ターン"
    dead_names = [p.mention for p in gamestatus[guild_id]["dead_players"]]
    if dead_names:
        await ctx.send(f"夜が明けました。昨晩の被害者は {', '.join(dead_names)} です。")
    else:
        await ctx.send("夜が明けました。昨晩の被害者はいませんでした。")

    await ctx.send("議論時間（5秒間のデモ）...")
    await asyncio.sleep(5)

    await ctx.send("投票開始！DMで投票してください。")
    tasks = [send_vote_selection(guild_id, user, gamestatus[guild_id]["players"]) for user in gamestatus[guild_id]["players"]]
    await asyncio.gather(*tasks)


    if gamestatus[guild_id]["vote"]:
        max_votes = max(gamestatus[guild_id]["vote"].values())
        await ctx.send(gamestatus[guild_id]['vote'])
        top_candidates = [p for p, v in gamestatus[guild_id]["vote"].items() if v == max_votes]
        executed = random.choice(top_candidates)  # 同票ならランダム
        await ctx.send(f"投票の結果、{executed.mention} が処刑されました。")
        gamestatus[guild_id]["players"].remove(executed)
        gamestatus[guild_id]["dead_players"].append(executed)
    else:
        await ctx.send("投票の結果、処刑者なし。")

    gamestatus[guild_id]["vote"] = {}
    await asyncio.sleep(2)
    await judge_phase(ctx)
    if gamestatus[guild_id]["status"] != "勝敗判定":
        await night_phase(ctx)

async def judge_phase(ctx):
    guild_id = ctx.guild.id
    alive_roles = [role for player, role in gamestatus[guild_id]["roles"].items() if player not in gamestatus[guild_id]["dead_players"]]
    wolf_count = alive_roles.count("人狼")
    villager_count = len(alive_roles) - wolf_count

    if wolf_count == 0:
        await ctx.send("村人陣営の勝利！")
        gamestatus[guild_id]["status"] = "勝敗判定"
        await show_roles(ctx)
    elif wolf_count >= villager_count:
        await ctx.send("人狼陣営の勝利！")
        gamestatus[guild_id]["status"] = "勝敗判定"
        await show_roles(ctx)
    else:
        await ctx.send("次のターンへ進みます。")

async def show_roles(ctx):
    guild_id = ctx.guild.id
    await ctx.send("最終結果")
    for player, role in gamestatus[guild_id]["roles"].items():
        await ctx.send(f"{player.mention} : {role}")
    del gamestatus[guild_id]



async def send_target_selection(guild_id, user, players, action_name):
    selectable = [p for p in players if p != user and p not in gamestatus[guild_id]["dead_players"]]
    await user.send(f"誰を{action_name[0:2]}しますか？")
    for idx, player in enumerate(selectable, start=1):
        await user.send(f"{idx}. {player.display_name}({player.name})")
    await user.send("番号で選んでください（例: 1）")

    def check(m):
        return m.author == user and m.content.isdigit() and 1 <= int(m.content) <= len(selectable)

    try:
        msg = await client.wait_for("message", check=check, timeout=30)
        target_player = selectable[int(msg.content) - 1]
        await user.send(f"あなたは {target_player.display_name} を{action_name[0:2]}しました。")
        gamestatus[guild_id][f"{action_name}_target"].append(target_player)
    except asyncio.TimeoutError:
        await user.send("時間切れで行動できませんでした。")

async def send_vote_selection(guild_id, user, players):
    selectable = [p for p in players if p != user]
    await user.send("誰を処刑しますか？")
    for idx, player in enumerate(selectable, start=1):
        await user.send(f"{idx}. {player.display_name}({player.name})")
    await user.send("番号で選んでください（例: 1）")

    def check(m):
        return m.author == user and m.content.isdigit() and 1 <= int(m.content) <= len(selectable)

    try:
        msg = await client.wait_for("message", check=check, timeout=30)
        target_player = selectable[int(msg.content) - 1]
        gamestatus[guild_id]["vote"][target_player] = gamestatus[guild_id]["vote"].get(target_player, 0) + 1
        await user.send(f"{target_player.display_name} に投票しました。")
    except asyncio.TimeoutError:
        await user.send("時間切れで投票できませんでした。")

client.run(tkn.TOKEN)