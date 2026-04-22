from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from model.factory import chat_model
from utils.prompt_loader import load_rag_prompts
from rag.vector_store import VectorStoreService
from langchain_core.prompts import PromptTemplate

def print_prompt(prompt):
    """调试辅助函数：打印当前提示词内容。"""
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt

class RagSummarizeService(object):
    """RAG 总结服务。

    核心职责：
    1. 从向量库检索与问题相关的参考资料；
    2. 把“用户问题 + 检索上下文”送入提示词链路；
    3. 返回模型生成的中文总结文本。
    """
    def __init__(self):
        # 初始化检索组件
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        # 读取并编译 RAG 提示词模板
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        """构建可执行链路：Prompt -> Model -> 字符串解析。"""
        #chain = self.prompt_template | print_prompt | self.model |StrOutputParser()
        chain = self.prompt_template | self.model |StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> list[Document]:
        """检索与 query 相关的文档片段列表。"""
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        """执行一次完整 RAG 总结。

        参数：
            query: 用户问题或检索词。
        返回：
            基于参考资料生成的总结文本。
        """

        context_docs = self.retriever_docs(query)
        context = ""
        counter = 0
        # 把多条检索结果拼接成统一上下文字符串，交给提示词模板消费。
        for doc in context_docs:
            counter += 1
            context += f"[参考资料{counter}]:参考资料：{doc.page_content} | 参考元数据: {doc.metadata}\n"

        # 返回值语义：模型最终生成的纯文本答案。
        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )

if __name__ == '__main__':
    rag = RagSummarizeService()

    print(rag.rag_summarize("小户型适合哪些扫地机器人"))
