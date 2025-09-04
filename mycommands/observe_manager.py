import tkn

isobserve = False
observe_guild = []
async def observe(ctx, mode="server"):
    if ctx.author.id != tkn.admin_id:
            await ctx.reply("このコマンドは管理者のみ使用できます。")
            return
    global isobserve
    if mode == "server":
        if ctx.guild.id in observe_guild:
            observe_guild.remove(ctx.guild.id)
            await ctx.reply("監視を停止しました。")
        else:
            observe_guild.append(ctx.guild.id)
            await ctx.reply("監視を開始しました。監視中のサーバーでの発言を管理者に通知します。")
    elif mode == "c":
        if ctx.channel.id in observe_guild:
            observe_guild.remove(ctx.channel.id)
            await ctx.reply("監視を停止しました。")
        else:
            observe_guild.append(ctx.channel.id)
            await ctx.reply("監視を開始しました。このチャンネルでの発言を管理者に通知します。")
    else:
        await ctx.reply("無効なモードです。`!監視` または `!監視 c` を使用してください。")