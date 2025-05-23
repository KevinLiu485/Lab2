import streamlit as st
import os
import json
from api import GPT_MODELS

HISTORY_FILE = "chat_history.json"  # 聊天历史文件名

state = st.session_state

# 初始化会话状态
if "initialized" not in state:
    state.initialized = True

    # 从HISTORY_FILE初始化聊天历史
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                state.history_lists = json.load(f)
            except json.JSONDecodeError:
                print("Error decoding JSON. Initializing empty history.")
    if "history_lists" not in state:
        state.history_lists = {gpt.get_model_name(): [] for gpt in GPT_MODELS}

    state.front_model_name = GPT_MODELS[0].get_model_name()  # 默认模型
    # state.summaries = []  # 用于存储摘要
    state.summaries = [
        {"model": gpt.get_model_name(), "summary": "Click to view history"} for gpt in GPT_MODELS
    ]  # 用于存储摘要

# 页面标题
st.title("Simple Chat")

# 侧栏标题
st.sidebar.title("Summaries")
st.sidebar.markdown("***")

def render_sidebar():
    """
    渲染侧栏中的摘要按钮
    :return: None
    """
    for summary in state.summaries:
        model_name = summary["model"]
        summary_text = summary["summary"]

        st.sidebar.markdown(f"## **{model_name}**")
        # 为每个模型创建一个按钮
        if st.sidebar.button(f"{summary_text}", key=model_name):
            # 如果按钮被点击，更新当前显示的模型
            state.front_model_name = model_name
            # rerend()

def render_chat_history():   
    """
    渲染当前模型的聊天历史
    :return: None
    """ 
    for message in state.history_lists[state.front_model_name]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def make_summary(model_name: str, response: str):
    """
    创建摘要
    :param model_name: 模型名称
    :param summary: 摘要内容
    :return: 摘要字典
    """
    if len(response) > 50:
        summary = response[:50] + "..."
    else:
        summary = response
    summary = summary.replace("\n", " ")  # 替换换行符为空格
    summary = summary.ljust(20)  # 填充空格到至少 20 个字符
    return {"model": model_name, "summary": summary}

def save_history():
    """
    保存聊天历史到json文件
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(state.history_lists, f, ensure_ascii=False, indent=4)

def render_chat_input():
    # 输入框，用于输入用户消息
    if prompt := st.chat_input(f"Ask {state.front_model_name}"):
        with st.chat_message("user"):
            st.markdown(prompt)

        # 遍历所有模型，获取响应
        summaries = []
        for model in GPT_MODELS:
            model_name = model.get_model_name()
            response = model.chat(prompt)  # 调用模型的 chat 方法获取响应

            if model_name == state.front_model_name:
                with st.chat_message("assistant"):
                    st.markdown(response)

            # 更新该模型的对话历史
            state.history_lists[model_name].append({"role": "user", "content": prompt})
            state.history_lists[model_name].append({"role": "assistant", "content": response})

            # 保存摘要（这里假设摘要是响应的前50个字符）
            summaries.append(make_summary(model_name, response))

        # 将摘要保存到会话状态
        state.summaries = summaries
        # 保存聊天历史到文件
        save_history()
        


# 正式渲染流程
render_chat_input()

render_sidebar()

render_chat_history()