from Voicebot.voicebot import voice_clients,read_channels,speak_text

async def clean_air(ctx):
    if ctx.author.voice is None:
        await ctx.reply("ボイスチャンネルに参加してからコマンドを実行してください。")
        return
    voice_channel = ctx.author.voice
    if ctx.voice_client is None:
        voice_client = await voice_channel.connect()
        await ctx.reply(f"{voice_channel.name}に参加しました。")
        voice_clients[ctx.guild.id] = voice_client
        read_channels[ctx.guild.id] = ctx.channel.id
    else:
        await ctx.reply("すでにボイスチャンネルに参加しています。")
