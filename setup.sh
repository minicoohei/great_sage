#\!/bin/bash

# Great Sage System Setup Script
# 大賢者システムのセットアップスクリプト

echo "=========================================="
echo "大賢者システム セットアップスクリプト"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check OS
if [[ "$OSTYPE" \!= "darwin"* ]]; then
    echo -e "${RED}エラー: このスクリプトはmacOS用です${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        exit 1
    fi
}

# Step 1: Check and install Homebrew
echo "1. Homebrewの確認..."
if \! command_exists brew; then
    echo -e "${YELLOW}Homebrewがインストールされていません。インストールしますか？ (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        print_status $? "Homebrewのインストール"
    else
        echo -e "${RED}Homebrewが必要です。インストールを中止します。${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Homebrewは既にインストールされています${NC}"
fi

# Step 2: Install portaudio
echo ""
echo "2. PortAudioの確認..."
if \! brew list portaudio &>/dev/null; then
    echo "PortAudioをインストールしています..."
    brew install portaudio
    print_status $? "PortAudioのインストール"
else
    echo -e "${GREEN}✓ PortAudioは既にインストールされています${NC}"
fi

# Step 3: Check Python
echo ""
echo "3. Python3の確認..."
if \! command_exists python3; then
    echo -e "${RED}Python3がインストールされていません${NC}"
    echo "brew install python3 でインストールしてください"
    exit 1
else
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    echo -e "${GREEN}✓ Python $PYTHON_VERSION が見つかりました${NC}"
fi

# Step 4: Create virtual environment
echo ""
echo "4. Python仮想環境の作成..."
cd great_sage

if [ \! -d "venv" ]; then
    python3 -m venv venv
    print_status $? "仮想環境の作成"
else
    echo -e "${GREEN}✓ 仮想環境は既に存在します${NC}"
fi

# Step 5: Activate virtual environment and install packages
echo ""
echo "5. Pythonパッケージのインストール..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
print_status $? "Pythonパッケージのインストール"

# Step 6: Check .env file
echo ""
echo "6. 環境変数の確認..."
if [ \! -f ".env" ]; then
    echo -e "${YELLOW}.envファイルが見つかりません${NC}"
    echo "テンプレートから.envファイルを作成します..."
    cp .env.template .env 2>/dev/null || echo "# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Slack Configuration
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# Application Settings
DEBUG=False
LOG_LEVEL=INFO" > .env
    echo -e "${GREEN}✓ .envファイルを作成しました${NC}"
fi

# Check if OPENAI_API_KEY is set
if grep -q "your_openai_api_key_here" .env; then
    echo -e "${YELLOW}⚠️  .envファイルにOPENAI_API_KEYを設定してください${NC}"
    echo "   OpenAI APIキーは https://platform.openai.com/api-keys から取得できます"
fi

# Step 7: Create necessary directories
echo ""
echo "7. 必要なディレクトリの作成..."
mkdir -p logs
mkdir -p data/{conversations,speakers,knowledge_base}
mkdir -p results/{analysis,reports}
echo -e "${GREEN}✓ ディレクトリを作成しました${NC}"

# Step 8: Test installation
echo ""
echo "8. インストールのテスト..."
python -c "import pyaudio; import openai; print('✓ 基本的なモジュールが正常にインポートできました')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}インストールテスト成功${NC}"
else
    echo -e "${YELLOW}⚠️  一部のモジュールでエラーが発生しました${NC}"
    echo "   個別にデバッグが必要かもしれません"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}セットアップが完了しました！${NC}"
echo ""
echo "次のステップ:"
echo "1. .envファイルを編集してOPENAI_API_KEYを設定"
echo "2. 仮想環境を有効化: source venv/bin/activate"
echo "3. システムを起動: python main.py"
echo ""
echo "詳細は README.md を参照してください"
echo "=========================================="

# Deactivate virtual environment
deactivate
