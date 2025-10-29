import os
import discord
from pdf2image import convert_from_path
from math import ceil
import json

DATA_PATH = "data/dashboard.json"

async def open_pdf(message):
    if not message.attachments:
        return

    guild = message.guild
    if guild is None:
        return
    if not os.path.exists(DATA_PATH):
        await message.channel.send("⚠️ ダッシュボードが未作成です。`/pdf-dashboard` を先に実行してください。")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            dashboard_data = json.load(f)
        except json.JSONDecodeError:
            dashboard_data = {}

    dashboard_id = dashboard_data.get(str(guild.id))
    dashboard_message_id = dashboard_id.get("dashboard_ID") if dashboard_id else None
    category_id = dashboard_id.get("category_ID") if dashboard_id else None
    if not dashboard_message_id:
        await message.channel.send("このサーバーのダッシュボードが登録されていません。\n```/pdf-dashboard``` を実行して登録してください。")
        return

    for attachment in message.attachments:
        if not attachment.filename.endswith(".pdf"):
            continue
        if message.content != "":
            base_name = message.content
        else:
            base_name = os.path.splitext(attachment.filename)[0]
        channel_name = f"pdf-{base_name}".replace(" ", "-").lower()

        if category_id:
            category = guild.get_channel(category_id)
            channel = await category.create_text_channel(channel_name)
        else:
            channel = await message.reply("カテゴリーが見つかりません。エラーが起きている可能性がございますので、お手数ですが開発者にお問い合わせください")
            return

        await channel.send(f"# {attachment.filename}")

        file_path = f"./{attachment.filename}"
        await attachment.save(file_path)

        images = convert_from_path(file_path)
        paths = []
        for i, img in enumerate(images):
            img_path = f"page_{i+1}.png"
            img.save(img_path, "PNG")
            paths.append(img_path)

        chunk_size = 10
        total_chunks = ceil(len(paths) / chunk_size)
        await channel.send(f"{attachment}")
        for chunk_index in range(total_chunks):
            chunk_paths = paths[chunk_index*chunk_size : (chunk_index+1)*chunk_size]
            files = [discord.File(p) for p in chunk_paths]
            await channel.send(
                content=f"{chunk_index*chunk_size+1}p ~ {chunk_index*chunk_size+len(files)}p",
                files=files
            )

        for path in paths:
            os.remove(path)
        os.remove(file_path)

        dashboard_message = None
        for c in guild.text_channels:
            try:
                m = await c.fetch_message(dashboard_message_id)
                dashboard_message = m
                break
            except:
                continue

        if dashboard_message:
            embed = dashboard_message.embeds[0] if dashboard_message.embeds else discord.Embed(
                title="📂 PDFリンクまとめダッシュボード(最大25件まで)",
                description=f"{guild.name} に送信されたPDF一覧です",
                color=discord.Color.blue()
            )

            desc = embed.description or ""
            filename = attachment.filename[:-4] if message.content == "" else message.content
            new_line = f"[{filename.lower()}](https://discord.com/channels/{guild.id}/{channel.id})"
            updated_desc = desc + ("\n" if desc else "") + new_line

            embed.description = updated_desc
            await dashboard_message.edit(embed=embed)


async def remove_pdf_link(guild, pdf_name):
    if not os.path.exists(DATA_PATH):
        return False
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            dashboard_data = json.load(f)
        except json.JSONDecodeError:
            dashboard_data = {}
    guild_data = dashboard_data.get(str(guild.id))
    if not guild_data:
        return False
    dashboard_message_id = guild_data.get("dashboard_ID")
    if not dashboard_message_id:
        return False
    dashboard_message = None
    for c in guild.text_channels:
        try:
            m = await c.fetch_message(dashboard_message_id)
            dashboard_message = m
            break
        except Exception as e:
            print(f"⚠️ {c.name} でメッセージ取得失敗: {e}")
    if not dashboard_message or not dashboard_message.embeds:
        return False
    else:
        print(f"✅ ダッシュボードメッセージを取得しました: {dashboard_message.id}")
    embed = dashboard_message.embeds[0]
    lines = (embed.description or "").splitlines()
    print(lines)
    new_lines = [line for line in lines if f"{pdf_name}" not in line]
    if len(new_lines) == len(lines):
        return False
    embed.description = "\n".join(new_lines)
    await dashboard_message.edit(embed=embed)
    return True