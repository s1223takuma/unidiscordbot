import os
import discord
from pdf2image import convert_from_path
from math import ceil

async def open_pdf(message):
    cnt = 0
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith(".pdf"):
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
                if message.content == "":
                    await message.channel.send(f"# {attachment.filename}")
                else:
                    cnt += 1
                    await message.channel.send(f"# {message.content}({cnt})")
                for chunk_index in range(total_chunks):
                    chunk_paths = paths[chunk_index*chunk_size : (chunk_index+1)*chunk_size]
                    files = [discord.File(p) for p in chunk_paths]
                    await message.channel.send(
                        content=f"{chunk_index*chunk_size+1}p ~ {chunk_index*chunk_size+len(files)}p",
                        files=files
                    )
                for path in paths:
                    os.remove(path)
                os.remove(file_path)