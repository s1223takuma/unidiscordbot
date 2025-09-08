from Voicebot.voicebot import voice_clients,read_channels
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.reply("ボイスチャンネルに参加してからコマンドを実行してください。")
        return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        voice_client = await voice_channel.connect()
        await ctx.reply(f"{voice_channel.name}に参加しました。")
        voice_clients[ctx.guild.id] = voice_client
        read_channels[ctx.guild.id] = ctx.channel.id
    else:
        await ctx.reply("すでにボイスチャンネルに参加しています。")

async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.reply("ボイスチャンネルに参加していません。")
    else:
        guild_id = ctx.guild.id
        await ctx.voice_client.disconnect()
        await ctx.reply("ボイスチャンネルから退出しました。")
        if guild_id in voice_clients:
            del voice_clients[guild_id]
            
            if guild_id in read_channels:
                del read_channels[guild_id]