# monitors/etherscan_monitor.py
import aiohttp
from typing import Dict, Optional
from utils.rate_limiter import EtherscanRateLimiter
from utils.logger import default_logger

class EtherscanMonitor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.etherscan.io/v2/api"
        self.rate_limiter = EtherscanRateLimiter()
        self.logger = default_logger
        
    async def _make_request(self, params: Dict) -> Optional[Dict]:
        """带速率限制的请求"""
        # 构建URL（新版本的写法更规范）
        params['apikey'] = self.api_key
        
        async def fetch():
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"HTTP {response.status}: {await response.text()}")
                        return None
        
        return await self.rate_limiter.execute(fetch)
    
    async def get_token_info(self, token_address: str) -> Optional[Dict]:
        """获取代币信息"""
        params = {
            'chainid': 1,
            'module': 'token',
            'action': 'tokeninfo',
            'contractaddress': token_address
        }
        
        data = await self._make_request(params)
        
        if data and data.get('status') == '1' and data.get('result'):
            result = data['result'][0]
            self.logger.info(f"成功获取代币信息: {result.get('symbol')}")
            return {
                'address': token_address,
                'name': result.get('name'),
                'symbol': result.get('symbol'),
                'total_supply': result.get('totalSupply'),
                'decimals': result.get('divisor', '18'),
                'holders_count': result.get('holdersCount', 0)
            }
        else:
            self.logger.warning(f"获取代币信息失败: {token_address}")
            return None
    
    # ========== 保留旧版本的这个重要方法 ==========
    async def get_contract_source(self, token_address: str) -> Optional[Dict]:
        """获取合约源代码（保留这个重要方法）"""
        params = {
            'chainid': 1,
            'module': 'contract',
            'action': 'getsourcecode',
            'address': token_address
        }
        
        data = await self._make_request(params)
        
        if data and data.get('status') == '1' and data.get('result'):
            result = data['result'][0]
            self.logger.info(f"成功获取合约源码: {token_address}")
            return result
        else:
            self.logger.warning(f"获取合约源码失败: {token_address}")
            return None
