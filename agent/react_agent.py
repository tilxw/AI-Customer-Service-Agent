from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import rag_summarize, get_weather, get_user_location, get_user_id, get_current_month, fetch_external_data, fill_context_for_report
from agent.tools.middleware import monitor_tool, log_before_model,report_prompt_switch


class ReactAgent():
    """Agent 封装层。

    作用：把“模型 + 提示词 + 工具 + 中间件”装配成一个可流式执行的智能体，
    对外只暴露 execute_stream，简化上层 UI 的调用复杂度。
    """
    def __init__(self):
        # create_agent 是 LangChain 的组装入口：
        # - model：大语言模型
        # - system_prompt：基础行为规则
        # - tools：可调用的外部能力
        # - middleware：调用前后插入的监控/动态行为
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize, fill_context_for_report, get_weather,
                   get_user_location, get_user_id, get_current_month, fetch_external_data],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self, query: str):
        """流式执行用户请求并逐段返回文本。

        参数：
            query: 用户自然语言问题。
        返回：
            生成器；每次 yield 一段 assistant 输出文本，供前端实时渲染。
        """
        # 统一转换为消息格式，便于 Agent 按对话范式推理。
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }
        # report 初始值为 False；
        # 若后续调用 fill_context_for_report，中间件会把它改为 True，
        # 从而触发报告提示词切换。
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content and latest_message.type == "ai":
                # 返回值语义：输出当前最新文本片段（清理首尾空白并补换行）。
                yield latest_message.content.strip() + "\n"

if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
