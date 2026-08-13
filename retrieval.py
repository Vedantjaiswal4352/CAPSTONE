# retrieval.py -> Llamaindex and query retrieval module
# initialize_retrieval, execute_query

import os
import asyncio
import logging
from llama_index.core import Document, VectorStoreIndex
# from llama_index.llms.openai import OpenAI
# from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from data import load_csv
from dotenv import load_dotenv
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
logger = logging.getLogger("capstone_retrieval")

query_engine = None
index_initialized = False

def build_index():
    """Build and cache vector index with error handling"""
    global query_engine, index_initialized
    try:
        logger.info("Started vector build...")
        df = load_csv()
        docs = [Document(text=row["text"]) for _, row in df.iterrows()]
        logger.info(f"Creating embeddings for {len(docs)} documents...")

        llm = HuggingFaceInferenceAPI(
            model_name="Qwen/Qwen2.5-72B-Instruct", 
            token=HF_TOKEN,
            temperature=0.1
        )
        embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
        logger.info("Vector index built successfully.")
        query_engine = index.as_query_engine(llm=llm, similarity_top_k = 2)
        index_initialized = True
        return query_engine
    except Exception as e:
        logger.error(f"Error building index: {str(e)}")
        index_initialized = False
        return None

def initialize_retrieval():
    """Initialize retrieval system on startup"""
    global query_engine,index_initialized
    try:
        logger.info(f"Initializing retrieval system")
        query_engine = build_index()
        if query_engine:
            logger.info(f"Retrieval system initialized successfully.")
        else:
            logger.error(f"Retrieval system initialization failed - queries may fail.")
            index_initialized = False
    except Exception as e:
        logger.error(f"Failed to initialize retrieval: {str(e)}")
        index_initialized = False

async def execute_query(question: str)-> str:
    """Execute a query using the query engine."""
    if not index_initialized or query_engine is None:
        raise Exception("Query engine not initialized.")
    try:
        response = query_engine.query(question)
        print(str(response))
        return str(response)
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise RuntimeError(f"Query execution failed: {str(e)}") from e