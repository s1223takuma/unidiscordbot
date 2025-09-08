import os
import discord
import asyncio
import tempfile
from ttx import DEFAULT_SPEAKER, VoiceVoxTTS

tts = VoiceVoxTTS()
voice_clients = {}
read_channels = {}
speaker_settings = {}

async def set_speaker(ctx, speaker_id: int = None):
    if speaker_id is None:
        current = speaker_settings.get(ctx.author.id, DEFAULT_SPEAKER)
        await ctx.send(f"🎤 現在の話者ID: {current}\n`!speaker <ID>` で変更できます。")
        return
        
    # 話者IDの範囲チェック（0-46程度）
    if not (0 <= speaker_id <= 50):
        await ctx.send("❌ 話者IDは0-50の範囲で指定してください。")
        return
        
    speaker_settings[ctx.author.id] = speaker_id
    await ctx.send(f"✅ 話者を ID:{speaker_id} に設定しました！")


async def list_speakers(ctx):
    """利用可能な話者一覧を表示"""
    speaker_info = """
🎤 **VoiceVox 話者一覧**
```
0: 四国めたん (あまあま)
1: 四国めたん (ノーマル) ← デフォルト
2: 四国めたん (セクシー)
3: 四国めたん (ツンツン)
8: ずんだもん (ノーマル)
9: ずんだもん (あまあま)
10: ずんだもん (ツンツン)
11: ずんだもん (セクシー)
14: 春日部つむぎ (ノーマル)
15: 春日部つむぎ (おっとり)
16: 波音リツ (ノーマル)
17: 波音リツ (クイーン)
20: 雨晴はう (ノーマル)
21: 玄野武宏 (ノーマル)
23: 白上虎太郎 (ふつう)
27: 青山龍星 (ノーマル)
29: 冥鳴ひまり (ノーマル)
```
使用例: `!speaker 8` (ずんだもんに変更)
    """
    await ctx.send(speaker_info)

async def say_text(ctx, *, text: str):
        """指定したテキストを読み上げ"""
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
        
        # ファイルが正しく作成されているか確認
        if not os.path.exists(temp_path):
            print("❌ Temp file was not created")
            return
            
        file_size = os.path.getsize(temp_path)
        print(f"Temp file size: {file_size} bytes")
        
        # 既に再生中の場合は停止
        if voice_client.is_playing():
            voice_client.stop()
            await asyncio.sleep(0.5)  # 停止を待つ
            
        print("Starting audio playback...")
        
        # FFmpegのオプションを追加
        source = discord.FFmpegPCMAudio(
            temp_path,
            before_options='-loglevel panic',  # FFmpegログを抑制
            options='-vn'  # ビデオストリームを無効化
        )
        
        # 音声を再生
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
    """一時ファイルをクリーンアップ"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Failed to cleanup temp file: {e}")
        
    if error:
        print(f"Audio playback finished with error: {error}")

def clean_text(text: str) -> str:
    """テキストをクリーンアップ（URL、メンション等を除去）"""
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