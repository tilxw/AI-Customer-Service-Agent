import os,hashlib
from utils.logger_handler import logger

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,TextLoader

"""文件处理工具模块。

用途：
1. 计算文件 MD5（用于向量库增量加载去重）；
2. 按后缀筛选目录文件；
3. 提供 txt/pdf 文档加载能力，统一返回 LangChain Document 列表。
"""

def get_file_md5_hex(filepath:str):         # 获取文件的md5的十六进制字符串
    """计算文件 MD5 十六进制字符串。

    参数：
        filepath: 目标文件绝对路径。
    返回：
        成功返回 md5 字符串；失败返回 None。
    """
    if not os.path.exists(filepath):
        logger.error(f"[MD5计算]文件{filepath}不存在")
        return
    if not os.path.isfile(filepath):
        logger.error(f"[MD5计算]路径{filepath}不是文件")
        return

    md5_obj = hashlib.md5()
    chunk_size=4096     # 4KB分片，避免文件过大爆内存
    try:
            with open(filepath, "rb")as f:  # 必须二进制读取
                while chunk:=f.read(chunk_size):
                    md5_obj.update(chunk)

            md5_hex=md5_obj.hexdigest()
            return md5_hex
    except Exception as  e:
        logger.error(f"计算文件{filepath}md5失败，{str(e)}")
        return None

def listdir_with_allowed_type(path:str,allowed_types:tuple[str]):   # 返回文件夹内的文件列表（允许的文件后缀）
    """列出目录下指定后缀的文件路径。"""
    files= []
    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return allowed_types

    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path,f))
    return tuple(files)

def pdf_loader(filepath:str,passwd=None)->list[Document]:
    """读取 PDF 并返回 Document 列表。"""

    return PyPDFLoader(filepath,passwd).load()

def txt_loader(filepath:str)->list[Document]:
    """读取 TXT 并返回 Document 列表。"""

    return TextLoader(filepath,encoding="utf-8").load()
