# config.py
class Config:
    ETHERSCAN_API_KEY = "YOUR_API_KEY"
    ETHERSCAN_V2_URL = "https://api.etherscan.io/v2/api"
    REQUEST_DELAY = 0.2  # 秒
    LOG_LEVEL = "INFO"
    
    # 过滤条件
    MIN_LIQUIDITY = 10000  # 最小流动性 $10K
    MIN_VOLUME = 30000     # 最小24h交易量 $30K
