from typing import Callable
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.prompt_loader import load_system_prompts, load_report_prompts
from utils.logger_handler import logger

@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    """工具调用监控中间件。

    为什么需要它：
    1. 统一记录工具调用日志，便于排查“为什么答错/为什么没走工具”；
    2. 在特定工具触发后写入上下文标记，驱动后续提示词动态切换。

    返回值说明：
        透传工具原始返回（ToolMessage 或 Command），不改变业务语义。
    """
    logger.info(f"[tool monitor]执行工具:{request.tool_call['name']}")
    logger.info(f"[tool monitor]传入参数：{request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")
        # 关键开关：
        # fill_context_for_report 被调用后，把 report 标记设为 True，
        # 后续 dynamic_prompt 中间件会读取该标记并切换到报告提示词。
        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True
        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}调用失败，原因：{str(e)}")
        raise e

@before_model
def log_before_model(
        state: AgentState,
        runtime: Runtime,
):
    """模型调用前日志中间件。

    作用：在真正调用模型前，记录消息数量和最后一条消息摘要，
    方便定位上下文过长、角色错乱、输入异常等问题。
    """
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")
    return None

@dynamic_prompt
def report_prompt_switch(request: ModelRequest):
    """动态提示词切换中间件。

    决策逻辑：
    - report=True  -> 使用报告生成提示词；
    - report=False -> 使用普通客服提示词。

    返回值说明：
        返回对应提示词文本字符串，供模型本轮推理使用。
    """
    is_report = request.runtime.context.get("report", False)
    if is_report:
        return load_report_prompts()

    return load_system_prompts()

