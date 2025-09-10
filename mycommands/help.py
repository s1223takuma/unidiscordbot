import discord
from discord.ext import commands

async def help(ctx):
    embed = discord.Embed(title="ヘルプ", description="以下のコマンドを使用できます。")
    embed.add_field(name="!join", value="ボイスチャンネルに参加します。", inline=False)
    embed.add_field(name="!leave", value="ボイスチャンネルから退出します。", inline=False)
    embed.add_field(name="!監視 [server/c]", value="サーバー全体または特定のチャンネルの発言を監視します。(管理者専用)", inline=False)
    embed.add_field(name="!カテゴリ作成 [カテゴリー名]", value="指定した名前でカテゴリーとチャンネルを作成します。", inline=False)
    embed.add_field(name="!url [日数]", value="指定した日数の招待URLを発行します。", inline=False)
    embed.add_field(name="!お問い合わせ [内容]", value="管理者にお問い合わせを送信します。", inline=False)
    embed.add_field(name="!人狼", value="人狼ゲームを開始します。", inline=False)
    embed.add_field(name="!search [クエリ]", value="ウェブ検索を行います。", inline=False)
    embed.add_field(name="!searchnews [クエリ]", value="ニュース検索を行います。", inline=False)
    embed.add_field(name="!searchimage [クエリ]", value="画像検索を行います。", inline=False)
    embed.add_field(name="!speaker [話者ID]", value="話者を指定します。0-88の範囲で指定してください。", inline=False)
    embed.add_field(name="!speakers", value="利用可能な話者の一覧を表示します。", inline=False)
    await ctx.send(embed=embed)