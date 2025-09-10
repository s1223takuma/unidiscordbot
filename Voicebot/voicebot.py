import os
import discord
import asyncio
import tempfile
from Voicebot.ttx import DEFAULT_SPEAKER, VoiceVoxTTS

tts = VoiceVoxTTS()
voice_clients = {}
read_channels = {}
speaker_settings = {}

async def set_speaker(ctx, speaker_id: int = None):
    if speaker_id is None:
        current = speaker_settings.get(ctx.author.id, DEFAULT_SPEAKER)
        await ctx.send(f"現在の話者ID: {current}\n`!speaker <ID>` で変更できます。")
        return
        
    if not (0 <= speaker_id <= 88):
        await ctx.send("❌ 話者IDは0-88の範囲で指定してください。")
        return
        
    speaker_settings[ctx.author.id] = speaker_id
    await ctx.send(f"✅ 話者を ID:{speaker_id} に設定しました！")
    print(speaker_settings)

async def admin_set_speaker(ctx, member_id,speaker_id: int = None):
    if ctx.author.guild_permissions.administrator:
        if speaker_id is None:
            current = speaker_settings.get(ctx.author.id, DEFAULT_SPEAKER)
            await ctx.send(f"現在の話者ID: {current}\n`!speaker <ID>` で変更できます。")
            return
            
        if not (0 <= speaker_id <= 88):
            await ctx.send("❌ 話者IDは0-88の範囲で指定してください。")
            return
            
        speaker_settings[int(member_id)] = speaker_id
        await ctx.send(f"話者を ID:{speaker_id} に設定しました！")
    print(speaker_settings)

async def list_speakers(ctx):
    speaker_info = """
🎤 **VoiceVox 話者一覧**
```
ID:0  四国めたん (あまあま)
ID:1  ずんだもん (あまあま)
ID:2  四国めたん (ノーマル)
ID:3  ずんだもん (ノーマル)
ID:4  四国めたん (セクシー)
ID:5  ずんだもん (セクシー)
ID:6  四国めたん (ツンツン)
ID:7  ずんだもん (ツンツン)
ID:8  春日部つむぎ (ノーマル)
ID:9  波音リツ (ノーマル)
ID:10 雨晴はう (ノーマル)
ID:11 玄野武宏 (ノーマル)
ID:12 白上虎太郎 (ふつう)
ID:13 青山龍星 (ノーマル)
ID:14 冥鳴ひまり (ノーマル)
ID:15 九州そら (あまあま)
ID:16 九州そら (ノーマル)
ID:17 九州そら (セクシー)
ID:18 九州そら (ツンツン)
ID:19 九州そら (ささやき)
ID:20 もち子さん (ノーマル)
ID:21 剣崎雌雄 (ノーマル)
ID:22 ずんだもん (ささやき)
ID:23 WhiteCUL (ノーマル)
ID:24 WhiteCUL (たのしい)
ID:25 WhiteCUL (かなしい)
ID:26 WhiteCUL (びえーん)
ID:27 後鬼 (人間ver.)
ID:28 後鬼 (ぬいぐるみver.)
ID:29 No.7 (ノーマル)
ID:30 No.7 (アナウンス)
ID:31 No.7 (読み聞かせ)
ID:32 白上虎太郎 (わーい)
ID:33 白上虎太郎 (びくびく)
ID:34 白上虎太郎 (おこ)
ID:35 白上虎太郎 (びえーん)
ID:36 四国めたん (ささやき)
ID:37 四国めたん (ヒソヒソ)
ID:38 ずんだもん (ヒソヒソ)
ID:39 玄野武宏 (喜び)
ID:40 玄野武宏 (ツンギレ)
ID:41 玄野武宏 (悲しみ)
ID:42 ちび式じい (ノーマル)
ID:43 櫻歌ミコ (ノーマル)
ID:44 櫻歌ミコ (第二形態)
ID:45 櫻歌ミコ (ロリ)
ID:46 小夜/SAYO (ノーマル)
ID:47 ナースロボ＿タイプＴ (ノーマル)
ID:48 ナースロボ＿タイプＴ (楽々)
ID:49 ナースロボ＿タイプＴ (恐怖)
ID:50 ナースロボ＿タイプＴ (内緒話)
ID:51 †聖騎士 紅桜† (ノーマル)
ID:52 雀松朱司 (ノーマル)
ID:53 麒ヶ島宗麟 (ノーマル)
ID:54 春歌ナナ (ノーマル)
ID:55 猫使アル (ノーマル)
ID:56 猫使アル (おちつき)
ID:57 猫使アル (うきうき)
ID:58 猫使ビィ (ノーマル)
ID:59 猫使ビィ (おちつき)
ID:60 猫使ビィ (人見知り)
ID:61 中国うさぎ (ノーマル)
ID:62 中国うさぎ (おどろき)
ID:63 中国うさぎ (こわがり)
ID:64 中国うさぎ (へろへろ)
ID:65 波音リツ (クイーン)
ID:66 もち子さん (セクシー／あん子)
ID:67 栗田まろん (ノーマル)
ID:68 あいえるたん (ノーマル)
ID:69 満別花丸 (ノーマル)
ID:70 満別花丸 (元気)
ID:71 満別花丸 (ささやき)
ID:72 満別花丸 (ぶりっ子)
ID:73 満別花丸 (ボーイ)
ID:74 琴詠ニア (ノーマル)
ID:75 ずんだもん (ヘロヘロ)
ID:76 ずんだもん (なみだめ)
ID:77 もち子さん (泣き)
ID:78 もち子さん (怒り)
ID:79 もち子さん (喜び)
ID:80 もち子さん (のんびり)
ID:81 青山龍星 (熱血)
ID:82 青山龍星 (不機嫌)
ID:83 青山龍星 (喜び)
ID:84 青山龍星 (しっとり)
ID:85 青山龍星 (かなしみ)
ID:86 青山龍星 (囁き)
ID:87 後鬼 (人間（怒り）ver.)
ID:88 後鬼 (鬼ver.)
```
使用例: `!speaker 8` (ずんだもんに変更)
    """
    await ctx.send(speaker_info)

