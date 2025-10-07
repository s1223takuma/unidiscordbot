import discord
async def mention_slash(interaction: discord.Interaction,cnt: int, member: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "管理者権限を持っていないため、このコマンドは実行できません。",
            ephemeral=True
        )
        return
    for i in range(cnt):
        await interaction.channel.send(f"{member.mention}さん、呼ばれていますよ！")