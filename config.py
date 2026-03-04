# config.py
class Config:
    # ========== API配置 ==========
    ETHERSCAN_API_KEY = "YOUR_API_KEY"
    ETHERSCAN_V2_URL = "https://api.etherscan.io/v2/api"
    REQUEST_DELAY = 0.2  # 请求延迟
    
    # ========== 日志配置 ==========
    LOG_LEVEL = "INFO"
    
    # ========== 你的自定义参数 ==========
    # 基础过滤参数
    MIN_LIQUIDITY = 10000        # 最小流动性 ($)
    MIN_VOLUME_24H = 30000       # 最小24h交易量 ($)
    MAX_HOLDER_CONCENTRATION = 20  # 前10持有者最大占比 (%)
    
    # 自定义算法参数（你可以随意修改这些）
    SCORING_PARAMS = {
        'liquidity_weight': 0.3,      # 流动性权重
        'volume_weight': 0.25,         # 交易量权重  
        'holder_weight': 0.2,           # 持有者分布权重
        'age_weight': 0.15,             # 代币年龄权重
        'verified_bonus': 0.1,          # 合约验证加分
    }
    
    # 判断阈值
    SCORE_THRESHOLD = 60  # 总分100，超过60分才报警
    
    # 自定义规则（你可以添加任意规则）
    CUSTOM_RULES = {
        'avoid_high_concentration': True,     # 避免高度集中
        'prefer_verified_contracts': True,    # 偏好已验证合约
        'min_holders': 100,                    # 最少持有者数量
        'max_renounced_percentage': 5,          # 最大放弃权限占比？
    }

SCORING_PARAMS = {
    'liquidity_weight': 0.4,      # 你觉得流动性最重要
    'volume_weight': 0.1,          # 交易量不重要
    'holder_weight': 0.3,          # 持有者分布很重要
    'age_weight': 0.1,             
    'verified_bonus': 0.1,
}
