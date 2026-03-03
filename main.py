# main.py
import asyncio
from config import Config
from monitors.etherscan_monitor import EtherscanMonitor
from monitors.dex_monitor import DexMonitor

async def main():
    # 初始化组件
    etherscan = EtherscanMonitor(
        api_key=Config.ETHERSCAN_API_KEY,
        delay=Config.REQUEST_DELAY
    )
    
    monitor = DexMonitor(
        etherscan_monitor=etherscan,
        min_liquidity=Config.MIN_LIQUIDITY
    )
    
    # 启动监控
    await monitor.start()

if __name__ == "__main__":
    asyncio.run(main())
