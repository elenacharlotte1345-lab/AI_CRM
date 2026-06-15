import os
from pathlib import Path
from typing import List, Optional

from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .logger import LoggerManager

from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from .llms import MODEL_CONFIGS,DEFAULT_LLM_TYPE


logger = LoggerManager.get_logger()

from dotenv import load_dotenv
load_dotenv("./.env")

LAW_DOC_PATH = Path(__file__).parent.parent / "data" / "medical_content.txt"
CHROMA_PERSIST_DIR = Path(__file__).parent / "chroma_medical"
COLLECTION_NAME = "medical_content"

_vector_store: Optional[Chroma] = None

def get_embedding_model():
    config = MODEL_CONFIGS.get(DEFAULT_LLM_TYPE, MODEL_CONFIGS["qwen"])
    model_name = config["embedding_model"]
    api_key = config["api_key"]           
    return DashScopeEmbeddings(
        model=model_name,        
        dashscope_api_key=api_key      
    )


def load_and_split_documents() -> List[Document]:
    if not LAW_DOC_PATH.exists():
        raise FileNotFoundError(f"医学知识文件不存在: {LAW_DOC_PATH}")
    loader = TextLoader(str(LAW_DOC_PATH), encoding="utf-8")
    documents = loader.load()
    
    # 方法1：按序号手动分割（最精确）
    content = documents[0].page_content
    # 按 "数字+点号+空格" 分割，如 "1. " "2. " "10. "
    import re
    chunks = re.split(r'\n(?=\d+\.\s)', content)
    
    splits = []
    for i, chunk in enumerate(chunks):
        if chunk.strip():  # 跳过空内容
            splits.append(Document(page_content=chunk.strip(), metadata={"source": str(LAW_DOC_PATH), "index": i}))
    
    logger.info(f"医学知识条文加载完成，共{len(chunks)}条独立知识")
    return splits

def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    logger.info("正在初始化医学知识条文向量存储（Chroma）")
    splits = load_and_split_documents()
    embeddings_model = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings_model,
        persist_directory=str(CHROMA_PERSIST_DIR),
        collection_name=COLLECTION_NAME
    )
    _vector_store = vector_store
    logger.info("医学知识条文向量存储初始化完成，持久化目录{CHROMA_PERSIST_DIR}")
    return vector_store
       
def retrieve_medical(query: str, k: int = 3) -> List[Document]:
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return results

def format_docs(docs: List[Document]) -> str:
    formatted = []
    for i, doc in enumerate(docs,1):
        content = doc.page_content.strip()
        formatted.append(f"第{i}条：{content}")
    return "\n".join(formatted)
    
def rag_medical_query(query: str) -> str:
    try:
        docs = retrieve_medical(query, k = 3)
        if not docs:
            return "没有找到相关医学知识"
        return format_docs(docs)
    except Exception as e:
        logger.error(f"查询相关医学知识失败: {e}")
        return f"查询相关医学知识失败{str(e)}"
'''  
if __name__ == "__main__":
    test_query = "骨质疏松的定义，临床表现为？"
    print(f"测试查询: {test_query}")
    result = rag_medical_query(test_query)
    print(f"检索结果：\n{result}")
'''