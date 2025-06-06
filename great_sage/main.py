#\!/usr/bin/env python3
"""
大賢者 (Great Sage) System - Main Entry Point
リアルタイム会話解析・ファクトチェックシステム
"""

import os
import sys
import logging
import click
import yaml
from dotenv import load_dotenv
from datetime import datetime

# Import custom modules
from src.modules.audio_recorder import AudioRecorder
from src.modules.speech_recognizer import SpeechRecognizer
from src.modules.analyzer import BasicAnalyzer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('great_sage')


class GreatSage:
    """大賢者システムのメインクラス"""
    
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._validate_environment()
        
        # Initialize components
        try:
            self.audio_recorder = AudioRecorder(self.config)
            self.speech_recognizer = SpeechRecognizer(self.config)
            self.analyzer = BasicAnalyzer(self.config)
            self.notifier = None  # TODO: Phase 3
            
            # Set up audio callbacks
            self.audio_recorder.on_speech_start = self._on_speech_start
            self.audio_recorder.on_speech_end = self._on_speech_end
            
            logger.info("【告】大賢者システムを起動しています...")
        except Exception as e:
            logger.error(f"【エラー】コンポーネントの初期化に失敗: {e}")
            sys.exit(1)
    
    def _load_config(self, config_path):
        """設定ファイルを読み込む"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"設定ファイルが見つかりません: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"設定ファイルの読み込みエラー: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """ロギングの設定"""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('file', 'logs/great_sage.log')
        
        # Create log directory if not exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
    
    def _validate_environment(self):
        """環境変数の検証"""
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("【警告】OPENAI_API_KEYが設定されていません")
            logger.info("【解】.envファイルにOPENAI_API_KEYを設定してください")
    
    def _on_speech_start(self):
        """発話開始時のコールバック"""
        print("\n🎤 聞いています...")
    
    def _on_speech_end(self, audio_data):
        """発話終了時のコールバック"""
        print("📝 解析中...")
        
        # 音声認識
        result = self.speech_recognizer.recognize(audio_data, self.config['audio']['sample_rate'])
        
        if result:
            text = result['text']
            print(f"\n【発言】{text}")
            
            # テキスト解析
            analysis = self.analyzer.analyze(text)
            
            # アラートがある場合は表示
            if analysis['alerts']:
                for alert in analysis['alerts']:
                    print(f"【{alert['severity'].upper()}】{alert['message']}")
            
            # キーワードが検出された場合
            if analysis['keywords']:
                print(f"【解】重要キーワード: {', '.join(analysis['keywords'])}")
    
    def start(self):
        """システムを開始"""
        logger.info("【告】大賢者システムが起動しました")
        logger.info("【解】音声解析を開始します...")
        
        try:
            print("\n" + "="*50)
            print("大賢者システムへようこそ！")
            print("="*50)
            print("\n【告】音声認識を開始します")
            print("【解】マイクに向かって話してください")
            print("【答】Ctrl+Cで終了できます\n")
            
            # 音声録音を開始
            self.audio_recorder.start_recording()
            
            # メインループ
            import time
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("【告】システムを終了します...")
            self.stop()
    
    def stop(self):
        """システムを停止"""
        # Cleanup resources
        if self.audio_recorder:
            self.audio_recorder.stop_recording()
        
        # 会話サマリーを表示
        if self.analyzer:
            summary = self.analyzer.get_summary()
            if summary.get('total_statements', 0) > 0:
                print("\n" + "="*50)
                print("【告】会話サマリー")
                print("="*50)
                print(f"総発言数: {summary['total_statements']}")
                print(f"話者別: {summary['speakers']}")
                if summary['keyword_frequency']:
                    print(f"頻出キーワード: {summary['keyword_frequency']}")
        
        logger.info("【答】大賢者システムを正常に終了しました")
        sys.exit(0)


@click.command()
@click.option('--config', '-c', default='config.yaml', help='設定ファイルのパス')
@click.option('--debug', is_flag=True, help='デバッグモードで実行')
def main(config, debug):
    """大賢者システムのエントリーポイント"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("デバッグモードで実行中")
    
    sage = GreatSage(config_path=config)
    sage.start()


if __name__ == '__main__':
    main()
EOF < /dev/null