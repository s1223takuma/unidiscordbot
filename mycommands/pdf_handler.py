import os
import discord
from pdf2image import convert_from_path
from math import ceil
import json

DATA_PATH = "data/pdfdashboard.json"

async def open_pdf(message, tag_list=None, filename=None):
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
    if not dashboard_id:
        await message.channel.send("このサーバーのダッシュボードが登録されていません。\n```/pdf-dashboard``` を実行して登録してください。")
        return

    dashboard_message_id = dashboard_id.get("dashboard_ID")
    category_id = dashboard_id.get("category_ID")
    tags_data = dashboard_id.setdefault("tags", {})

    for attachment in message.attachments:
        if not attachment.filename.endswith(".pdf"):
            continue
        base_name = filename if filename != None else os.path.splitext(attachment.filename)[0]
        channel_name = f"pdf-{base_name}".replace(" ", "-").lower()

        # チャンネル作成
        if category_id:
            category = guild.get_channel(category_id)
            channel = await category.create_text_channel(channel_name)
        else:
            await message.reply("カテゴリーが見つかりません。開発者にお問い合わせください。")
            return

        await channel.send(f"# {base_name}")

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

        if tag_list:
            for tag in tag_list:
                tag_entry = tags_data.setdefault(tag, [])
                if channel.id not in tag_entry:
                    tag_entry.append(channel.id)
        else:
            tag_entry = tags_data.setdefault("タグ無し", [])
            if channel.id not in tag_entry:
                tag_entry.append(channel.id)

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=4, ensure_ascii=False)

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
            filename = attachment.filename[:-4] if filename == None else filename
            new_line = f"[{filename.lower()}](https://discord.com/channels/{guild.id}/{channel.id})"
            embed.description = desc + ("\n" if desc else "") + new_line
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
    new_lines = [line for line in lines if f"{pdf_name}" not in line]
    if len(new_lines) == len(lines):
        print("⚠️ 一致するPDF名が見つかりませんでした")
        return False
    embed.description = "\n".join(new_lines)
    await dashboard_message.edit(embed=embed)
    print(f"🗑️ Embedから {pdf_name} を削除しました")
    tags = guild_data.get("tags", {})
    removed_channels = []
    for tag, channel_ids in list(tags.items()):
        new_ids = []
        for ch_id in channel_ids:
            ch = guild.get_channel(ch_id)
            if not ch:
                continue
            if pdf_name.lower() in ch.name.lower():
                print(f"タグ「{tag}」からチャンネル {ch.name} を削除")
                removed_channels.append(ch_id)
            else:
                new_ids.append(ch_id)
        if new_ids:
            tags[tag] = new_ids
        else:
            print(f"タグ「{tag}」が空になったので削除")
            del tags[tag]
    guild_data["tags"] = tags
    dashboard_data[str(guild.id)] = guild_data
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=4)
    return True
