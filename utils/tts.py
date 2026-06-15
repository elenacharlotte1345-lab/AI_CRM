# utils/tts.py
import os
import asyncio
import edge_tts
from .logger import LoggerManager

logger = LoggerManager.get_logger()

# 项目根目录下的 temp_audio 文件夹
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_AUDIO_DIR = os.path.join(BASE_DIR, "temp_audio")

def ensure_temp_dir():
    if not os.path.exists(TEMP_AUDIO_DIR):
        os.makedirs(TEMP_AUDIO_DIR)
        logger.info(f"创建临时音频目录: {TEMP_AUDIO_DIR}")

async def _async_tts(text: str, voice: str, output_file: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def text_to_speech(text: str, voice: str = "zh-CN-XiaoxiaoNeural", filename: str = None) -> str:
    """
    将文本转为语音，保存到 temp_audio/ 目录。
    返回保存的文件路径。
    """
    ensure_temp_dir()
    if filename is None:
        import hashlib
        hash_name = hashlib.md5(text.encode()).hexdigest()[:12]
        filename = f"response_{hash_name}.mp3"
    output_path = os.path.join(TEMP_AUDIO_DIR, filename)
    
    try:
        asyncio.run(_async_tts(text, voice, output_path))
        logger.info(f"TTS 生成成功: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"TTS 失败: {e}")
        return ""

# 简单测试
if __name__ == "__main__":
    text = "你好，这是语音合成的测试。"
    path = text_to_speech(text)
    print(f"生成文件: {path}")