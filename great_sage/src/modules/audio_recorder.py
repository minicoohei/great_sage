"""
音声録音モジュール
リアルタイムで音声を録音し、発話区間を検出する
"""

import pyaudio
import numpy as np
import queue
import threading
import logging
from collections import deque
from typing import Optional, Callable

logger = logging.getLogger('great_sage.audio_recorder')


class AudioRecorder:
    """音声録音クラス"""
    
    def __init__(self, config: dict):
        self.config = config.get('audio', {})
        
        # Audio parameters
        self.sample_rate = self.config.get('sample_rate', 16000)
        self.chunk_size = self.config.get('chunk_size', 1024)
        self.channels = self.config.get('channels', 1)
        self.format = pyaudio.paInt16
        
        # VAD parameters
        self.silence_threshold = self.config.get('silence_threshold', 500)
        self.silence_duration = self.config.get('silence_duration', 0.5)
        
        # Audio interface
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Buffers
        self.audio_queue = queue.Queue()
        self.recording_buffer = []
        
        # State
        self.is_recording = False
        self.is_speaking = False
        self._stop_event = threading.Event()
        
        # Callbacks
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        
        logger.info("音声録音モジュールを初期化しました")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """音声入力のコールバック関数"""
        if self.is_recording:
            # Convert byte data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            self.audio_queue.put(audio_data)
        
        return (in_data, pyaudio.paContinue)
    
    def _calculate_rms(self, audio_chunk):
        """音声のRMS（Root Mean Square）を計算"""
        return np.sqrt(np.mean(audio_chunk.astype(np.float32) ** 2))
    
    def _process_audio(self):
        """音声処理のメインループ"""
        silence_chunks = 0
        chunks_per_second = self.sample_rate / self.chunk_size
        silence_chunks_threshold = int(self.silence_duration * chunks_per_second)
        
        while not self._stop_event.is_set():
            try:
                # Get audio chunk from queue
                audio_chunk = self.audio_queue.get(timeout=0.1)
                
                # Calculate volume
                rms = self._calculate_rms(audio_chunk)
                
                # Voice Activity Detection
                if rms > self.silence_threshold:
                    if not self.is_speaking:
                        self.is_speaking = True
                        self.recording_buffer = []
                        logger.debug("【告】発話を検出しました")
                        if self.on_speech_start:
                            self.on_speech_start()
                    
                    silence_chunks = 0
                    self.recording_buffer.append(audio_chunk)
                    
                else:
                    if self.is_speaking:
                        silence_chunks += 1
                        self.recording_buffer.append(audio_chunk)
                        
                        if silence_chunks > silence_chunks_threshold:
                            self.is_speaking = False
                            logger.debug("【告】発話が終了しました")
                            
                            # Combine audio chunks
                            audio_data = np.concatenate(self.recording_buffer)
                            
                            if self.on_speech_end:
                                self.on_speech_end(audio_data)
                            
                            self.recording_buffer = []
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"音声処理エラー: {e}")
    
    def start_recording(self):
        """録音を開始"""
        if self.is_recording:
            logger.warning("すでに録音中です")
            return
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self._stop_event.clear()
            
            # Start processing thread
            self.processing_thread = threading.Thread(
                target=self._process_audio,
                daemon=True
            )
            self.processing_thread.start()
            
            logger.info("【告】音声録音を開始しました")
            
        except Exception as e:
            logger.error(f"録音開始エラー: {e}")
            raise
    
    def stop_recording(self):
        """録音を停止"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self._stop_event.set()
        
        # Stop and close stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        # Wait for processing thread to finish
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=1.0)
        
        logger.info("【告】音声録音を停止しました")
    
    def __del__(self):
        """クリーンアップ"""
        self.stop_recording()
        if hasattr(self, 'audio'):
            self.audio.terminate()


def test_audio_recorder():
    """音声録音のテスト"""
    import time
    
    config = {
        'audio': {
            'sample_rate': 16000,
            'chunk_size': 1024,
            'channels': 1,
            'silence_threshold': 500,
            'silence_duration': 0.5
        }
    }
    
    recorder = AudioRecorder(config)
    
    def on_speech_start():
        print("\n🎤 発話開始...")
    
    def on_speech_end(audio_data):
        duration = len(audio_data) / config['audio']['sample_rate']
        print(f"📝 発話終了 (長さ: {duration:.2f}秒)")
    
    recorder.on_speech_start = on_speech_start
    recorder.on_speech_end = on_speech_end
    
    print("音声録音テストを開始します（Ctrl+Cで終了）")
    
    try:
        recorder.start_recording()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nテストを終了します")
        recorder.stop_recording()


if __name__ == '__main__':
    test_audio_recorder()
EOF < /dev/null