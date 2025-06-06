"""
基本解析モジュール
キーワード検出と簡易的な矛盾検出を行う
"""

import re
import logging
from typing import List, Dict, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger('great_sage.analyzer')


class BasicAnalyzer:
    """基本的な解析を行うクラス"""
    
    def __init__(self, config: dict):
        self.config = config.get('analysis', {})
        
        # キーワードアラート設定
        self.keyword_alerts = self.config.get('keyword_alerts', [
            "問題", "課題", "リスク", "重要", "決定", 
            "締切", "期限", "予算", "承認", "却下"
        ])
        
        # 矛盾検出の閾値
        self.contradiction_threshold = self.config.get('contradiction_threshold', 0.85)
        
        # 会話履歴（最新100件を保持）
        self.conversation_history = deque(maxlen=100)
        
        logger.info("基本解析モジュールを初期化しました")
    
    def analyze(self, text: str, speaker: Optional[str] = None) -> Dict:
        """テキストを解析"""
        result = {
            'text': text,
            'speaker': speaker or "Unknown",
            'timestamp': datetime.now().isoformat(),
            'alerts': [],
            'keywords': [],
            'analysis': {}
        }
        
        # キーワード検出
        detected_keywords = self._detect_keywords(text)
        if detected_keywords:
            result['keywords'] = detected_keywords
            result['alerts'].append({
                'type': 'keyword',
                'message': f"重要なキーワードを検出: {', '.join(detected_keywords)}",
                'severity': 'info'
            })
        
        # 数値や日付の検出
        numbers = self._extract_numbers(text)
        dates = self._extract_dates(text)
        
        if numbers:
            result['analysis']['numbers'] = numbers
        if dates:
            result['analysis']['dates'] = dates
        
        # 簡易的な感情分析
        sentiment = self._analyze_sentiment(text)
        result['analysis']['sentiment'] = sentiment
        
        # 会話履歴に追加
        self.conversation_history.append({
            'text': text,
            'speaker': result['speaker'],
            'timestamp': result['timestamp'],
            'keywords': detected_keywords
        })
        
        # 簡易的な矛盾検出
        contradictions = self._detect_simple_contradictions(text, speaker)
        if contradictions:
            result['alerts'].extend(contradictions)
        
        return result
    
    def _detect_keywords(self, text: str) -> List[str]:
        """キーワードを検出"""
        detected = []
        for keyword in self.keyword_alerts:
            if keyword in text:
                detected.append(keyword)
        return detected
    
    def _extract_numbers(self, text: str) -> List[Dict]:
        """数値を抽出"""
        numbers = []
        
        # 金額パターン（円、万円、億円など）
        money_pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:円|万円|億円|千円)'
        for match in re.finditer(money_pattern, text):
            numbers.append({
                'value': match.group(0),
                'type': 'money',
                'position': match.span()
            })
        
        # パーセンテージ
        percent_pattern = r'(\d+(?:\.\d+)?)\s*(?:%|％|パーセント)'
        for match in re.finditer(percent_pattern, text):
            numbers.append({
                'value': match.group(0),
                'type': 'percentage',
                'position': match.span()
            })
        
        # 一般的な数値
        number_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?\b'
        for match in re.finditer(number_pattern, text):
            # 既に検出済みでない場合のみ追加
            if not any(match.span()[0] >= n['position'][0] and match.span()[1] <= n['position'][1] for n in numbers):
                numbers.append({
                    'value': match.group(0),
                    'type': 'number',
                    'position': match.span()
                })
        
        return numbers
    
    def _extract_dates(self, text: str) -> List[Dict]:
        """日付を抽出"""
        dates = []
        
        # 日本語の日付パターン
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{1,2}月\d{1,2}日',
            r'今日|明日|明後日|昨日|一昨日',
            r'今週|来週|先週|今月|来月|先月',
            r'月曜|火曜|水曜|木曜|金曜|土曜|日曜'
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                dates.append({
                    'value': match.group(0),
                    'position': match.span()
                })
        
        return dates
    
    def _analyze_sentiment(self, text: str) -> str:
        """簡易的な感情分析"""
        positive_words = ['良い', '素晴らしい', '完璧', '成功', '達成', '順調']
        negative_words = ['悪い', '問題', '失敗', '遅延', '困難', '課題']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_simple_contradictions(self, text: str, speaker: Optional[str]) -> List[Dict]:
        """簡易的な矛盾検出"""
        contradictions = []
        
        # 数値の矛盾をチェック
        current_numbers = self._extract_numbers(text)
        
        for history_item in self.conversation_history:
            # 同じ話者の過去の発言をチェック
            if history_item['speaker'] == speaker:
                # 同じトピックについて異なる数値を述べていないか
                for keyword in history_item['keywords']:
                    if keyword in text:
                        # 簡易的なチェック：同じキーワードで異なる数値
                        history_numbers = self._extract_numbers(history_item['text'])
                        if history_numbers and current_numbers:
                            if history_numbers[0]['value'] \!= current_numbers[0]['value']:
                                contradictions.append({
                                    'type': 'contradiction',
                                    'message': f"【警告】数値の矛盾を検出: 以前「{history_numbers[0]['value']}」→ 現在「{current_numbers[0]['value']}」",
                                    'severity': 'warning',
                                    'previous_statement': history_item['text'],
                                    'previous_timestamp': history_item['timestamp']
                                })
        
        return contradictions
    
    def get_summary(self) -> Dict:
        """これまでの会話のサマリーを取得"""
        if not self.conversation_history:
            return {'message': '会話履歴がありません'}
        
        total_statements = len(self.conversation_history)
        speakers = {}
        all_keywords = []
        
        for item in self.conversation_history:
            # 話者別の発言数をカウント
            speaker = item['speaker']
            speakers[speaker] = speakers.get(speaker, 0) + 1
            
            # キーワードを収集
            all_keywords.extend(item['keywords'])
        
        # キーワードの頻度をカウント
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        return {
            'total_statements': total_statements,
            'speakers': speakers,
            'keyword_frequency': keyword_freq,
            'duration': self._calculate_duration()
        }
    
    def _calculate_duration(self) -> Optional[float]:
        """会話の継続時間を計算"""
        if len(self.conversation_history) < 2:
            return None
        
        first_timestamp = datetime.fromisoformat(self.conversation_history[0]['timestamp'])
        last_timestamp = datetime.fromisoformat(self.conversation_history[-1]['timestamp'])
        
        duration = (last_timestamp - first_timestamp).total_seconds()
        return duration


