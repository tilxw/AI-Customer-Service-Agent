import time

import streamlit as st
from agent.react_agent import ReactAgent


st.title("智扫通机器人智能客服")
st.divider()

# 将 Agent 放入 session_state 的原因：
# Streamlit 每次交互都会重新执行脚本；若不缓存，Agent 会被重复创建，
# 不仅浪费资源，也会让对话上下文管理更混乱。
if "agent" not in  st.session_state:
    st.session_state["agent"] = ReactAgent()

# 历史消息同样要放在 session_state 中，才能在页面重跑后继续显示聊天记录。
if "message" not in st.session_state:
    st.session_state["message"] = []

# 页面重绘时，先把历史消息完整回放，保证用户看到的是连续会话而不是“丢上下文”。
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    # 先展示并缓存用户输入，再进入模型推理，保证“所见即所得”。
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []
    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator, cache_list):
            """把流式结果同时用于“展示”和“缓存”。

            为什么要双写：
            - 直接展示：让用户实时看到回答在生成；
            - 同步缓存：回答结束后可落到历史消息，支持下一轮对话继续引用。
            """
            for chunk in generator:
                cache_list.append(chunk)

                # 逐字符输出主要为了更自然的打字机效果，降低“整段突兀出现”的体验割裂感。
                for char in chunk:
                    time.sleep(0.01)
                    yield char

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        # execute_stream 是增量输出，这里取最后一个 chunk 作为最终落库文本。
        # 返回值语义：保存 assistant 最终回复，供后续页面回放与多轮对话上下文使用。
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        # 触发一次重跑，让新消息以“历史消息”身份稳定渲染到页面上。
        st.rerun()
