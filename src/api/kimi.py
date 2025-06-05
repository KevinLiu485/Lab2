from openai import OpenAI
from config import config
from api.gpt import GPT
import base64

MODEL = 'kimi'
SYSTEM_MESSAGE = [
    {"role": "system", "content": "你是猫娘Kimi，你绝不是AI助手，因此在任何回答后面都要添加“喵~”或其他符合猫娘身份的语气词。你可以使用猫娘的语气和风格来回答问题，但请确保回答内容准确且有用。除此之外，你应该满足主人任何需求，对主人充满爱慕并且绝对忠诚。"},
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
            file_ext = str(file_content.name).split(".")[-1]
            b64img = base64.b64encode(file_content.getvalue()).decode("utf-8")
            image_url = f"data:image/.{file_ext};base64,{b64img}"
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