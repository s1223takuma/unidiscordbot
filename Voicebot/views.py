import discord

class SpeakerMenu(discord.ui.View):
    def __init__(self, ctx, speakers):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.speakers = list(speakers.items())
        self.current_page = 0

        # グループ分け
        group1 = self.speakers[:15]
        group2 = self.speakers[15:]

        # Select1
        options1 = [discord.SelectOption(label=chara) for chara, _ in group1]
        select1 = discord.ui.Select(placeholder="キャラグループ1", options=options1)
        select1.callback = self.select_callback
        self.add_item(select1)

        # Select2
        options2 = [discord.SelectOption(label=chara) for chara, _ in group2]
        select2 = discord.ui.Select(placeholder="キャラグループ2", options=options2)
        select2.callback = self.select_callback
        self.add_item(select2)

    async def select_callback(self, interaction: discord.Interaction):
        label = interaction.data["values"][0]  # 選択されたキャラ名
        for i, (chara, voices) in enumerate(self.speakers):
            if chara == label:
                self.current_page = i
                await interaction.response.edit_message(embed=self.get_embed(i), view=self)
                break

    def get_embed(self, index):
        chara, voices = self.speakers[index]
        embed = discord.Embed(title=f"🎤 {chara}", color=discord.Color.blue())
        embed.add_field(name="ボイス", value="\n".join(voices), inline=False)
        embed.set_thumbnail(url="https://voicevox.hiroshiba.jp/img/voicevox_icon.png")
        embed.set_footer(text=f"{index + 1}/{len(self.speakers)}ページ")
        return embed