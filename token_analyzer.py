# analyzers/token_analyzer.py
from typing import Dict, Any, Optional
import time
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
                'holders_count': etherscan_data.get('holders_count', 0),
                'total_supply': etherscan_data.get('total_supply', 0),
                'is_verified': contract_data.get('SourceCode') is not None if contract_data else False,
            },
            
            # 计算指标
            'indicators': {},
            
            # 最终评分和决策
            'score': 0,
            'decision': 'IGNORE',
            'reasons': []
        }
        
        # 2. 计算各种指标（你可以自定义这里的算法）
        indicators = self._calculate_indicators(analysis['raw_data'])
        analysis['indicators'] = indicators
        
        # 3. 应用你的自定义规则
        rule_check = self._apply_custom_rules(analysis['raw_data'], indicators)
        analysis['rule_violations'] = rule_check['violations']
        
        if rule_check['should_ignore']:
            analysis['reasons'] = rule_check['violations']
            analysis['decision'] = 'IGNORE'
            return analysis
        
        # 4. 计算综合评分（你可以自定义这里的权重）
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
    
    def _calculate_indicators(self, raw_data: Dict) -> Dict[str, float]:
        """
        计算各种技术指标 - 这是你可以自由发挥的地方！
        """
        indicators = {}
        
        # 1. 持有者集中度
        if raw_data.get('holders_count', 0) > 0:
            # 这里简化了，实际可以从Etherscan获取前10持有者占比
            indicators['holder_concentration'] = min(100, 10000 / raw_data['holders_count'])
        else:
            indicators['holder_concentration'] = 100
        
        # 2. 流动性深度指标
        liquidity = raw_data.get('liquidity', 0)
        indicators['liquidity_score'] = min(100, liquidity / 1000)  # 每$1000得1分
        
        # 3. 交易活跃度
        volume = raw_data.get('volume_24h', 0)
        indicators['volume_score'] = min(100, volume / 3000)  # 每$3000得1分
        
        # 4. 流动性/市值比（如果知道市值的话）
        # 你可以添加更多自定义指标
        
        # 5. 你的自定义算法可以写在这里！
        # 例如：计算价格波动性、交易频次等
        
        return indicators
    
    def _apply_custom_rules(self, raw_data: Dict, indicators: Dict) -> Dict:
        """
        应用你的自定义规则 - 这是规则引擎的核心
        """
        violations = []
        should_ignore = False
        
        # 规则1：避免高度集中
        if self.custom_rules.get('avoid_high_concentration'):
            if indicators.get('holder_concentration', 0) > 80:  # 前10持有者占80%以上
                violations.append("高度集中风险")
                should_ignore = True
        
        # 规则2：偏好已验证合约
        if self.custom_rules.get('prefer_verified_contracts'):
            if not raw_data.get('is_verified', False):
                violations.append("合约未验证")
                # 你可以决定是否因为未验证就忽略
                # should_ignore = True  # 如果严格要求验证
        
        # 规则3：最小持有者数量
        min_holders = self.custom_rules.get('min_holders', 0)
        if min_holders > 0 and raw_data.get('holders_count', 0) < min_holders:
            violations.append(f"持有者数量不足: {raw_data.get('holders_count', 0)}/{min_holders}")
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
        
        # 持有者分布得分（集中度越低越好）
        if 'holder_concentration' in indicators:
            holder_score = 100 - indicators['holder_concentration']
            score += holder_score * weights.get('holder_weight', 0.2)
        
        # 合约验证加分
        if raw_data.get('is_verified', False):
            score += 100 * weights.get('verified_bonus', 0.1)
        
        return min(100, score)  # 确保不超过100分
