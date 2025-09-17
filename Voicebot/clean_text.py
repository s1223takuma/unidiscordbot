import re
import json
import os
import bot_setup as bs
# よく使われる英単語の読み方
word_to_kana = {
    'discord': 'ディスコード',
    'bot': 'ボット',
    'api': 'エーピーアイ',
    'url': 'ユーアールエル',
    'http': 'エイチティーティーピー',
    'https': 'エイチティーティーピーエス',
    'ww': 'ワラワラ',
    'ok': 'オーケー',
    'ng': 'エヌジー',
    'pc': 'ピーシー',
    'id': 'アイディー',
    'php': 'ピーエイチピー',
    'sql': 'エスキューエル',
    'html': 'エイチティーエムエル',
    'css': 'シーエスエス',
    'js': 'ジェーエス',
    'json': 'ジェーソン',
    '〜': 'ー',
    "ggrks": "ググレカス"
}

async def add_word(ctx,word,kana):
    guild_id = ctx.guild.id
    if guild_id not in bs.guild_to_kana:
        bs.guild_to_kana[guild_id] = {}
    bs.guild_to_kana[guild_id][word] = kana
    path = "data/guild_to_kana.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({str(gid): words for gid, words in bs.guild_to_kana.items()}, f, ensure_ascii=False, indent=4)
    await ctx.reply(f'単語を追加しました: {word} -> {kana}')


def advanced_convert(ctx,text):
    if ctx.guild and ctx.guild.id in bs.guild_to_kana:
        for word, kana in bs.guild_to_kana[ctx.guild.id].items():
            text = re.sub(re.escape(word), kana, text, flags=re.IGNORECASE)
    for word, kana in word_to_kana.items():
        text = re.sub(re.escape(word), kana, text, flags=re.IGNORECASE)
    return text


def clean_text(ctx,text: str) -> str:
    # URL除去
    text = re.sub(r'https?://\S+', 'URL', text)
    # メンション除去
    text = re.sub(r'<@!?\d+>', 'メンション', text)
    # チャンネル言及除去
    text = re.sub(r'<#\d+>', 'チャンネル', text)
    # 絵文字除去
    text = re.sub(r'<:\w+:\d+>', '絵文字', text)
    # 改行を句点に
    text = text.replace('\n', '。')
    text = advanced_convert(ctx,text)
    return text.strip()