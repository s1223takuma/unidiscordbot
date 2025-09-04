import random
import asyncio
import discord
from games.jinro.status import gamestatus
from games.jinro.selection import send_target_selection, send_vote_selection


async def start_game(ctx):
    from games.jinro.setup import cleanup_channels
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
    from games.jinro.setup import cleanup_channels
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