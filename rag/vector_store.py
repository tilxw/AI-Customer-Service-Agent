import os
from langchain_core.documents import Document
from utils.path_tool import get_abs_path
from utils.config_handler import chroma_conf
from langchain_chroma import Chroma
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.logger_handler import logger
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex


class VectorStoreService:
    """向量库服务层。

    负责两件核心事情：
    1. 初始化 Chroma 向量库与文本切片器；
    2. 把本地知识文件加载、切片后写入向量库，并通过 MD5 去重避免重复入库。
    """
    def __init__(self):
        # Chroma 持久化目录来自配置，重启进程后仍可复用已写入向量数据。
        self.vector_store = Chroma(
            collection_name = chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )

        # 文本切片器：把长文档切成可嵌入、可检索的小块。
        # chunk_overlap 的价值是保留相邻片段上下文，降低“语义断裂”。
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):
        """返回检索器对象。

        返回值说明：
            retriever 会按配置 k 值返回最相关的若干文本片段。
        """
        return self.vector_store.as_retriever(search_kwargs = {"k": chroma_conf["k"]})

    def load_document(self):
        """扫描知识目录并增量写入向量库。

        处理流程（输入 -> 处理 -> 输出）：
        - 输入：data_path 下允许类型的文件；
        - 处理：MD5 去重 -> 文档读取 -> 分片 -> 向量入库；
        - 输出：新增文档写入 Chroma，重复文档跳过并记录日志。
        """


        def check_md5_hex(md5_for_check: str):
            """检查 MD5 是否已存在于记录文件中（用于去重）。"""
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False

            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True

                return False
        def save_md5_hex(md5_for_check: str):
            """将新文件 MD5 追加保存，作为下次增量加载依据。"""
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str):
            """根据文件后缀选择对应加载器。"""
            if read_path.endswith("txt"):
                return txt_loader(read_path)

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)

            return []

        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )

        for path in allowed_files_path:
            md5_hex = get_file_md5_hex(path)

            # 若 MD5 已登记，说明内容已入库，直接跳过提升加载效率。
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在知识库内，跳过")
                continue
            try:
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue

                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没有有效内容，跳过")
                    continue

                # 关键落库动作：把切片后的文档写入向量库，供后续 retriever 检索。
                self.vector_store.add_documents(split_document)
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path} 内容加载成功")
            except Exception as e:
                logger.error(f"[加载知识库]{path}加载失败：{str(e)}", exc_info=True)
                continue

if __name__ == '__main__':
    vs = VectorStoreService()

    vs.load_document()

    retriever = vs.get_retriever()
    res = retriever.invoke("迷路")
    for doc in res:
        print(doc.page_content)
        print("-"*20)
