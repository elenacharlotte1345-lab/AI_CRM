# utils/asr.py
import os
import dashscope
from dashscope import MultiModalConversation
from dotenv import load_dotenv, find_dotenv
from .logger import LoggerManager

# 加载 .env 文件（从 utils/ 或根目录查找）
load_dotenv("./.env")
logger = LoggerManager.get_logger()

# 设置 API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
if not dashscope.api_key:
    raise ValueError("❌ DASHSCOPE_API_KEY not found in .env")

def asr_from_wav(file_path: str) -> str:
    """
    使用 Qwen3-ASR-Flash 模型将本地音频文件转为文字。
    """
    if not os.path.exists(file_path):
        logger.error(f"音频文件不存在: {file_path}")
        return ""

    logger.info(f"开始 ASR 识别: {file_path}")
    try:
        messages = [{
            "role": "user",
            "content": [{"audio": file_path}]
        }]
        response = MultiModalConversation.call(
            model="qwen3-asr-flash",
            messages=messages
        )
        
        # 提取 content（可能是 list 或 str）
        content = response.output.choices[0].message.content
        
        # 统一提取为字符串
        if isinstance(content, list):
            # 常见格式：[{"text": "识别结果"}] 或 ["识别结果"]
            if content and isinstance(content[0], dict):
                text = content[0].get("text", "")
            else:
                text = " ".join(str(item) for item in content)
        elif isinstance(content, str):
            text = content
        else:
            raise Exception(f"未知的 content 类型: {type(content)}")
        
        text = text.strip()
        if not text:
            raise Exception("未识别到文本")
        
        logger.info(f"ASR 识别成功: {text[:50]}...")
        return text
    except Exception as e:
        error_msg = f"ASR 错误: {str(e)}"
        logger.error(error_msg)
        return ""

# 简单测试
if __name__ == "__main__":
    test_file = "test1.wav"
    if os.path.exists(test_file):
        result = asr_from_wav(test_file)
        print(f"识别结果: '{result}'")
    else:
        print(f"请将测试文件 {test_file} 放在当前目录下")