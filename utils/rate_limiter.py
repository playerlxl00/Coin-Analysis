# utils/rate_limiter.py
import asyncio
import time
from typing import Optional

class RateLimiter:
    """
    速率限制器 - 控制API请求频率
    """
    def __init__(self, max_calls: int = 5, period: float = 1.0):
        """
        初始化速率限制器
        
        Args:
            max_calls: 在指定时间段内允许的最大请求数
            period: 时间段（秒）
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []  # 记录每次调用的时间戳
        
    async def acquire(self) -> None:
        """
        获取请求许可，如果超过限制则等待
        """
        now = time.time()
        
        # 清理过期的调用记录
        self.calls = [t for t in self.calls if now - t < self.period]
        
        if len(self.calls) >= self.max_calls:
            # 计算需要等待的时间
            wait_time = self.period - (now - self.calls[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # 记录本次调用
        self.calls.append(time.time())
    
    async def execute(self, func, *args, **kwargs):
        """
        执行函数，自动进行速率限制
        """
        await self.acquire()
        return await func(*args, **kwargs)

class EtherscanRateLimiter(RateLimiter):
    """
    Etherscan专用的速率限制器
    Etherscan免费版API限制：5 calls/sec
    """
    def __init__(self):
        super().__init__(max_calls=5, period=1.0)
        
class DexScreenerRateLimiter(RateLimiter):
    """
    DexScreener专用的速率限制器
    """
    def __init__(self):
        # DexScreener限制较宽松，但保守起见设为 30 calls/sec
        super().__init__(max_calls=30, period=1.0)
