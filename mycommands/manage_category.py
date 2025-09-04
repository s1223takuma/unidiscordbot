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
    