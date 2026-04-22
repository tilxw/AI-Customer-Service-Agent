import time

import streamlit as st
from agent.react_agent import ReactAgent
from utils.ui_styles import init_page_styles, render_message_bubble


# ==================== 页面初始化 ====================
init_page_styles()

st.title("扫地机器人AI客服")
st.divider()

# ==================== 会话状态初始化 ====================
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

# ==================== 消息回放 ====================
for message in st.session_state["message"]:
    render_message_bubble(message["role"], message["content"])

prompt = st.chat_input()

# ==================== 用户输入处理 ====================
if prompt:
    # 先展示并缓存用户输入
    render_message_bubble("user", prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []
    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator, cache_list):
            """把流式结果同时用于"展示"和"缓存"。"""
            for chunk in generator:
                cache_list.append(chunk)
                for char in chunk:
                    time.sleep(0.01)
                    yield char

        # 流式输出到气泡中
        placeholder = st.empty()
        current_text = ""
        
        for char in capture(res_stream, response_messages):
            current_text += char
            # 调用转义和渲染的函数
            import html
            escaped_text = html.escape(current_text)
            # 紧凑HTML，无缩进，无div污染
            placeholder.markdown(
                f'<div class="message-container assistant-message-container"><div class="message-bubble assistant-message-bubble">{escaped_text}</div></div>',
                unsafe_allow_html=True,
            )
        
        # 保存原始内容（未转义）到历史，因为显示时会自动转义
        st.session_state["message"].append({"role": "assistant", "content": current_text})
        st.rerun()
