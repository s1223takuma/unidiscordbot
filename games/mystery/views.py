import discord
from discord.ui import View, Button
from games.mystery.status import gamestatus


class JoinView(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)  # タイムアウトしない
        self.ctx = ctx
    @discord.ui.button(label="参加", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: Button):
        guild_id = self.ctx.guild.id
        # 募集していない場合
        if gamestatus[guild_id]["status"] != "募集":
            await interaction.response.send_message("現在募集は行っていません。", ephemeral=True)
            return
        player = interaction.user
        if player in gamestatus[guild_id]["players"]:
            await interaction.response.send_message("すでに参加しています！", ephemeral=True)
        else:
            gamestatus[guild_id]["players"].append(player)
            await interaction.response.send_message(f"{player.display_name} が参加しました！", ephemeral=False)

    @discord.ui.button(label="犯人希望で参加", style=discord.ButtonStyle.red)
    async def criminal_button(self, interaction: discord.Interaction, button: Button):
        guild_id = self.ctx.guild.id
        # 募集していない場合
        if gamestatus[guild_id]["status"] != "募集":
            await interaction.response.send_message("現在募集は行っていません。", ephemeral=True)
            return
        player = interaction.user
        if player in gamestatus[guild_id]["criminals"] or player in gamestatus[guild_id]["players"]:
            await interaction.response.send_message("すでに参加しています！", ephemeral=True)
        else:
            gamestatus[guild_id]["criminals"].append(player)
            gamestatus[guild_id]["players"].append(player)
            await interaction.response.send_message(f"{player.display_name} が参加しました！", ephemeral=False)