import discord
from discord.ui import View, Button

from games.mystery.status import gamestatus,location_status
from games.mystery.manager import move_user


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


class SelectView(View):
    def __init__(self, ctx, event, player):
        super().__init__(timeout=None)
        for choice in event.get("choices", []):
            button = Button(label=choice["label"], style=discord.ButtonStyle.green)
            button.callback = self.make_callback(ctx, player, choice["next_location"])
            self.add_item(button)
    def make_callback(self, ctx, player, next_location):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            resolved_location = (
                gamestatus[ctx.guild.id]["player_guestroom"][player.id] if next_location == "自分の部屋" else next_location
            )
            location_status[player.id] = resolved_location
            await move_user(ctx, player, resolved_location)
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(content=f"あなたは{resolved_location}に移動しました。",view=self)
        return callback