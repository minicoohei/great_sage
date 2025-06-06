"""
音声認識モジュール
OpenAI Whisper APIを使用して音声をテキストに変換
"""

import os
import io
import wave
import numpy as np
import logging
from typing import Optional
from openai import OpenAI
from datetime import datetime

logger = logging.getLogger('great_sage.speech_recognizer')


class SpeechRecognizer:
    """音声認識クラス"""
    
    def __init__(self, config: dict):
        self.config = config.get('speech_recognition', {})
        
        # OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEYが設定されていません")
        
        self.client = OpenAI(api_key=api_key)
        
        # Recognition parameters
        self.model = self.config.get('model', 'whisper-1')
        self.language = self.config.get('language', 'ja')
        self.temperature = self.config.get('temperature', 0.2)
        
        logger.info("音声認識モジュールを初期化しました")
    
    def _numpy_to_wav_bytes(self, audio_data: np.ndarray, sample_rate: int) -> bytes:
        """NumPy配列をWAVバイトデータに変換"""
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        wav_buffer.seek(0)
        return wav_buffer.read()
    
    def recognize(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[dict]:
        """音声をテキストに変換"""
        try:
            # Convert numpy array to WAV bytes
            wav_bytes = self._numpy_to_wav_bytes(audio_data, sample_rate)
            
            # Create a file-like object
            audio_file = io.BytesIO(wav_bytes)
            audio_file.name = "audio.wav"
            
            # Call Whisper API
            logger.debug("Whisper APIを呼び出しています...")
            
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=self.language,
                temperature=self.temperature
            )
            
            # Extract transcription
            text = response.text.strip()
            
            if text:
                result = {
                    'text': text,
                    'timestamp': datetime.now().isoformat(),
                    'duration': len(audio_data) / sample_rate
                }
                
                logger.info(f"【解】認識結果: {text}")
                return result
            else:
                logger.debug("音声が認識されませんでした")
                return None
                
        except Exception as e:
            logger.error(f"音声認識エラー: {e}")
            return None
    
    def recognize_with_timestamps(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[dict]:
        """タイムスタンプ付きで音声を認識"""
        try:
            # Convert numpy array to WAV bytes
            wav_bytes = self._numpy_to_wav_bytes(audio_data, sample_rate)
            
            # Create a file-like object
            audio_file = io.BytesIO(wav_bytes)
            audio_file.name = "audio.wav"
            
            # Call Whisper API with timestamp
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=self.language,
                response_format="verbose_json",
                temperature=self.temperature
            )
            
            if response.text:
                result = {
                    'text': response.text.strip(),
                    'timestamp': datetime.now().isoformat(),
                    'duration': response.duration if hasattr(response, 'duration') else len(audio_data) / sample_rate,
                    'segments': response.segments if hasattr(response, 'segments') else []
                }
                
                return result
            else:
                return None
                
        except Exception as e:
            logger.error(f"音声認識エラー（タイムスタンプ付き）: {e}")
            return None


def test_speech_recognizer():
    """音声認識のテスト"""
    # Test with a sample audio
    config = {
        'speech_recognition': {
            'model': 'whisper-1',
            'language': 'ja',
            'temperature': 0.2
        }
    }
    
    try:
        recognizer = SpeechRecognizer(config)
        
        # Create a test audio (1 second of silence)
        sample_rate = 16000
        duration = 1.0
        audio_data = np.zeros(int(sample_rate * duration), dtype=np.int16)
        
        print("音声認識テストを実行中...")
        result = recognizer.recognize(audio_data, sample_rate)
        
        if result:
            print(f"認識結果: {result}")
        else:
            print("音声が認識されませんでした（無音のテストデータのため）")
            
    except Exception as e:
        print(f"テストエラー: {e}")


if __name__ == '__main__':
    test_speech_recognizer()
EOF < /dev/null