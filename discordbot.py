import discord
from discord.ui import View, Button
import traceback
from discord.ext import commands,tasks
from discord.utils import get
from os import getenv
import asyncio
import tkn
import random

TOKEN = getenv('Discord_TOKEN')

# 接続に必要なオブジェクトを生成
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents)
invite = None


# 起動時に動作する処理
@client.event
async def on_ready():
    print('ログインしました')
    await client.tree.sync()

isobserve = False

observe_guild = []

@client.event
async def on_message(message):
    user = client.get_user(tkn.admin_id)
    if not message.author.bot:
        if message.guild.id in observe_guild or message.channel.id in observe_guild:
            if message.content[0] != "!":
                await user.send(f"「{message.author.guild.name}」で{message.author.mention}が発言:{message.content}")
    if message.author.id == 1083313772258676786:
        return
    await client.process_commands(message)

@client.command(name="監視")
async def observe(ctx, mode="server"):
    if ctx.author.id != tkn.admin_id:
            await ctx.reply("このコマンドは管理者のみ使用できます。")
            return
    global isobserve
    if mode == "server":
        if ctx.guild.id in observe_guild:
            observe_guild.remove(ctx.guild.id)
            await ctx.reply("監視を停止しました。")
        else:
            observe_guild.append(ctx.guild.id)
            await ctx.reply("監視を開始しました。監視中のサーバーでの発言を管理者に通知します。")
    elif mode == "c":
        if ctx.channel.id in observe_guild:
            observe_guild.remove(ctx.channel.id)
            await ctx.reply("監視を停止しました。")
        else:
            observe_guild.append(ctx.channel.id)
            await ctx.reply("監視を開始しました。このチャンネルでの発言を管理者に通知します。")
    else:
        await ctx.reply("無効なモードです。`!監視` または `!監視 c` を使用してください。")

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

# ===========ここから人狼=============
gamestatus = {}

class JoinView(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)  # タイムアウトしない
        self.ctx = ctx

    @discord.ui.button(label="参加", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: Button):
        guild_id = self.ctx.guild.id

        # 募集していない場合
        if gamestatus[guild_id]["status"] != "募集":
            await interaction.response.send_message("現在募集は行っていません。", ephemeral=True)
            return

        player = interaction.user
        if player in gamestatus[guild_id]["players"]:
            await interaction.response.send_message("すでに参加しています！", ephemeral=True)
        else:
            gamestatus[guild_id]["players"].append(player)
            await interaction.response.send_message(f"{player.display_name} が参加しました！", ephemeral=False)


@client.command(name="人狼")
async def setup(ctx):
    if ctx.guild.id in gamestatus:
        await ctx.send("すでにゲームが進行中です。")
        return
    gamestatus[ctx.guild.id] = {
        "players": [],
        "roles": {},
        "status": "募集",
        "襲撃_target": [],
        "守護_target": [],
        "vote": {},
        "player_channel": {},
        "dead_players": [],
        "category": None,
        "heven_channel": None,
        "heaven_voice_channel": None,
        "turn": 1,
        "wolf_list": []
    }
    view = JoinView(ctx)
    await ctx.send(
        "人狼ゲームを開始します！\n30秒間参加者を募集します。\n下のボタンから参加してください。",
        view=view
    )
    await asyncio.sleep(30)
    if len(gamestatus[ctx.guild.id]["players"]) < 3:
        await ctx.send("参加者が3人未満のため、ゲームを中止します。")
        del gamestatus[ctx.guild.id]
        return
    await ctx.send(f"ゲームを開始します！役職を配布します。")
    category = await ctx.guild.create_category("人狼")
    gamestatus[ctx.guild.id]["category"] = category
    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)}
    heaven = await category.create_text_channel("天界", overwrites=overwrites)
    heaven_voice = await category.create_voice_channel("天界", user_limit=99, overwrites=overwrites)
    gamestatus[ctx.guild.id]["heven_channel"] = heaven
    gamestatus[ctx.guild.id]["heaven_voice_channel"] = heaven_voice
    for player in gamestatus[ctx.guild.id]["players"]:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            player: discord.PermissionOverwrite(read_messages=True),
        }
        channel = await category.create_text_channel(f"{player.name}-chat", overwrites=overwrites)
        gamestatus[ctx.guild.id]["player_channel"][player] = channel
    await start_game(ctx)




