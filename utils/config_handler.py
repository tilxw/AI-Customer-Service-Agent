import yaml
from utils.path_tool import get_abs_path

"""配置读取模块。

职责：
1. 把不同业务域（rag/chroma/prompts/agent）的 yml 配置读取为字典；
2. 在模块加载时初始化为全局配置对象，供其他模块直接导入使用。
"""


def load_rag_config(config_path: str = get_abs_path("config/rag.yml"), encoding: str = "utf-8"):
    """读取 RAG 模型相关配置。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml"), encoding: str = "utf-8"):
    """读取向量库与切片相关配置。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml"), encoding: str = "utf-8"):
    """读取提示词文件路径配置。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding: str = "utf-8"):
    """读取 Agent 业务相关配置（如外部数据路径）。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# 模块级配置对象：
# 导入方可直接使用 rag_conf/chroma_conf/agent_conf/prompts_conf，
# 避免每次调用都重复读取磁盘文件。
rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
agent_conf = load_agent_config()
prompts_conf = load_prompts_config()

if __name__ == '__main__':
    print(rag_conf["chat_model_name"])  # 输出对应配置
