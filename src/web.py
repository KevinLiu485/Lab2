import gradio as gr
from kimi import chat, messages

# 清除对话历史
def clear_history():
    global messages
    messages.clear()
    return ""

# 与Kimi模型对话并保持聊天历史
def chat_with_kimi(message, history):
    if not message:
        return "", history
    
    # 调用main.py中的chat函数
    bot_response = chat(message)
    
    # 更新聊天历史
    history = history + [[message, bot_response]]
    
    return "", history

# 创建Gradio界面
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown("# Kimi 聊天机器人")
    
    chatbot = gr.Chatbot(height=500, label="对话历史")
    msg = gr.Textbox(
        placeholder="在这里输入消息...",
        label="用户输入",
        lines=2
    )
    
    with gr.Row():
        submit_btn = gr.Button("发送")
        clear_btn = gr.Button("清除对话")
    
    # 设置事件处理
    submit_btn.click(
        chat_with_kimi,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )
    
    msg.submit(
        chat_with_kimi,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )
    
    clear_btn.click(
        lambda: (None, []),
        inputs=None,
        outputs=[msg, chatbot],
        queue=False
    )
    clear_btn.click(clear_history)

# 启动Gradio应用
if __name__ == "__main__":
    print("启动Kimi聊天界面，请在浏览器中访问提供的URL...")
    demo.launch(share=False)