"""
UI 样式模块：集中管理 Streamlit 聊天应用的所有样式和组件。

包含：
- CSS 样式定义
- 消息气泡渲染函数
- 样式初始化函数
"""

import streamlit as st


# ==================== 样式常量 ====================
# Claude 风格配色方案
USER_MESSAGE_BG = "#D3D3D3"      # 用户消息背景（灰色）
ASSISTANT_MESSAGE_BG = "#F5F5F5" # 助手消息背景（极浅灰）
TEXT_COLOR = "#000000"           # 文字颜色（黑色）
BORDER_RADIUS = "18px"           # 气泡圆角
INPUT_BORDER_RADIUS = "12px"     # 输入框圆角


def init_page_styles():
    """初始化页面样式（在 app_aigaiban.py 最顶部调用一次）。
    
    作用：注入全局 CSS，美化所有消息气泡和输入栏。
    """
    st.markdown(
        f"""
        <style>
            /* ==================== 消息容器样式 ==================== */
            .message-container {{
                display: flex;
                margin: 12px 0;
                align-items: flex-start;
            }}
            
            .user-message-container {{
                justify-content: flex-end;
            }}
            
            .assistant-message-container {{
                justify-content: flex-start;
            }}
            
            /* ==================== 消息气泡样式 ==================== */
            .message-bubble {{
                padding: 12px 16px;
                border-radius: {BORDER_RADIUS};
                max-width: 70%;
                word-wrap: break-word;
                line-height: 1.5;
                font-size: 15px;
            }}
            
            .user-message-bubble {{
                background-color: {USER_MESSAGE_BG};
                color: {TEXT_COLOR};
                border-bottom-right-radius: 4px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            
            .assistant-message-bubble {{
                background-color: {ASSISTANT_MESSAGE_BG};
                color: {TEXT_COLOR};
                border-bottom-left-radius: 4px;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            }}
            
            /* ==================== 输入框美化 ==================== */
            .stChatInputContainer {{
                border-radius: {INPUT_BORDER_RADIUS};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                border: 1px solid #e0e0e0;
            }}
            
            /* 输入框内部 */
            .stChatInputContainer input {{
                border-radius: {INPUT_BORDER_RADIUS};
            }}
            
            /* ==================== 代码块美化 ==================== */
            .message-bubble pre {{
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #e0e0e0;
                overflow-x: auto;
            }}
            
            .message-bubble code {{
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }}
            
            /* ==================== 列表美化 ==================== */
            .message-bubble ul {{
                margin: 8px 0;
                padding-left: 20px;
            }}
            
            .message-bubble li {{
                margin: 4px 0;
            }}
            
            /* ==================== 标题美化 ==================== */
            .message-bubble h1, 
            .message-bubble h2, 
            .message-bubble h3 {{
                margin: 8px 0;
                font-weight: 600;
            }}
            
            /* ==================== 加粗文本 ==================== */
            .message-bubble strong {{
                font-weight: 600;
                color: #1a1a1a;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_message_bubble(role: str, content: str):
    """渲染单条消息气泡（无头像，仅对齐）。
    
    参数：
        role: "user" 或 "assistant"
        content: 消息文本内容
    """
    import html
    
    # 关键：转义内容，防止 < > 等特殊字符破坏 HTML 结构
    escaped_content = html.escape(content)
    
    # 选择样式
    if role == "user":
        bubble_class = "user-message-bubble"
        container_class = "user-message-container"
    else:  # assistant
        bubble_class = "assistant-message-bubble"
        container_class = "assistant-message-container"
    
    # 关键：使用紧凑 HTML（无缩进），防止被当成代码块
    html_content = f'<div class="message-container {container_class}"><div class="message-bubble {bubble_class}">{escaped_content}</div></div>'
    
    st.markdown(html_content, unsafe_allow_html=True)

