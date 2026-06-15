import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
#从当前包中导入LoggerManager类,用于获取日志记录器实例，以输出运行和调试信息。
from .logger import LoggerManager

load_dotenv("./.env")
#获取全局日志实例，用于在工具加载和调用过程中记录日志。
logger = LoggerManager.get_logger()

# #定义一个字典，用于存储不同类型的LLM配置信息。
MODEL_CONFIGS = {
    "qwen": {
        "base_url": os.getenv("QWEN_BASE_URL"),
        "api_key": os.getenv("DASHSCOPE_API_KEY"),
        "model": os.getenv("QWEN_MODEL"),
        "embedding_model":os.getenv("QWEN_EMBEDDING_MODEL")
    }
}

#定义默认的LLM类型为"qwen"
DEFAULT_LLM_TYPE = "qwen"

DEFAULT_TEMPERATURE = 0

class LLMInitializationError(Exception):
    '''自定义异常类用于llm初始化错误。'''
    pass


def initialize_llm(llm_type:str = DEFAULT_LLM_TYPE) ->tuple[ChatOpenAI, OpenAIEmbeddings]:
    '''初始化LLM，返回ChatOpenAI和OpenAIEmbeddings实例。'''
    try:
        if llm_type not in MODEL_CONFIGS:
            raise ValueError(f"不支持的LLM类型: {llm_type}.可用的类型: {list(MODEL_CONFIGS.keys())}")
        config = MODEL_CONFIGS[llm_type]
        llm_chat = ChatOpenAI(
            model=config["model"],
            temperature=DEFAULT_TEMPERATURE,
            base_url=config["base_url"],
            api_key=config["api_key"],
            timeout=30,
            max_retries=2
        )
        llm_embedding = OpenAIEmbeddings(
            base_url=config["base_url"],
            api_key=config["api_key"],
            model=config["embedding_model"]
        )
        logger.info(f"成功初始化LLM: {llm_type}")
        return llm_chat, llm_embedding
    
    except ValueError as ve:

        logger.error(f"LLM配置错误: {str(ve)}")
        raise LLMInitializationError(f"初始化LLM失败: {str(ve)}")
    except Exception as e:
        logger.error(f"初始化LLM失败: {str(e)}")
        raise LLMInitializationError(f"初始化LLM失败: {str(e)}")
    

def get_llm(llm_type:str = DEFAULT_LLM_TYPE) -> ChatOpenAI:
    '''获取LLM实例的封装函数，提供默认值和错误处理。
    
    Args:
        llm_type (str): LLM类型. 
    
    Returns:
        ChatOpenAI: LLM实例.
    '''
    try:
        llm_chat, _ = initialize_llm(llm_type)  # 只取 ChatOpenAI 部分
        return llm_chat
    except LLMInitializationError as e:
        logger.warning(f"使用默认配置重试：{str(e)}")
        
        if llm_type != DEFAULT_LLM_TYPE:
            # 修复这里：只取 ChatOpenAI 部分
            llm_chat, _ = initialize_llm(DEFAULT_LLM_TYPE)
            return llm_chat
        raise

'''
if __name__ == "__main__":
    try:
        # 直接调用 initialize_llm 获取两个对象
        llm_chat, llm_embedding = initialize_llm("qwen")
        print("LLM 初始化成功")
        
        # 或者单独获取 ChatOpenAI
        llm_chat_only = get_llm("qwen")
        
        # 测试无效类型
        llm_invalid = get_llm("invalid_type")
    except LLMInitializationError as e:
        logger.error(f"初始化LLM失败: {str(e)}")
'''