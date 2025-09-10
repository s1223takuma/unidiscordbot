import re
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
    'json': 'ジェーソン'
}
guild_to_kana = {}

async def add_word(ctx,word,kana):
    guild_id = ctx.guild.id
    if guild_id not in guild_to_kana:
        guild_to_kana[guild_id] = {}  # ← ここで初期化
    guild_to_kana[guild_id][word] = kana
    await ctx.reply(f'単語を追加しました: {word} -> {kana}{guild_to_kana,word_to_kana}')

def advanced_convert(ctx,text):
    if ctx.guild and ctx.guild.id in guild_to_kana:
        for word, kana in guild_to_kana[ctx.guild.id].items():
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

    text = advanced_convert(ctx,text)
    # 改行を句点に
    text = text.replace('\n', '。')
    
    return text.strip()