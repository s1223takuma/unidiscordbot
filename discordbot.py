import discord
import traceback
from discord.ext import commands,tasks
from discord.utils import get
from os import getenv
from datetime import time,datetime
import pytz
import requests
import tkn

# 接続に必要なオブジェクトを生成
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents)
invite = None




# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    c = Loops()
    c.check_time.start()
    print('ログインしました')

class Loops:
    @tasks.loop(seconds=3600)
    async def check_time(self):
        global invite
        channels = client.get_channel(1118169853606502443)
        if invite == None:
            invite = invite = await channels.create_invite(max_age = 7 * 24 * 3600)
        invite = invite
        target_time = time(12)
        now = datetime.now().time()
        print(now)
        print(target_time)
        if str(now)[0:2] == str(target_time)[0:2]:
            invite = await channels.create_invite(max_age = 24 * 3600)
            print(invite.url)
            # Google Apps Scriptにデータを送信
            try:
                payload = {'inviteLink': invite.url}
                response = requests.post("https://script.google.com/macros/s/AKfycbzC0g3AQuklpnXw-6iP36xP5wG2ZxrG6QXADkSNWXOfvDt_upIHUTKChCe_dpGBpmZqOA/exec", params=payload)
                
                if response.status_code == 200:
                    adminchannel = client.get_channel(1194279786357465239)
                    await adminchannel.send(f"{invite.url} 新規URLが作成されました")
                else:
                    print(f"Error adding data to Google Sheet: {response.text}")
            except Exception as e:
                print(f"Error adding data to Google Sheet: {e}")

    @check_time.before_loop
    async def before_check(self):
        await client.wait_until_ready()


@client.event
async def on_message(message):
    print(message)
    if message.author.id == 1083313772258676786:
        return
    await client.process_commands(message)
    alert_role = discord.utils.get(message.guild.roles, name="ちゅうがくせい")
    post_time = message.created_at
    jst = pytz.timezone('Asia/Tokyo')
    post_time_jst = post_time.astimezone(jst)
    str_time = int(post_time_jst.strftime("%H%M"))
    if str_time <= 800 or str_time >= 2200:
        if alert_role in message.author.roles:
            if message.author.guild.name == 'botお試し':
                embed = discord.Embed(title="中学生の発言検知", description=f'{message.content}\n該当メッセージリンク {message.jump_url}')
                adminchannel = client.get_channel(1194279786357465239)
                await adminchannel.send(embed=embed)
                embed = discord.Embed(title="あなたの発言が検知されました")
                await message.author.send(embed=embed)
                print(str_time)
                print('けんち')
    else:
        print(str_time)


@client.command(name="カテゴリ作成")
async def create_category(ctx, *, content):
    category = await ctx.guild.create_category(content)

    text_channels = [f'{content}{category_type}' for category_type in ["雑談", "募集", "解説動画、情報"]]
    voice_channels = [f'{content}VC{vc_number}' for vc_number in range(1, 3)]

    for channel_name in text_channels:
        await category.create_text_channel(channel_name)

    # Add 聞き専チャットvc1 and 聞き専チャットvc2
    await category.create_text_channel(f'聞き専チャットvc1')
    await category.create_text_channel(f'聞き専チャットvc2')

    for channel_name in voice_channels:
        await category.create_voice_channel(channel_name, user_limit=99)

    await ctx.reply(f'「{content}」のカテゴリーとチャンネルが作成されました。')


@client.command(name='url')
async def geturl(ctx,day=1):

    if day >= 30:
        await ctx.send('30日を超える招待URLは発行できません')
        return
    channels = client.get_channel(ctx.channel.id)
    invite = await channels.create_invite(max_age = int(day) * 24 * 3600)
    print(invite.url)

    # Google Apps Scriptにデータを送信
    try:
        payload = {'inviteLink': invite.url}
        response = requests.post("https://script.google.com/macros/s/AKfycbzC0g3AQuklpnXw-6iP36xP5wG2ZxrG6QXADkSNWXOfvDt_upIHUTKChCe_dpGBpmZqOA/exec", params=payload)
        
        if response.status_code == 200:
            await ctx.send(f"{invite.url} この鯖のURLあげる！ 有効期限は{day}日間だよ！気をつけてね！")
            embed = discord.Embed(title="新規URL発行", description=f"{ctx.author.mention}が{day}日間の招待リンクを作成しました")
            adminchannel = client.get_channel(1194279786357465239)
            await adminchannel.send(embed=embed)
        else:
            print(f"Error adding data to Google Sheet: {response.text}")
            await ctx.send('An error occurred while updating the Google Sheet.')
    except Exception as e:
        print(f"Error adding data to Google Sheet: {e}")
        await ctx.send('An error occurred while updating the Google Sheet.')


@client.command(name="招待リンク")
async def surl(ctx,day=10):
    if day >= 2592000:
        await ctx.send('2592000を超える招待URLは発行できません')
        return
    channels = client.get_channel(1118169854046896148)
    invite = await channels.create_invite(max_age = int(day)) 
    print(invite.url)
    await ctx.send(f"{invite.url} この鯖のURLあげる！ 有効期限は{day}秒間だよ！気をつけてね！")
    embed = discord.Embed(title="新規URL発行", description=f"{ctx.author.mention}が{day}秒間の招待リンクを作成しました")
    adminchannel = client.get_channel(1194279786357465239)
    await adminchannel.send(embed=embed)


# @client.command(name="お問い合わせ")
# async def contact(ctx,*,inquiry):
#     print(inquiry)
#     managementrole = discord.utils.get(ctx.guild.roles, name='運営')
#     teacherrole = discord.utils.get(ctx.guild.roles, name='職員')
#     overwrites = {
#         ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
#         ctx.author: discord.PermissionOverwrite(read_messages=True),
#         managementrole: discord.PermissionOverwrite(read_messages=True),
#         teacherrole: discord.PermissionOverwrite(read_messages=True),
#     }
#     channel = await ctx.guild.create_text_channel(f'お問い合わせ- {ctx.author.name}', overwrites=overwrites)

#     embed = discord.Embed(title="新規お問い合わせ", description=inquiry)
#     await channel.send(embed=embed)
#     await channel.send(f"こんにちは！\n{ctx.author.mention}さんのお問い合わせを受け付けました。{managementrole.mention}よりご連絡いたします。")







client.run(tkn.TOKEN)