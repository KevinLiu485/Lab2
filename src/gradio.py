import gradio as gr
from api import GPT_MODELS

# 使用GPT_MODELS中的模型名称作为键的字典
history_lists = {gpt.get_model_name(): [] for gpt in GPT_MODELS}

def get_favored_history() -> list:
    """
    获取默认呈现的聊天历史
    :return: 默认呈现的聊天历史
    """
    return history_lists[GPT_MODELS[0].get_model_name()]

# 清除对话历史
def clear_history():
    # 清理 history_lists 中的所有模型的历史记录
    for model in GPT_MODELS:
        history_lists[model] = []

    return [], gr.Dataset(samples=[])

# 与模型对话并返回摘要和完整内容
def chat(message: str):
    if not message:
        return "", get_favored_history(), gr.Dataset(samples=[])

    # 添加用户消息到聊天历史
    # history += [{"role": "user", "content": message}]
    summaries = []
    user_message = [{"role": "user", "content": message}]

    # 遍历所有模型，获取回复
    for model in GPT_MODELS:
        model_name = model.get_model_name()
        response = model.chat(message)

        print(f"Model: {model_name}, Response: {response}")

        # 更新模型的历史
        history_lists[model_name] += user_message
        history_lists[model_name] += [{"role": "assistant", "content": response}]

        # 生成摘要（这里假设摘要是回复的前50个字符）
        summaries.append({
            "model": model_name,
            "summary": response[:50],
            # "full_content": response
        })

    # print(f"History: {history}")
    summaries = gr.Dataset(samples=[[s["model"], s["summary"]] for s in summaries])

    # 返回完整历史记录和新的 Dataset 对象
    return "", get_favored_history(), summaries

def update_chatbot(selected):
    if not selected:
        print("No selection made.")
        return get_favored_history()
    
    # 获取选中的摘要
    model_name, _summary = selected

    history = history_lists[model_name]
    print(f"Selected Model: {model_name}, History: {history}")

    return history

# 更新聊天历史
# def update_chatbot(selected, chatbot_history):
#     if not selected:
#         return chatbot_history  # 如果没有选中任何摘要，返回原历史记录

#     # 获取选中的完整内容
#     model_name, summary = selected
#     full_content = summary  # 假设完整内容存储在摘要中

#     # 更新聊天历史
#     chatbot_history.append({"role": "assistant", "content": full_content})
#     return chatbot_history

# 查看完整内容
# def view_full_content(summary):
#     if summary is None:
#         return "未选择任何摘要。"
#     return summary["full_content"]

# def set_chatbot_content():
#     # 设置新的聊天内容
#     return [
#         {"role": "user", "content": "user content1"},
#         {"role": "assistant", "content": "assistant content1"},
#         {"role": "assistant", "content": "assistant content2"},
#         {"role": "ass", "content": "ass content"},
#         {"role": "user", "content": "user content2"},
#         {"role": "assistant", "content": "assistant content3"},
#     ]

# 创建Gradio界面
with gr.Blocks(css="footer {visibility: hidden}") as interface:
    gr.Markdown("# 聊天机器人")

    chatbot = gr.Chatbot(height=500, label="对话历史", type="messages")
    msg = gr.Textbox(
        placeholder="在这里输入消息...",
        label="用户输入",
        lines=2
    )

    with gr.Row():
        submit_btn = gr.Button("发送")
        clear_btn = gr.Button("清除对话")

    summaries = gr.Dataset(
        components=["text", "text"],
        headers=["模型", "摘要"],
        label="聊天摘要",
        type="array"
    )
    # full_content = gr.Textbox(
    #     label="完整内容",
    #     lines=10,
    #     interactive=False
    # )


    # 设置事件处理
    submit_btn.click(
        chat,
        inputs=[msg],
        outputs=[msg, chatbot, summaries]
    )

    msg.submit(
        chat,
        inputs=[msg],
        outputs=[msg, chatbot, summaries]
    )

    summaries.select(
        lambda selected: print(f"Selected row: {selected}") or update_chatbot(selected),
        inputs=[summaries],
        outputs=[chatbot]
    )
    # summaries.select(
    #     update_chatbot,
    #     inputs=[summaries],
    #     outputs=[chatbot]
    # )

    clear_btn.click(
        lambda: (None, [], gr.Dataset(samples=[])),
        inputs=None,
        outputs=[msg, chatbot, summaries],
        queue=False
    )
    clear_btn.click(clear_history)

    # set_btn = gr.Button("设置聊天内容")
    # set_btn.click(
    #     set_chatbot_content,
    #     inputs=None,
    #     outputs=[chatbot]
    # )

# 启动Gradio应用
if __name__ == "__main__":
    print("启动Kimi聊天界面，请在浏览器中访问提供的URL...")
    interface.launch(share=False)