async def start_game(ctx):
    guild_id = ctx.guild.id
    gamestatus[guild_id]["status"] = "配役"
    if len(gamestatus[guild_id]["players"]) < 6:
        roles_list = ["人狼","占い師","騎士"] + ["村人" for _ in range(len(gamestatus[guild_id]["players"])-3)]
    elif len(gamestatus[guild_id]["players"]) < 8:
        roles_list = ["人狼","狂人","占い師","騎士"] + ["村人" for _ in range(len(gamestatus[guild_id]["players"])-4)]
    else:
        roles_list = ["人狼","人狼","狂人","占い師","騎士"] + ["村人" for _ in range(len(gamestatus[guild_id]["players"])-5)]
    random.shuffle(roles_list)
    for player, role in zip(gamestatus[guild_id]["players"], roles_list):
        gamestatus[guild_id]["roles"][player] = role
        if role == "人狼":
            gamestatus[guild_id]["wolf_list"].append(player)
        try:
            await gamestatus[ctx.guild.id]["player_channel"][player].send(f"{player.mention}\nあなたの役職は **{role}** です。")
        except:
            await ctx.send(f"{player.mention} さんにメッセージが送れません！ ゲーム中止。")
            del gamestatus[guild_id]
            await cleanup_channels(ctx)
            return
    lunatic = [key for key, value in gamestatus[guild_id]["roles"].items() if value == "狂人"]
    if lunatic:
        lunatic = lunatic[0]
        await gamestatus[guild_id]["player_channel"][lunatic].send("あなたは狂人です。人狼と協力して村人を排除してください。")
        # await gamestatus[guild_id]["player_channel"][lunatic].send(f"人狼は{', '.join([wolf.display_name for wolf in gamestatus[guild_id]['wolf_list']])} です。")
    gamestatus[guild_id]["status"] = "夜ターン"
    await asyncio.sleep(2)
    await ctx.send("役職配布完了。夜ターン開始...")
    await night_phase(ctx)



