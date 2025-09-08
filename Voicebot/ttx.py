import aiohttp
from typing import Optional
VOICEVOX_URL = "http://localhost:50021"
DEFAULT_SPEAKER = 1

class VoiceVoxTTS:
    def __init__(self, voicevox_url: str = VOICEVOX_URL):
        self.voicevox_url = voicevox_url
        
    async def generate_audio(self, text: str, speaker: int = DEFAULT_SPEAKER) -> Optional[bytes]:
        try:
            async with aiohttp.ClientSession() as session:
                query_params = {
                    'text': text,
                    'speaker': speaker
                }
                
                async with session.post(
                    f"{self.voicevox_url}/audio_query",
                    params=query_params
                ) as response:
                    if response.status != 200:
                        print(f"Audio query failed: {response.status}")
                        return None
                    
                    query_data = await response.json()
                async with session.post(
                    f"{self.voicevox_url}/synthesis",
                    params={'speaker': speaker},
                    json=query_data
                ) as response:
                    if response.status != 200:
                        print(f"Synthesis failed: {response.status}")
                        return None
                    
                    return await response.read()
                    
        except Exception as e:
            print(f"VoiceVox error: {e}")
            return None