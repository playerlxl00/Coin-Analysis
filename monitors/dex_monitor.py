# monitors/dex_monitor.py
from dexscraper import DexScraper
from .etherscan_monitor import EtherscanMonitor
from analyzers.token_analyzer import TokenAnalyzer
import asyncio
from config import Config

class DexMonitor:
    def __init__(self, 
                 etherscan_monitor: EtherscanMonitor,
                 analyzer: TokenAnalyzer,
                 min_liquidity: float = 0):
        self.etherscan_monitor = etherscan_monitor
        self.analyzer = analyzer
        self.min_liquidity = min_liquidity
        
    async def analyze_new_pair(self, pair_data):
        """分析新交易对"""
        # 提取DexScreener数据
        dex_info = {
            'address': pair_data.base_token.address,
            'symbol': pair_data.base_token.symbol,
            'liquidity': pair_data.liquidity.usd,
            'volume_24h': getattr(pair_data.volume, 'h24', 0),
            'price': pair_data.price_data.usd,
            'pair_address': pair_data.pair_address,
            'created_at': pair_data.pair_created_at
        }
        
        print(f"\n🔍 发现新币: {dex_info['symbol']}")
        print(f"  流动性: ${dex_info['liquidity']:,.2f}")
        print(f"  24h交易量: ${dex_info['volume_24h']:,.2f}")
        
        # 基础过滤
        if dex_info['liquidity'] < self.min_liquidity:
            print(f"⏭️ 流动性不足，跳过")
            return
        
        # 查询Etherscan
        token_info = await self.etherscan_monitor.get_token_info(dex_info['address'])
        contract_info = await self.etherscan_monitor.get_contract_source(dex_info['address'])
        
        if not token_info:
            print(f"⚠️ Etherscan上暂无数据，可能为新部署合约")
            return
        
        # 使用你的分析器进行综合分析
        analysis_result = await self.analyzer.analyze_token(
            dex_data=dex_info,
            etherscan_data=token_info,
            contract_data=contract_info
        )
        
        # 输出分析结果
        self._print_analysis(analysis_result)
        
        # 根据决策采取行动
        if analysis_result['decision'] == 'ALERT':
            await self._send_alert(analysis_result)
    
    def _print_analysis(self, analysis: Dict):
        """打印分析结果"""
        print(f"\n📊 分析结果 [{analysis['token_symbol']}]:")
        print(f"  综合评分: {analysis['score']:.1f}/100")
        print(f"  决策: {analysis['decision']}")
        
        if analysis['reasons']:
            print("  原因:")
            for reason in analysis['reasons']:
                print(f"    • {reason}")
        
        if analysis.get('indicators'):
            print("  指标详情:")
            for key, value in analysis['indicators'].items():
                print(f"    • {key}: {value:.2f}")
    
    async def _send_alert(self, analysis: Dict):
        """发送警报 - 你可以自定义这里，比如发送到Telegram"""
        print(f"\n🚨 发现优质代币: {analysis['token_symbol']}")
        print(f"   地址: {analysis['token_address']}")
        print(f"   评分: {analysis['score']:.1f}")
        # 这里添加发送到Telegram、钉钉等的代码
        
    async def start(self):
        """启动监控"""
        scraper = DexScraper(debug=True)
        print("🚀 开始监控以太坊新币...")
        print(f"📋 使用自定义参数: {Config.SCORING_PARAMS}")
        print(f"🎯 评分阈值: {Config.SCORE_THRESHOLD}")
        
        async for pair in scraper.stream_pairs(chain_ids=[1]):
            asyncio.create_task(self.analyze_new_pair(pair))
