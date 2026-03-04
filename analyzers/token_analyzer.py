# analyzers/token_analyzer.py
from typing import Dict, Any, Optional
from datetime import datetime

class TokenAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化分析器，传入你的自定义参数
        """
        self.scoring_params = config.get('SCORING_PARAMS', {})
        self.custom_rules = config.get('CUSTOM_RULES', {})
        self.score_threshold = config.get('SCORE_THRESHOLD', 60)
        
    async def analyze_token(self, 
                           dex_data: Dict[str, Any], 
                           etherscan_data: Dict[str, Any],
                           contract_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        综合分析代币，返回评分和决策
        """
        # 1. 提取所有需要的数据
        analysis = {
            'token_address': dex_data.get('address'),
            'token_symbol': dex_data.get('symbol'),
            'timestamp': datetime.now().isoformat(),
            
            # 原始数据
            'raw_data': {
                'liquidity': dex_data.get('liquidity', 0),
                'volume_24h': dex_data.get('volume_24h', 0),
                'price': dex_data.get('price', 0),
                'open_price': dex_data.get('open_price', 0),  # 新增：开盘价
                'holders_count': etherscan_data.get('holders_count', 0),
                'total_supply': etherscan_data.get('total_supply', 0),
                'is_verified': contract_data.get('SourceCode') is not None if contract_data else False,
            },
            
            # 计算指标（这里会调用你问的两个方法）
            'indicators': {},
            
            # 最终评分和决策
            'score': 0,
            'decision': 'IGNORE',
            'reasons': []
        }
        
        # 2. 计算各种指标 - 这里调用你问的第一个方法
        indicators = self._calculate_indicators(analysis['raw_data'])
        analysis['indicators'] = indicators
        
        # 3. 应用你的自定义规则 - 这里调用你问的第二个方法
        rule_check = self._apply_custom_rules(analysis['raw_data'], indicators)
        analysis['rule_violations'] = rule_check['violations']
        
        if rule_check['should_ignore']:
            analysis['reasons'] = rule_check['violations']
            analysis['decision'] = 'IGNORE'
            return analysis
        
        # 4. 计算综合评分
        score = self._calculate_score(indicators, analysis['raw_data'])
        analysis['score'] = score
        
        # 5. 根据阈值做出决策
        if score >= self.score_threshold:
            analysis['decision'] = 'ALERT'
            analysis['reasons'].append(f"评分达到阈值: {score:.1f}/{self.score_threshold}")
        else:
            analysis['decision'] = 'IGNORE'
            analysis['reasons'].append(f"评分不足: {score:.1f}/{self.score_threshold}")
        
        return analysis
    
    # ========== 这是你问的第一个方法：计算指标 ==========
    def _calculate_indicators(self, raw_data: Dict) -> Dict[str, float]:
        """
        计算各种技术指标 - 这是你可以自由发挥的地方！
        """
        indicators = {}
        
        # 1. 持有者集中度
        if raw_data.get('holders_count', 0) > 0:
            indicators['holder_concentration'] = min(100, 10000 / raw_data['holders_count'])
        else:
            indicators['holder_concentration'] = 100
        
        # 2. 流动性深度指标
        liquidity = raw_data.get('liquidity', 0)
        indicators['liquidity_score'] = min(100, liquidity / 1000)
        
        # 3. 交易活跃度
        volume = raw_data.get('volume_24h', 0)
        indicators['volume_score'] = min(100, volume / 3000)
        
        # ==== 你问的新增指标：价格相对于开盘的涨幅 ====
        if raw_data.get('price') and raw_data.get('open_price') and raw_data['open_price'] > 0:
            indicators['price_increase'] = (raw_data['price'] / raw_data['open_price'] - 1) * 100
        else:
            indicators['price_increase'] = 0
        
        # ==== 你问的新增指标：交易量/流动性比 ====
        if raw_data.get('volume_24h') and raw_data.get('liquidity') and raw_data['liquidity'] > 0:
            indicators['volume_liquidity_ratio'] = raw_data['volume_24h'] / raw_data['liquidity']
        else:
            indicators['volume_liquidity_ratio'] = 0
        
        return indicators
    
    # ========== 这是你问的第二个方法：应用规则 ==========
    def _apply_custom_rules(self, raw_data: Dict, indicators: Dict) -> Dict:
        """
        应用你的自定义规则 - 这是规则引擎的核心
        """
        violations = []
        should_ignore = False
        
        # 规则1：避免高度集中
        if self.custom_rules.get('avoid_high_concentration'):
            if indicators.get('holder_concentration', 0) > 80:
                violations.append("高度集中风险")
                should_ignore = True
        
        # 规则2：偏好已验证合约
        if self.custom_rules.get('prefer_verified_contracts'):
            if not raw_data.get('is_verified', False):
                violations.append("合约未验证")
        
        # ==== 你问的新增规则：限制涨幅 ====
        if 'max_price_increase' in self.custom_rules:
            max_increase = self.custom_rules['max_price_increase']
            if indicators.get('price_increase', 0) > max_increase:
                violations.append(f"涨幅过大: {indicators['price_increase']:.0f}% > {max_increase}%")
                should_ignore = True
        
        # ==== 你问的新增规则：最小交易量/流动性比 ====
        if 'min_volume_liquidity_ratio' in self.custom_rules:
            min_ratio = self.custom_rules['min_volume_liquidity_ratio']
            if indicators.get('volume_liquidity_ratio', 0) < min_ratio:
                violations.append(f"交易量/流动性比过低: {indicators['volume_liquidity_ratio']:.2f} < {min_ratio}")
                should_ignore = True
        
        return {
            'violations': violations,
            'should_ignore': should_ignore
        }
    
    def _calculate_score(self, indicators: Dict, raw_data: Dict) -> float:
        """
        计算综合评分 - 使用你设置的权重
        """
        score = 0
        weights = self.scoring_params
        
        # 流动性得分
        if 'liquidity_score' in indicators:
            score += indicators['liquidity_score'] * weights.get('liquidity_weight', 0.3)
        
        # 交易量得分  
        if 'volume_score' in indicators:
            score += indicators['volume_score'] * weights.get('volume_weight', 0.25)
        
        # 持有者分布得分
        if 'holder_concentration' in indicators:
            holder_score = 100 - indicators['holder_concentration']
            score += holder_score * weights.get('holder_weight', 0.2)
        
        # 合约验证加分
        if raw_data.get('is_verified', False):
            score += 100 * weights.get('verified_bonus', 0.1)
        
        return min(100, score)
