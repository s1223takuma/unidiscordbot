import discord
from rapidfuzz import process, fuzz
import json

SYNONYMS = {
    "大学全般": ["大学", "単位", "授業", "履修", "成績"],
    "教職関連": ["教育", "教師", "教育実習"],
    "資格試験": ["資格", "試験", "検定"],
}

def find_tag(user_input: str, tags: dict):
    for tag, keywords in SYNONYMS.items():
        if any(k in user_input for k in keywords):
            print(f"[synonym hit] '{user_input}' → {tag}")
            if tag in tags:
                return [(tag, title) for title, _ in tags[tag]]
            return [(tag, None)]

    all_titles = []
    for tag, items in tags.items():
        for title, _ in items:
            all_titles.append((title, tag))

    results = process.extract(user_input, [t[0] for t in all_titles], scorer=fuzz.partial_ratio)
    print(f"[fuzz results] {results}")

    matched = []
    for name, score, _ in results:
        if score >= 50:
            for title, tag in all_titles:
                if title == name:
                    matched.append((tag, title))

    if matched:
        return matched
    return None


async def search(ctx, *, query: str):
    DATA_PATH = "data/pdfdashboard.json"
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            dashboard_data = json.load(f)
        except json.JSONDecodeError:
            dashboard_data = {}
    guild_data = dashboard_data.get(str(ctx.guild.id))
    if not guild_data:
        await ctx.send("このサーバーにはダッシュボードが設定されていません。")
        return
    tags = guild_data.get("tags", {})
    result = find_tag(query, tags)
    if not result:
        await ctx.send("🔍 一致する資料が見つかりませんでした。")
        return
    embed = discord.Embed(
        title=f"検索結果: {query}",
        color=discord.Color.blurple()
    )
    for tag, title in result:
        channel_id = next((mid for t, mid in tags[tag] if t == title), None)
        if channel_id:
            url = f"https://discord.com/channels/{ctx.guild.id}/{channel_id}"
            embed.add_field(
                name=f"{url}",
                value=f"タグ: {tag}",
                inline=False
            )
    await ctx.send(embed=embed)