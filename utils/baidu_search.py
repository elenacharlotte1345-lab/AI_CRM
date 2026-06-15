import os
import requests
from typing import Optional, Dict
from .logger import LoggerManager
from dotenv import load_dotenv

load_dotenv("./.env")
logger = LoggerManager.get_logger()

# 百度搜索配置
BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
if not BAIDU_API_KEY:
    logger.warning("BAIDU_API_KEY 环境变量未设置，百度搜索可能无法正常工作。")

# 百度搜索 API 地址
BAIDU_SEARCH_URL = "https://qianfan.baidubce.com/v2/ai_search/web_search"


class BaiduSearchClient:
    """百度搜索客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def search(self, query: str, max_results: int = 5, search_recency: Optional[str] = None) -> Dict:
        """
        执行百度搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大返回结果数（网页类型最大50）
            search_recency: 时间筛选，可选值: 'week', 'month', 'semiyear', 'year'
        
        Returns:
            搜索结果字典
        """
        # 构建请求体
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": query[:72]  # 限制72个字符
                }
            ],
            "search_source": "baidu_search_v2",
            "resource_type_filter": [
                {"type": "web", "top_k": min(max_results, 50)},
                {"type": "video", "top_k": 0},
                {"type": "image", "top_k": 0}
            ]
        }
        
        # 添加时间筛选
        if search_recency:
            payload["search_recency_filter"] = search_recency
        
        try:
            response = requests.post(BAIDU_SEARCH_URL, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"百度搜索请求失败: {e}")
            raise


_client: Optional[BaiduSearchClient] = None


def get_baidu_client() -> BaiduSearchClient:
    """获取百度搜索客户端单例"""
    global _client
    if _client is None:
        if not BAIDU_API_KEY:
            raise ValueError("BAIDU_API_KEY 环境变量未设置，请先设置该变量以使用百度搜索")
        _client = BaiduSearchClient(api_key=BAIDU_API_KEY)
        logger.info("BaiduSearchClient 客户端初始化成功。")
    return _client


def baidu_search(query: str, max_results: int = 5, recency_filter: Optional[str] = None) -> str:
    """
    百度搜索函数
    
    Args:
        query: 搜索关键词
        max_results: 最大返回结果数（默认5，最大50）
        recency_filter: 时间筛选，可选值: 'week', 'month', 'semiyear', 'year'
    
    Returns:
        格式化的搜索结果字符串
    """
    try:
        client = get_baidu_client()
        logger.info(f"正在使用百度搜索: {query}")
        
        response = client.search(query, max_results=max_results, search_recency=recency_filter)
        
        # 检查错误
        if response.get("code"):
            error_msg = f"百度搜索API错误: {response.get('message', '未知错误')}"
            logger.error(error_msg)
            return error_msg
        
        # 获取搜索结果
        references = response.get("references", [])
        
        if not references:
            logger.info(f"搜索 '{query}' 未找到相关结果")
            return "未找到相关结果。"
        
        # 格式化结果
        formatted = []
        for i, ref in enumerate(references[:max_results], 1):
            title = ref.get("title", "无标题")
            url = ref.get("url", "")
            content = ref.get("content", "").strip()
            
            # 限制摘要长度
            if len(content) > 300:
                content = content[:300] + "..."
            
            # 添加来源网站信息
            website = ref.get("website", "")
            site_info = f"来源：{website}" if website else ""
            
            formatted.append(f"{i}. {title}\n摘要：{content}\n链接：{url}\n{site_info}\n")
        
        result_text = "\n".join(formatted)
        logger.info(f"搜索完成，共找到 {len(references)} 条结果，返回 {len(formatted)} 条。")
        return result_text
        
    except requests.exceptions.Timeout:
        error_msg = "百度搜索请求超时，请稍后重试。"
        logger.error(error_msg)
        return error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "网络连接失败，请检查网络设置。"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"搜索时发生错误: {str(e)}"
        logger.error(error_msg)
        return error_msg


# 为了兼容原有代码，保留原函数名作为别名
def tavily_search(query: str, max_results: int = 5) -> str:
    """兼容原有函数名的包装函数"""
    return baidu_search(query, max_results)

'''
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = "今天南阳天气如何？"
    print("测试百度搜索结果：")
    print(baidu_search(query, max_results=2))
'''