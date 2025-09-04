from games.jinro.status import gamestatus
import asyncio
from bot_setup import client


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