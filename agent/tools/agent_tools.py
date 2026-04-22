import os.path
from utils.logger_handler import logger
from langchain_core.tools import tool
from rag.rag_service import  RagSummarizeService
import random
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path

"""Agent 工具集合。

设计思路：
1. 用 @tool 暴露给 LangChain Agent 调用；
2. 把“知识检索、环境信息、用户信息、外部记录读取”拆成独立能力；
3. 通过 fill_context_for_report 工具触发中间件上下文开关，联动提示词切换。
"""

user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010",]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", ]
rag = RagSummarizeService()
# 外部报告数据缓存（进程级）：
# 首次读取 CSV 后常驻内存，避免每次工具调用都重复 I/O。
external_data = {}
@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    """RAG 检索总结工具。

    参数：
        query: 贴合用户问题的检索词。
    返回：
        基于知识库与提示词总结后的中文文本。
    """
    return rag.rag_summarize(query)

@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    """天气信息工具（示例实现）。

    参数：
        city: 城市名。
    返回：
        面向对话的天气描述字符串。
    """
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度50%，南风1级，AQI21，最近6小时降雨概率极低"

@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location() -> str:
    """获取用户所在城市（示例实现，随机返回）。"""
    return  random.choice(["深圳", "合肥", "杭州"])

@tool(description="获取用户的ID，以纯字符串形式返回")
def get_user_id() -> str:
    """获取用户 ID（示例实现，随机返回）。"""
    return random.choice(user_ids)

@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() -> str:
    """获取当前月份（示例实现，随机返回）。"""
    return random.choice(month_arr)

def generate_external_data():
    """按需加载并解析外部 CSV 数据到 external_data。

    为什么懒加载：
    - 启动时不阻塞；
    - 仅在报告相关查询真正发生时才读取文件。
    返回值说明：
    - 本函数通过修改全局 external_data 生效，不直接返回数据。
    """
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")
        # 第 1 行为表头，因此从第 2 行开始读取业务数据。
        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")

                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }



@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回， 如果未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    """按 user_id + month 获取外部使用记录。

    参数：
        user_id: 用户唯一标识（字符串）。
        month: 月份（YYYY-MM）。
    返回：
        命中时返回结构化记录；未命中时返回空字符串。
    """
    generate_external_data()
    try:
        return external_data[user_id][month]
    except KeyError:
        # 这里返回空字符串是工具协议的一部分：让 Agent 感知“未命中”，再决定后续动作。
        logger.warning(f"[fetch_external_data]未能检索到用户：{user_id}在{month}的使用记录数据")
        return ""

@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    """报告场景上下文触发器。

    注意：
    真正的“上下文写入”发生在 middleware.monitor_tool 中。
    本工具主要承担“显式触发点”的角色，便于 Agent 严格遵循固定流程。
    """
    return "fill_context_for_report已调用"
