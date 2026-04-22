from abc import ABC, abstractmethod
from typing import Optional
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from utils.config_handler import rag_conf


class BaseModelFactory(ABC):
    """模型工厂抽象基类。

    统一约束：具体工厂都实现 generator()，返回可用模型实例。
    """
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    """聊天模型工厂：负责创建对话大模型实例。"""
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        # 模型名称来自配置，便于不同环境下切换模型而不改代码逻辑。
        return ChatTongyi(model=rag_conf["chat_model_name"])

class EmbeddingsFactory(BaseModelFactory):
    """向量模型工厂：负责创建文本嵌入模型实例。"""
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])

# 模块级单例对象：
# - chat_model 供 Agent / RAG 推理使用
# - embed_model 供向量化入库与检索使用
chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
