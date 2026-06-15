import os
from langgraph.checkpoint.sqlite import SqliteSaver
from .config import Config
from .logger import LoggerManager

logger = LoggerManager().get_logger()

def ensure_db_dir(db_path: str):
    dir_path = os.path.dirname(db_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path,exist_ok=True)
        logger.info(f"创建数据库目录: {dir_path}")

_sqlite_saver_instance = None

def get_sqlite_saver() -> SqliteSaver:
    global _sqlite_saver_instance
    if _sqlite_saver_instance is None:
       db_path = Config.MEMORY_DB_PATH
       ensure_db_dir(db_path)
       logger.info(f"初始化sqlite saver, 数据库路径: {db_path}")
       import sqlite3
       #创建数据库连接
       conn = sqlite3.connect(db_path, check_same_thread=False)
       #设置WAL模式
       conn.execute('PRAGMA journal_mode=WAL;')
       #创建SqliteSaver实例
       _sqlite_saver_instance = SqliteSaver(conn)
    return _sqlite_saver_instance

def clear_memory():
    db_path = Config.MEMORY_DB_PATH
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info(f"已清除内存数据库: {db_path}")
        global _sqlite_saver_instance
        _sqlite_saver_instance = None
    else:
        logger.info(f"内存数据库不存在，无需清除。")

if __name__ == "__main__":
    saver = get_sqlite_saver()
    print(f"sqlite saver初始化成功: {saver}")
    import asyncio
    async def test():
        checkpoint = await saver.aput(config={},checkpoint={},metadata={},new_versions={})
        print(f"检查点创建: {checkpoint}")
    asyncio.run(test())
