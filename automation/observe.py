import mycommands.observe_manager as ob

async def send_observe_message(message):
    if message.guild is None:
        return
    users = ob.adminuser.get(message.guild.id, [])
    for user_id in users:
        user = message.guild.get_member(user_id)
        if not message.author.bot:
            if message.guild and (message.guild.id in ob.observe_guild or message.channel.id in ob.observe_guild):
                if not message.content.startswith("!"):
                    await user.send(
                        f"「{message.guild.name}」で{message.author.mention}が発言:{message.content}"
                    )