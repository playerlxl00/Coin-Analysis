# main.py
import asyncio
from config import Config
from monitors.etherscan_monitor import EtherscanMonitor
from monitors.dex_monitor import DexMonitor
from analyzers.token_analyzer import TokenAnalyzer

async def main():
    # 初始化Etherscan监控
    etherscan = EtherscanMonitor(
        api_key=Config.ETHERSCAN_API_KEY,
        delay=Config.REQUEST_DELAY
    )
    
    # 初始化你的自定义分析器
    analyzer = TokenAnalyzer({
        'SCORING_PARAMS': Config.SCORING_PARAMS,
        'CUSTOM_RULES': Config.CUSTOM_RULES,
        'SCORE_THRESHOLD': Config.SCORE_THRESHOLD
    })
    
    # 初始化Dex监控，传入你的分析器
    monitor = DexMonitor(
        etherscan_monitor=etherscan,
        analyzer=analyzer,
        min_liquidity=Config.MIN_LIQUIDITY
    )
    
    # 启动监控
    await monitor.start()

if __name__ == "__main__":
    asyncio.run(main())