def test_analyzer():
    """解析モジュールのテスト"""
    config = {
        'analysis': {
            'keyword_alerts': ['重要', '問題', '決定'],
            'contradiction_threshold': 0.85
        }
    }
    
    analyzer = BasicAnalyzer(config)
    
    # テストケース
    test_statements = [
        ("プロジェクトの予算は500万円です", "田中"),
        ("重要な決定を行う必要があります", "鈴木"),
        ("締切は来月15日です", "田中"),
        ("プロジェクトの予算は800万円に変更されました", "田中"),
    ]
    
    print("=== 解析テスト ===\n")
    
    for text, speaker in test_statements:
        print(f"発言者: {speaker}")
        print(f"発言: {text}")
        
        result = analyzer.analyze(text, speaker)
        
        if result['keywords']:
            print(f"キーワード: {result['keywords']}")
        
        if result['alerts']:
            for alert in result['alerts']:
                print(f"{alert['severity'].upper()}: {alert['message']}")
        
        print("-" * 50)
    
    # サマリーを表示
    print("\n=== 会話サマリー ===")
    summary = analyzer.get_summary()
    print(f"総発言数: {summary['total_statements']}")
    print(f"話者別発言数: {summary['speakers']}")
    print(f"キーワード頻度: {summary['keyword_frequency']}")


if __name__ == '__main__':
    test_analyzer()
EOF < /dev/null