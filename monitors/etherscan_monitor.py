# monitors/etherscan_monitor.py
import aiohttp
import asyncio
import time
from typing import Dict, Any, Optional

class EtherscanMonitor:
    def __init__(self, api_key: str, delay: float = 0.2):
        self.api_key = api_key
        self.delay = delay
        self.last_request_time = 0
        
    async def _make_request(self, url: str) -> Optional[Dict]:
        """带速率限制的请求"""
        now = time.time()
        if now - self.last_request_time < self.delay:
            await asyncio.sleep(self.delay - (now - self.last_request_time))
            
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                self.last_request_time = time.time()
                return await response.json()
    
    async def get_token_info(self, token_address: str) -> Optional[Dict]:
        """获取代币基本信息"""
        url = f"https://api.etherscan.io/v2/api?chainid=1&module=token&action=tokeninfo&contractaddress={token_address}&apikey={self.api_key}"
        data = await self._make_request(url)
        
        if data and data.get('status') == '1' and data.get('result'):
            result = data['result'][0]
            return {
                'address': token_address,
                'name': result.get('name'),
                'symbol': result.get('symbol'),
                'total_supply': result.get('totalSupply'),
                'decimals': result.get('divisor', '18'),
                'holders_count': result.get('holdersCount', 0)
            }
        return None
    
    async def get_contract_source(self, token_address: str) -> Optional[Dict]:
        """获取合约源代码"""
        url = f"https://api.etherscan.io/v2/api?chainid=1&module=contract&action=getsourcecode&address={token_address}&apikey={self.api_key}"
        data = await self._make_request(url)
        
        if data and data.get('status') == '1' and data.get('result'):
            return data['result'][0]
        return None
