from openai import OpenAI
from config import config
from api.gpt import GPT
import base64

MODEL = 'kimi'
SYSTEM_MESSAGE = [
    {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
]
WINDOW_SIZE = 20

class Kimi(GPT):
    def __init__(self):
        self.messages = []
        self.client = OpenAI(
            api_key = config.get(MODEL, 'apikey'),
            base_url = config.get(MODEL, 'baseurl'),
        )
        self.system_messages = SYSTEM_MESSAGE
        self.window_size = WINDOW_SIZE

    def chat(self, input: str, file_content=None) -> str:
        """
        与Kimi模型进行多轮对话
        :param message: 用户输入的消息
        :return: Kimi模型的回复
        """    
        # if file_content:
        #     print(f"[Kimi::chat()] file size: {len(file_content)}")
        self._append_user_messages(input, file_content)
        # 携带 messages 与 Kimi 大模型对话
        completion = self.client.chat.completions.create(
            model=config.get(MODEL, 'modelname'),
            messages=self.messages,
            temperature=0.3,
        )
    
        # 通过 API 我们获得了 Kimi 大模型给予我们的回复消息（role=assistant）
        assistant_message = completion.choices[0].message
    
        # 为了让 Kimi 大模型拥有完整的记忆，我们必须将 Kimi 大模型返回给我们的消息也添加到 messages 中
        self._append_return_messages(assistant_message)
    
        return assistant_message.content
    
    def get_model_name(self) -> str:
        return MODEL
    
    def get_display_name(self) -> str:
        """
        获取模型的显示名称
        :return: 模型的显示名称
        """
        return "Kimi"

    def _append_return_messages(self, input: str):
        self.messages.append(input)
        self._maintain_messages_window()


    def _append_user_messages(self, input: str, file_content=None):
        """
        :param input: 用户输入的消息
        :return: 新的消息列表
        """
        if file_content:
            image_url = "data:image/.jpeg;base64," + base64.b64encode(file_content).decode("utf-8")
            self.messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": image_url,
                            },
                        },
                        {
                            "type": "text",
                            "text": input, 
                        },
                    ],
                }
            )
        else:
            self.messages.append({
                "role": "user",
                "content": input,	
            })
        self._maintain_messages_window()
    
    def _maintain_messages_window(self):
        """
        维护消息窗口大小
        """
        # new_messages 是我们下一次请求使用的消息列表，现在让我们来构建它
        new_messages = []
    
        # 每次请求都需要携带 System Messages，因此我们需要先把 system_messages 添加到消息列表中；
        # 注意，即使对消息进行截断，也应该注意保证 System Messages 仍然在 messages 列表中。
        new_messages.extend(self.system_messages)
    
        # 在这里，当历史消息超过 n 条时，我们仅保留最新的 n 条消息
        if len(self.messages) > self.window_size:
            self.messages = self.messages[-self.window_size:]
    
        new_messages.extend(self.messages)
        self.messages = new_messages

kimi = Kimi()