async def night_phase(ctx):
    guild_id = ctx.guild.id
    await ctx.send(f"**====={gamestatus[guild_id]['turn']}日目夜=====**")
    gamestatus[guild_id]["status"] = "夜ターン"
    await ctx.send("夜が始まりました。各自専用チャンネルで行動してください。")
    tasks = []
    for user, role in gamestatus[guild_id]["roles"].items():
        if user in gamestatus[guild_id]["dead_players"]:
            continue
        if gamestatus[guild_id]['turn'] != 1:
            if role == "人狼":
                tasks.append(send_target_selection(guild_id, user, gamestatus[guild_id]["players"], "襲撃"))
            elif role == "占い師":
                gamestatus[guild_id][f'占い{user}_target'] = []
                tasks.append(send_target_selection(guild_id, user, gamestatus[guild_id]["players"], f"占い{user}"))
            elif role == "騎士":
                gamestatus[guild_id][f'騎士{user}_target'] = []
                tasks.append(send_target_selection(guild_id, user, gamestatus[guild_id]["players"], "守護"))
            else:
                tasks.append(gamestatus[guild_id]["player_channel"][user].send("夜ターンです。村人は何もできません。"))
        else:
            await gamestatus[guild_id]["player_channel"][user].send("初日の夜は行動できません。")
    await asyncio.gather(*tasks)
    for user, role in gamestatus[guild_id]["roles"].items():
        if role == "占い師":
            targets = gamestatus[guild_id].get(f'占い{user}_target', [])
            if targets:
                target_player = targets[0]
                if gamestatus[guild_id]["roles"][target_player] == "人狼":
                    await gamestatus[guild_id]["player_channel"][user].send(f"占ったユーザー {target_player.display_name} は **人狼** です。")
                else:
                    await gamestatus[guild_id]["player_channel"][user].send(f"占ったユーザー {target_player.display_name} は **人間** です。")
            else:
                await gamestatus[guild_id]["player_channel"][user].send("占いは行われませんでした。")
    for victim in gamestatus[guild_id]["襲撃_target"]:
        if gamestatus[guild_id]["守護_target"] != []:
            if victim == gamestatus[guild_id]["守護_target"][0]:
                await gamestatus[guild_id]["player_channel"][victim].send("あなたは騎士に守られました。")
                gamestatus[guild_id]["襲撃_target"].remove(victim)
                gamestatus[guild_id]["守護_target"] = []
            elif victim not in gamestatus[guild_id]["dead_players"]:
                gamestatus[guild_id]["守護_target"] = []
                gamestatus[guild_id]["dead_players"].append(victim)
                gamestatus[guild_id]["players"].remove(victim)
                await gamestatus[guild_id]["player_channel"][victim].send("あなたは人狼に襲撃されました。死亡しました。")
                overwrite_text = discord.PermissionOverwrite(read_messages=True)
                await gamestatus[guild_id]["heven_channel"].set_permissions(victim, overwrite=overwrite_text)
                overwrite_voice = discord.PermissionOverwrite(connect=True, speak=True, read_messages=True)
                await gamestatus[guild_id]["heaven_voice_channel"].set_permissions(victim, overwrite=overwrite_voice)
                if victim.voice:
                    await victim.move_to(gamestatus[guild_id]["heaven_voice_channel"])
        else:
            if victim not in gamestatus[guild_id]["dead_players"]:
                gamestatus[guild_id]["守護_target"] = []
                gamestatus[guild_id]["dead_players"].append(victim)
                gamestatus[guild_id]["players"].remove(victim)
                await gamestatus[guild_id]["player_channel"][victim].send("あなたは人狼に襲撃されました。死亡しました。")
                overwrite_text = discord.PermissionOverwrite(read_messages=True)
                await gamestatus[guild_id]["heven_channel"].set_permissions(victim, overwrite=overwrite_text)
                overwrite_voice = discord.PermissionOverwrite(connect=True, speak=True, read_messages=True)
                await gamestatus[guild_id]["heaven_voice_channel"].set_permissions(victim, overwrite=overwrite_voice)
                if victim.voice:
                    await victim.move_to(gamestatus[guild_id]["heaven_voice_channel"])
    await asyncio.sleep(2)
    await judge_phase(ctx)
    if gamestatus[guild_id]["status"] != "勝敗判定":
        await day_phase(ctx)
    else:
        del gamestatus[guild_id]
        return



async def day_phase(ctx):
    guild_id = ctx.guild.id
    gamestatus[guild_id]["turn"] += 1
    gamestatus[guild_id]["status"] = "昼ターン"
    await ctx.send(f"**====={gamestatus[guild_id]['turn']}日目昼=====**")
    dead_names = [p.mention for p in gamestatus[guild_id]["襲撃_target"]]
    if dead_names:
        await ctx.send(f"夜が明けました。昨晩の被害者は {', '.join(dead_names)} です。")
        gamestatus[guild_id]["襲撃_target"] = []
    else:
        await ctx.send("夜が明けました。昨晩の被害者はいませんでした。")
    await ctx.send("議論の時間です。5分間で犯人を探してください。")
    await asyncio.sleep(180)
    await ctx.send("投票開始!各自専用チャンネルで投票してください。")
    tasks = [send_vote_selection(guild_id, user, gamestatus[guild_id]["players"]) for user in gamestatus[guild_id]["players"]]
    await asyncio.gather(*tasks)
    if gamestatus[guild_id]["vote"]:
        max_votes = max(gamestatus[guild_id]["vote"].values())
        # await ctx.send(gamestatus[guild_id]['vote'])
        top_candidates = [p for p, v in gamestatus[guild_id]["vote"].items() if v == max_votes]
        executed = random.choice(top_candidates)  # 同票ならランダム
        await ctx.send(f"投票の結果、{executed.mention} が処刑されました。")
        gamestatus[guild_id]["players"].remove(executed)
        gamestatus[guild_id]["dead_players"].append(executed)
        overwrite_text = discord.PermissionOverwrite(read_messages=True)
        await gamestatus[guild_id]["heven_channel"].set_permissions(executed, overwrite=overwrite_text)
        overwrite_voice = discord.PermissionOverwrite(connect=True, speak=True, read_messages=True)
        await gamestatus[guild_id]["heaven_voice_channel"].set_permissions(executed, overwrite=overwrite_voice)
        if executed.voice:
            await executed.move_to(gamestatus[guild_id]["heaven_voice_channel"])
    else:
        await ctx.send("投票の結果、処刑者なし。")
    gamestatus[guild_id]["vote"] = {}
    await asyncio.sleep(5)
    await judge_phase(ctx)
    if gamestatus[guild_id]["status"] != "勝敗判定":
        await night_phase(ctx)
    else:
        del gamestatus[guild_id]
        return



