import streamlit as st
import os
import json
from datetime import datetime
from api import GPT_MODELS

HISTORY_FILE = "chat_history.json"  # 聊天历史文件名
PREFERENCES_FILE = "preferences.json"  # 偏好设置文件名

state = st.session_state

def get_string_timestamp():
    """
    获取当前时间戳
    :return: 当前时间戳
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_history_lists():
    """
    读取 HISTORY_FILE 初始化 state.history_lists
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                state.history_lists = json.load(f)
                # 为每个模型添加一个时间戳
                for model in state.model_list:
                    state.history_lists[model.get_model_name()].append({"role": "system", "content": f"**Chat history loaded. Below is chat starts at {get_string_timestamp()}**"})
            except json.JSONDecodeError:
                print("Error decoding JSON. Initializing empty history.")
    if "history_lists" not in state:
        state.history_lists = {gpt.get_model_name(): [{"role": "system", "content": f"**Below is chat starts at {get_string_timestamp()}**"}] for gpt in state.model_list}

def init_model_list():
    """
    根据 PREFERENCES_FILE 初始化侧栏列表顺序
    """
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, "r") as f:
            try:
                preferences = json.load(f)
                print(f"init_model_list() read preferences: {preferences}")
                # 根据偏好设置的值对模型进行排序
                state.model_list = sorted(GPT_MODELS, key=lambda x: preferences[x.get_model_name()], reverse=True)
            except json.JSONDecodeError:
                print("Error decoding JSON. Initializing empty preferences.")
    if "model_list" not in state:
        # 如果没有偏好设置文件，则使用默认顺序
        state.model_list = GPT_MODELS
    print(f"init_model_list(): {state.model_list}")

# 初始化会话状态
if "initialized" not in state:
    state.initialized = True

    # 从 PREFERENCES_FILE 初始化侧栏列表顺序
    init_model_list()

    # 从HISTORY_FILE初始化聊天历史
    init_history_lists()

    state.front_model_name = state.model_list[0].get_model_name()  # 默认模型
    state.summaries = [
        {"model": gpt.get_model_name(), "summary": "Click to view history"} for gpt in state.model_list
    ]  # 用于存储摘要

    state.uploaded_file = None  # 用于存储上传的文件

    state.preferences = { gpt.get_model_name(): 0 for gpt in state.model_list } 

    print(f"init(): {state.preferences}")
    # 用于存储用户偏好


# 页面标题
st.title(state.front_model_name)

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
            record_preferences()
            # 如果按钮被点击，更新当前显示的模型
            state.front_model_name = model_name

def render_chat_history():   
    """
    渲染当前模型的聊天历史
    :return: None
    """ 
    for message in state.history_lists[state.front_model_name]:
        # 系统标注
        if message["role"] == "system":
            st.markdown(message["content"])
        else:
            # 正常对话数据
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

    # summary = summary.ljust(20)  # 填充空格到至少 20 个字符
    return {"model": model_name, "summary": summary}

def record_preferences():
    """
    读取 state.front_model_name 以记录用户的偏好
    """
    # 记录用户的偏好设置
    state.preferences[state.front_model_name] += 1
    print(f"record_preferences() {state.preferences}")

def save_preferences():
    """
    保存用户的偏好设置到json文件
    """
    with open(PREFERENCES_FILE, "w") as f:
        json.dump(state.preferences, f, ensure_ascii=False, indent=4)

def save_history():
    """
    保存聊天历史到json文件
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(state.history_lists, f, ensure_ascii=False, indent=4)

def render_chat_input():
    """
    渲染聊天输入框和图片上传功能
    """
    prompt = st.chat_input(f"Ask {state.front_model_name}")

    # 如果用户输入了文本或上传了图片
    if prompt:
        record_preferences()  # 记录用户的偏好设置
        #     # 显示用户的输入
        #     if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        uploaded_file = state.uploaded_file
        # 如果上传了图片，显示图片
        if uploaded_file:
            with st.chat_message("user"):
                st.image(uploaded_file, caption="Uploaded Image")

        # 遍历所有模型，获取响应
        summaries = []
        for model in state.model_list:
            model_name = model.get_model_name()

            # 调用模型的 chat 方法，传递文本和图片
            response = model.chat(prompt, file_content=uploaded_file.getvalue() if uploaded_file else None)

            if model_name == state.front_model_name:
                with st.chat_message("assistant"):
                    st.markdown(response)

            # 更新该模型的对话历史
            state.history_lists[model_name].append({"role": "user", "content": prompt})
            if uploaded_file:
                state.history_lists[model_name].append({"role": "user", "content": f"[Image uploaded: {uploaded_file.name}]"})
            state.history_lists[model_name].append({"role": "assistant", "content": response})

            # 保存摘要
            summaries.append(make_summary(model_name, response))

        # 将摘要保存到会话状态
        state.summaries = summaries
        # 保存聊天历史到文件
        save_history()
        save_preferences()

def render_file_uploader():
    state.uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])


# 正式渲染流程
render_chat_history()

render_chat_input()

render_file_uploader()

render_sidebar()
