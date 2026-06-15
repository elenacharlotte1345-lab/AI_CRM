from langchain.tools import tool
from .logger import LoggerManager
from .rag_medical import rag_medical_query
from .baidu_search import baidu_search as baidu_search_func
from .sql_agent import query_sql_agent
logger = LoggerManager.get_logger()


#定义一个函数，用于构建并返回当前agent可用的工具列表。

def get_tools():

    #使用@tool装饰器注册一个工具,该工具接收用户问题,并返回知识库相关内容。
    #该工具接收用户问题,并返回知识库相关内容。

    @tool("rag_medical",description="利用医学知识库回答用户问题。")

    def rag_medical(query: str) -> str:

        return rag_medical_query(query)
    
    #使用@tool装饰器注册第二个工具,该工具接收用户问题,并返回最新资讯。

    @tool("tavily_search",description="根据用户想要获取最新资讯的问题进行网络检索。")

    def tavily_search(query: str) -> str:

        return baidu_search_func(query)
    
    #使用@tool装饰器注册第三个工具,该工具接收用户问题,并返回SQL查询语句。

    @tool("sql_agent",description="根据用户问题生成SQL查询语句。")

    def sql_agent(query: str) -> str:

        return query_sql_agent(query)
    #将三个工具添加到tools列表中
    tools = [
        rag_medical,
        tavily_search,
        sql_agent
    ]
    #记录日志
    logger.info(f"当前agent可用的工具列表为:{tools}")
    #返回工具列表
    return tools
