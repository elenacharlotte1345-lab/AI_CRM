# agent.py
import os
from dotenv import load_dotenv
load_dotenv("utils/.env")

from langchain.agents import create_agent
from utils.memory_sqlite import get_sqlite_saver
from utils.config import Config
from utils.llms import get_llm
from utils.tools import get_tools
from utils.models import Context, ResponseFormat, SYSTEM_PROMPT
from utils.logger import LoggerManager
from utils.asr import asr_from_wav
from utils.tts import text_to_speech

logger = LoggerManager.get_logger()

# 初始化 LLM、工具、记忆
llm_chat = get_llm(Config.LLM_TYPE)
tools = get_tools()
checkpointer = get_sqlite_saver()

# 创建 Agent
agent = create_agent(
    model=llm_chat,
    system_prompt=SYSTEM_PROMPT,
    tools=tools,
    context_schema=Context,
    response_format=ResponseFormat,
    checkpointer=checkpointer
)

def interactive_mode(thread_id: str = "1", user_id: str = "1"):
    """交互式对话：每轮可选择文本输入或上传语音文件"""
    config = {"configurable": {"thread_id": thread_id}}
    print(f"\n📞 进入交互模式 | 线程ID: {thread_id} | 用户ID: {user_id}")
    print("=" * 60)
    print("每轮对话可选择输入方式：")
    print("  1. 输入文本")
    print("  2. 上传语音文件 (.wav)")
    print("  0. 退出对话")
    print("=" * 60)

    while True:
        print("\n请选择输入方式 (1/2/0): ", end="")
        choice = input().strip()

        if choice == "0":
            print("👋 退出对话，再见！")
            break

        user_content = None

        if choice == "1":
            print("📝 请输入文本: ", end="")
            user_content = input().strip()
            if not user_content:
                print("❌ 文本不能为空，请重新选择输入方式。")
                continue

        elif choice == "2":
            print("🎤 请输入 .wav 文件路径: ", end="")
            wav_path = input().strip()
            if not os.path.exists(wav_path):
                print(f"❌ 文件不存在: {wav_path}")
                continue
            user_content = asr_from_wav(wav_path)
            if not user_content:
                print("❌ 语音识别失败，请重试或换用文本输入。")
                continue
            print(f"📝 识别结果: {user_content}")

        else:
            print("❌ 无效选项，请输入 1、2 或 0。")
            continue

        print("🤖 AI 正在思考...")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_content}]},
            config=config,
            context=Context(user_id=user_id)
        )
        structured = response.get("structured_response")

        if structured:
            print(f"\n💬 回答：{structured.answer}")
            if structured.tool_used:
                print(f"🔧 使用工具：{structured.tool_used}")
            if structured.medical_content:
                print(f"📚 医学知识：{structured.medical_content}")
            
            # 美化搜索结果的输出
            if structured.search_results:
                print("🌐 搜索结果：")
                results = structured.search_results
                # 统一转换成列表
                if isinstance(results, dict):
                    if "results" in results:
                        items = results["results"]
                    else:
                        items = [results]
                elif isinstance(results, list):
                    items = results
                else:
                    items = [{"snippet": str(results)}]
                
                for idx, item in enumerate(items, 1):
                    title = item.get("title", "无标题")
                    snippet = item.get("snippet", item.get("content", "无内容"))
                    link = item.get("link", item.get("url", ""))
                    print(f"  [{idx}] {title}")
                    # 摘要缩进，过长可截断（可选）
                    if len(snippet) > 200:
                        snippet = snippet[:200] + "..."
                    print(f"      摘要：{snippet}")
                    if link:
                        print(f"      链接：{link}")
            
            if structured.sql_result:
                print(f"🗄️ SQL结果：{structured.sql_result}")
            if structured.confidence is not None:
                print(f"📊 置信度：{structured.confidence}")
        else:
            print(f"⚠️ Agent 返回非结构化结果: {response}")

        print("\n🔊 是否将回答转为语音？(y/n, 默认n): ", end="")
        if input().strip().lower() == 'y':
            answer_text = structured.answer if structured else str(response)
            audio_path = text_to_speech(answer_text)
            if audio_path:
                print(f"✅ 语音已保存至: {audio_path}")
            else:
                print("❌ TTS 生成失败")

    print("对话结束")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI CRM 语音/文本交互")
    parser.add_argument("--thread", type=str, default="1", help="线程ID (默认: 1)")
    parser.add_argument("--user", type=str, default="1", help="用户ID (默认: 1)")
    args = parser.parse_args()

    interactive_mode(thread_id=args.thread, user_id=args.user)