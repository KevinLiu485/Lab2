import streamlit as st
import os
import json
from datetime import datetime
from api import GPT_MODELS
import concurrent.futures

HISTORY_FILE = "profile/chat_history.json"  # 聊天历史文件名
PREFERENCES_FILE = "profile/preferences.json"  # 偏好设置文件名

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
                # print(f"init_model_list() read preferences: {preferences}")
                # 根据偏好设置的值对模型进行排序
                state.model_list = sorted(GPT_MODELS, key=lambda x: preferences[x.get_model_name()], reverse=True)
            except json.JSONDecodeError:
                print("Error decoding JSON. Initializing empty preferences.")
    if "model_list" not in state:
        # 如果没有偏好设置文件，则使用默认顺序
        state.model_list = GPT_MODELS
    # print(f"init_model_list(): {state.model_list}")

# 初始化会话状态
if "initialized" not in state:
    state.initialized = True

    # 从 PREFERENCES_FILE 初始化侧栏列表顺序
    init_model_list()

    # 从HISTORY_FILE初始化聊天历史
    init_history_lists()

    state.front_model = state.model_list[0]  # 默认模型

    state.summaries = {gpt: "No summary yet. Click to view history" for gpt in state.model_list}  # 用于存储摘要

    state.uploaded_file = None  # 用于存储上传的文件

    state.preferences = { gpt.get_model_name(): 0 for gpt in state.model_list }     # 用于存储用户偏好

def render_sidebar():
    """
    渲染侧栏中的摘要按钮
    :return: None
    """
    for model in state.model_list:

        # st.sidebar.markdown(f"## **{model.get_display_name()}**")
        # 为每个模型创建一个按钮
        if st.sidebar.button(f"## **{model.get_display_name()}** \n{state.summaries[model]}", key=model.get_model_name()):
            record_preferences()
            # 如果按钮被点击，更新当前显示的模型
            state.front_model = model
            st.rerun()

def render_chat_history():   
    """
    渲染当前模型的聊天历史
    :return: None
    """ 
    for message in state.history_lists[state.front_model.get_model_name()]:
        # 系统标注
        if message["role"] == "system":
            st.markdown(message["content"])
        else:
            # 正常对话数据
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def make_summary(response: str):
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
    return summary

def record_preferences():
    """
    读取 state.front_model 以记录用户的偏好
    """
    # 记录用户的偏好设置
    state.preferences[state.front_model.get_model_name()] += 1
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
    prompt = st.chat_input(f"Ask {state.front_model.get_display_name()} anything...")

    if prompt:
        record_preferences()  # 记录用户的偏好设置

        # 显示用户的输入
        with st.chat_message("user"):
            st.markdown(prompt)

        # 如果上传了图片，显示图片
        uploaded_file = state.uploaded_file
        if uploaded_file:
            with st.chat_message("user"):
                st.image(uploaded_file, caption="Uploaded Image")

        # 定义一个函数来调用模型的 `chat` 方法
        def call_model_chat(model, prompt, uploaded_file):
            # print(f"{model.get_model_name()} called")
            return model, model.chat(prompt, file_content=uploaded_file.getvalue() if uploaded_file else None)

        # 使用多线程调用所有模型的 `chat` 方法
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 提交任务
            future_to_model = {
                executor.submit(call_model_chat, model, prompt, uploaded_file): model
                for model in state.model_list
            }

            # 收集结果
            for future in concurrent.futures.as_completed(future_to_model):
                model, response = future.result()

                model_name = model.get_model_name()
                # print(f"{model_name} responsed")

                # 显示模型的响应
                if model_name == state.front_model.get_model_name():
                    with st.chat_message("assistant"):
                        st.markdown(response)

                # 更新该模型的对话历史
                state.history_lists[model_name].append({"role": "user", "content": prompt})
                if uploaded_file:
                    state.history_lists[model_name].append({"role": "user", "content": f"[Image] {uploaded_file.name}"})
                state.history_lists[model_name].append({"role": "assistant", "content": response})

                state.summaries[model] = make_summary(response)

        save_history()
        save_preferences()

        st.rerun()

def render_file_uploader():
    state.uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])


# 渲染流程

# 页面标题
st.title(state.front_model.get_display_name())

# 侧栏标题
st.sidebar.title("SUMMARIES")
st.sidebar.divider()

render_chat_history()

render_file_uploader()

render_chat_input()

render_sidebar()