async def judge_phase(ctx):
    guild_id = ctx.guild.id
    alive_roles = [role for player, role in gamestatus[guild_id]["roles"].items() if player not in gamestatus[guild_id]["dead_players"]]
    wolf_count = alive_roles.count("人狼")
    villager_count = len(alive_roles) - wolf_count
    if wolf_count == 0:
        await ctx.send("村人陣営の勝利！")
        gamestatus[guild_id]["status"] = "勝敗判定"
        await show_roles(ctx)
        await cleanup_channels(ctx)
    elif wolf_count >= villager_count:
        await ctx.send("人狼陣営の勝利！")
        gamestatus[guild_id]["status"] = "勝敗判定"
        await show_roles(ctx)
        await cleanup_channels(ctx)
    else:
        await ctx.send("次のターンへ進みます。")


async def show_roles(ctx):
    guild_id = ctx.guild.id
    await ctx.send("最終結果")
    for player, role in gamestatus[guild_id]["roles"].items():
        await ctx.send(f"{player.mention} : {role}")

async def send_target_selection(guild_id, user, players, action_name):
    selectable = [p for p in players if p != user and p not in gamestatus[guild_id]["dead_players"]]
    await gamestatus[guild_id]["player_channel"][user].send(f"誰を{action_name[0:2]}しますか？")
    for idx, player in enumerate(selectable, start=1):
        await gamestatus[guild_id]["player_channel"][user].send(f"{idx}. {player.display_name}({player.name})")
    await gamestatus[guild_id]["player_channel"][user].send("番号で選んでください（例: 1）")
    def check(m):
        return m.author == user and m.content.isdigit() and 1 <= int(m.content) <= len(selectable)
    try:
        msg = await client.wait_for("message", check=check, timeout=30)
        target_player = selectable[int(msg.content) - 1]
        await gamestatus[guild_id]["player_channel"][user].send(f"あなたは {target_player.display_name}({target_player.name}) を{action_name[0:2]}しました。")
        gamestatus[guild_id][f"{action_name}_target"].append(target_player)
    except asyncio.TimeoutError:
        await gamestatus[guild_id]["player_channel"][user].send("時間切れで行動できませんでした。")

async def send_vote_selection(guild_id, user, players):
    selectable = [p for p in players if p != user]
    await gamestatus[guild_id]["player_channel"][user].send("誰を処刑しますか？")
    for idx, player in enumerate(selectable, start=1):
        await gamestatus[guild_id]["player_channel"][user].send(f"{idx}. {player.display_name}({player.name})")
    await gamestatus[guild_id]["player_channel"][user].send("番号で選んでください（例: 1）")
    def check(m):
        return m.author == user and m.content.isdigit() and 1 <= int(m.content) <= len(selectable)
    try:
        msg = await client.wait_for("message", check=check, timeout=30)
        target_player = selectable[int(msg.content) - 1]
        gamestatus[guild_id]["vote"][target_player] = gamestatus[guild_id]["vote"].get(target_player, 0) + 1
        await gamestatus[guild_id]["player_channel"][user].send(f"{target_player.display_name}({target_player.name}) に投票しました。")
    except asyncio.TimeoutError:
        await gamestatus[guild_id]["player_channel"][user].send("時間切れで投票できませんでした。")

async def cleanup_channels(ctx):
    guild_id = ctx.guild.id
    category = gamestatus[guild_id].get("category")
    if category:
        for channel in category.channels:
            await channel.delete()
        await category.delete()


client.run(TOKEN)