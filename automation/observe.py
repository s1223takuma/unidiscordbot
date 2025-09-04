import mycommands.observe_manager as ob

async def send_observe_message(message,admin_id):
    if message.guild is None:
    # DM の場合の処理
        return
    user = message.guild.get_member(admin_id)
    if not message.author.bot:
            if message.guild and (message.guild.id in ob.observe_guild or message.channel.id in ob.observe_guild):
                if not message.content.startswith("!"):
                    await user.send(
                        f"「{message.guild.name}」で{message.author.mention}が発言:{message.content}"
                    )