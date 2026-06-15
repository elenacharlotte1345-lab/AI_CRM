import os

class Config:
    #日志文件
    LOG_FILE = "logfile/app.log"
    #如果不存在日志文件，则创建
    if not os.path.exists(LOG_FILE):
        os.makedirs(os.path.dirname(LOG_FILE))
    #日志文件最大字节数
    MAX_BYTES = 5*1024*1024
    #日志文件备份个数
    BACKUP_COUNT = 3
    #大模型类型
    LLM_TYPE ="qwen"
    #内存数据库路径
    MEMORY_DB_PATH = "data/memory.db"
    #SQL代理数据库路径
    SQL_AGENT_DB_PATH = "data/app.db"
    
    # ========== 修改这里：MySQL 配置 ==========
    # 数据库类型: mysql 或 sqlite
    DB_TYPE = "mysql"  # 改为 mysql
    
    # MySQL 配置（自己填）
    MYSQL_HOST = "localhost"  # 或 127.0.0.1
    MYSQL_PORT = 3306
    MYSQL_USER = "root"  # 你的 MySQL 用户名
    MYSQL_PASSWORD = ""  # 你的 MySQL 密码
    MYSQL_DATABASE = "medical_assistant"  # 数据库名称
    