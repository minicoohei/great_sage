# 大賢者システム (Great Sage System)

リアルタイム会話解析・ファクトチェックシステム

## 概要

大賢者システムは、会議や会話をリアルタイムで解析し、以下の機能を提供します：

- 🎤 **音声認識**: リアルタイムで音声をテキストに変換
- 🔍 **矛盾検出**: 過去の発言との矛盾を自動検出
- ✅ **ファクトチェック**: 発言内容の事実確認
- 👥 **話者識別**: 誰が何を話したかを記録（Phase 2）
- 📢 **通知機能**: 重要な検出事項をSlackやデスクトップに通知

## システム要件

- macOS (Intel/Apple Silicon)
- Python 3.8以上
- マイク（音声入力用）
- OpenAI APIキー

## クイックスタート

### 1. セットアップ

```bash
# セットアップスクリプトを実行
cd /path/to/grate_sage
./setup.sh
```

### 2. 環境変数の設定

`.env`ファイルを編集してAPIキーを設定：

```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. システムの起動

```bash
cd great_sage
source venv/bin/activate
python main.py
```

## ディレクトリ構造

```
great_sage/
├── src/
│   ├── modules/         # 各機能モジュール
│   │   ├── audio_recorder.py     # 音声録音
│   │   ├── speech_recognizer.py  # 音声認識
│   │   └── ...
│   └── config/          # 設定関連
├── data/               # データ保存
│   ├── conversations/  # 会話記録
│   ├── speakers/       # 話者プロファイル
│   └── knowledge_base/ # 知識ベース
├── results/            # 解析結果
├── logs/              # ログファイル
├── tests/             # テストコード
├── config.yaml        # 設定ファイル
├── requirements.txt   # 依存パッケージ
└── main.py           # エントリーポイント
```

## 主な機能

### Phase 1: 基礎実装（実装済み）
- ✅ 音声録音機能
- ✅ 音声認識（OpenAI Whisper）
- ⏳ 基本的な解析機能

### Phase 2: 解析強化（開発中）
- ⏳ 話者識別
- ⏳ 過去ログとの照合
- ⏳ リアルタイムファクトチェック

### Phase 3: 通知システム（計画中）
- ⏳ Slack連携
- ⏳ 音声フィードバック
- ⏳ デスクトップ通知

### Phase 4: 進化（将来計画）
- ⏳ 機械学習による精度向上
- ⏳ 感情解析
- ⏳ 智慧之王（ラファエル）へのアップグレード

## 使用方法

### 基本的な使い方

```bash
# 通常起動
python main.py

# デバッグモードで起動
python main.py --debug

# カスタム設定ファイルを使用
python main.py --config my_config.yaml
```

### 設定のカスタマイズ

`config.yaml`ファイルで各種設定を変更できます：

```yaml
audio:
  sample_rate: 16000      # サンプリングレート
  silence_threshold: 500  # 無音判定の閾値

speech_recognition:
  language: "ja"          # 認識言語
  temperature: 0.2        # 認識の確実性

analysis:
  keyword_alerts:         # 監視キーワード
    - "問題"
    - "重要"
```

## トラブルシューティング

### PortAudioエラー
```bash
brew install portaudio
```

### マイクが認識されない
システム環境設定 > セキュリティとプライバシー > マイクでアプリケーションを許可

### OpenAI APIエラー
- APIキーが正しく設定されているか確認
- APIの利用制限に達していないか確認

## 開発

### テストの実行
```bash
pytest tests/
```

### コードフォーマット
```bash
black src/
flake8 src/
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストは歓迎します！大きな変更の場合は、まずissueを作成して変更内容を議論してください。

## 謝辞

このシステムは「転生したらスライムだった件」の大賢者からインスピレーションを得ています。

---

【告】このドキュメントは大賢者システムによって生成されました。  
【答】質問や問題がある場合は、issueを作成してください。
EOF < /dev/null