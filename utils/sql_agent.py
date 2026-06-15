import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from .llms import get_llm
from .config import Config
from .logger import LoggerManager
import pymysql

logger = LoggerManager.get_logger()

_sql_agent_instance = None

def get_db_uri():
    """根据配置获取数据库连接URI"""
    if Config.DB_TYPE == "mysql":
        # MySQL 连接格式
        # 需要先安装: pip install pymysql
        db_uri = f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}"
        logger.info(f"使用 MySQL 数据库: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}")
        return db_uri
    else:
        # SQLite 连接格式
        db_path = Config.SQL_AGENT_DB_PATH
        dir_path = os.path.dirname(db_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        db_uri = f"sqlite:///{db_path}"
        logger.info(f"使用 SQLite 数据库: {db_uri}")
        return db_uri

def init_mysql_database():
    """初始化 MySQL 数据库（如果不存在则创建）"""
    if Config.DB_TYPE != "mysql":
        return
    
    try:
        # 先连接到 MySQL 服务器（不指定数据库）
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {Config.MYSQL_DATABASE}")
        
        # 检查是否已有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if len(tables) == 0:
            logger.info("MySQL 数据库为空，开始初始化表结构...")
            # 获取 schema.sql 路径
            schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "schema_mysql.sql")
            
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                    # 分割并执行 SQL 语句
                    for statement in schema_sql.split(';'):
                        if statement.strip():
                            try:
                                cursor.execute(statement)
                            except Exception as e:
                                logger.warning(f"执行 SQL 语句失败: {str(e)[:100]}")
                    conn.commit()
                    logger.info("MySQL 数据库初始化完成")
            else:
                logger.warning(f"未找到 schema 文件: {schema_path}")
                # 使用默认初始化
                init_mysql_default_tables(cursor)
                conn.commit()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"MySQL 初始化失败: {str(e)}")
        raise

def init_mysql_default_tables(cursor):
    """默认创建 MySQL 表结构"""
    # 创建 users 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INT,
            city VARCHAR(50),
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # 创建 medical_records 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            diagnosis TEXT,
            symptoms TEXT,
            treatment TEXT,
            prescription TEXT,
            visit_date DATE NOT NULL,
            doctor_name VARCHAR(50),
            department VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_visit_date (visit_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # 创建 products 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2),
            category VARCHAR(50),
            stock INT DEFAULT 0,
            expiry_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_category (category)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # 插入示例数据
    cursor.executemany(
        "INSERT IGNORE INTO users (name, email, age, city, phone) VALUES (%s, %s, %s, %s, %s)",
        [
            ("张三", "zhangsan@example.com", 25, "北京", "13800000001"),
            ("李四", "lisi@example.com", 30, "上海", "13800000002"),
            ("王五", "wangwu@example.com", 35, "广州", "13800000003"),
        ]
    )
    
    cursor.executemany(
        "INSERT IGNORE INTO products (name, price, category, stock) VALUES (%s, %s, %s, %s)",
        [
            ("阿莫西林", 25.50, "抗生素", 100),
            ("布洛芬", 18.00, "止痛药", 200),
            ("二甲双胍", 35.00, "降糖药", 150),
        ]
    )
    
    logger.info("MySQL 默认表结构创建完成")

def get_sql_agent():
    global _sql_agent_instance
    if _sql_agent_instance is None:
        
        # 如果是 MySQL，先初始化数据库
        if Config.DB_TYPE == "mysql":
            init_mysql_database()
        
        db_uri = get_db_uri()
        
        # 创建 SQLDatabase 实例
        db = SQLDatabase.from_uri(db_uri)
        
        # 测试连接
        try:
            tables = db.get_usable_table_names()
            logger.info(f"成功连接到数据库，可用表: {tables}")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise

        llm_chat = get_llm(Config.LLM_TYPE)

        toolkit = SQLDatabaseToolkit(db=db, llm=llm_chat)

        agent = create_sql_agent(
            llm=llm_chat,
            toolkit=toolkit,
            agent_type="zero-shot-react-description",
            verbose=True,
            handle_parse_error=True
        )
        _sql_agent_instance = agent
        logger.info(f"SQL代理已创建")
    return _sql_agent_instance

def query_sql_agent(question: str) -> str:
    try:
        agent = get_sql_agent()
        logger.info(f"SQL代理查询: {question}")
        result = agent.invoke({"input": question})
        output = result.get("output", str(result))
        logger.info(f"SQL代理查询结果: {output}")
        return output
    except Exception as e:
        error_msg = f"SQL代理查询时发生错误: {str(e)}"
        logger.error(error_msg)
        return error_msg
'''
if __name__ == "__main__":
    print("测试 MySQL 连接...")
    answer = query_sql_agent("显示所有用户")
    print(f"SQL查询结果: {answer}")
'''