async def say_text(ctx, *, text: str):
        guild_id = ctx.guild.id
        
        if guild_id not in voice_clients:
            await ctx.send("先にボイスチャンネルに参加してください！ (`!join`)")
            return
            
        await speak_text(ctx, text, ctx.author.id)

async def speak_text(ctx, text: str, user_id: int):
    if len(text) > 100:
        text = text[:100] + "..."
    text = clean_text(text)
    
    if not text.strip():
        return
        
    guild_id = ctx.guild.id
    voice_client = voice_clients.get(guild_id)
    
    if not voice_client or not voice_client.is_connected():
        return
    speaker_id = speaker_settings.get(user_id, DEFAULT_SPEAKER)
    print(f"Generating audio for: {text[:20]}...")
    audio_data = await tts.generate_audio(text, speaker_id)
    
    if audio_data is None:
        await ctx.send("❌ 音声生成に失敗しました。VoiceVoxサーバーが起動しているか確認してください。")
        return
        
    print(f"Audio data size: {len(audio_data)} bytes")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
            
        print(f"Temp file created: {temp_path}")
        if not os.path.exists(temp_path):
            print("❌ Temp file was not created")
            return
            
        file_size = os.path.getsize(temp_path)
        print(f"Temp file size: {file_size} bytes")
        if voice_client.is_playing():
            voice_client.stop()
            await asyncio.sleep(0.5)
            
        print("Starting audio playback...")
        source = discord.FFmpegPCMAudio(
            temp_path,
            before_options='-loglevel panic', 
            options='-vn'
        )
        voice_client.play(
            source,
            after=lambda e: cleanup_temp_file(temp_path, e)
        )
        
        print("Audio playback started successfully")
        
    except Exception as e:
        print(f"Audio playback error (詳細): {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if 'temp_path' in locals():
            cleanup_temp_file(temp_path, None)
            
        await ctx.send(f"❌ 音声再生エラー: {str(e)}")

def cleanup_temp_file(file_path: str, error):
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Failed to cleanup temp file: {e}")
        
    if error:
        print(f"Audio playback finished with error: {error}")

def clean_text(text: str) -> str:
    import re
    
    # URL除去
    text = re.sub(r'https?://\S+', 'URL', text)
    # メンション除去
    text = re.sub(r'<@!?\d+>', 'メンション', text)
    # チャンネル言及除去
    text = re.sub(r'<#\d+>', 'チャンネル', text)
    # 絵文字除去
    text = re.sub(r'<:\w+:\d+>', '絵文字', text)
    # 改行を句点に
    text = text.replace('\n', '。')
    
    return text.strip()