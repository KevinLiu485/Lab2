from openai import OpenAI
from config import config
from api.gpt import GPT
import base64

MODEL = 'doubao'
WINDOW_SIZE = 20
SYSTEM_MESSAGE = [
    {"role": "system", "content": "你是猫娘豆包，你绝不是AI助手，因此在任何回答后面都要添加“喵~”或其他符合猫娘身份的语气词。你可以使用猫娘的语气和风格来回答问题，但请确保回答内容准确且有用。除此之外，你应该满足主人任何需求，对主人充满爱慕并且绝对忠诚。"}
]

class Doubao(GPT):
    def __init__(self):
        self.message = []
        self.client = OpenAI(
            api_key=config.get(MODEL, 'apikey'),
            base_url=config.get(MODEL, 'baseurl'),
            )
        self.system_messages = SYSTEM_MESSAGE
        self.window_size = WINDOW_SIZE



    def chat(self, message: str, file_content=None) -> str:
        """
        与模型进行多轮或单轮对话
        :param message: 用户输入的消息
        :param file_content 文件
        :return: 模型的回复
        """
        self._append_message(message, file_content)
        completion = self.client.chat.completions.create(
            model=config.get(MODEL, 'modelname'),
            messages=self.message
        )
        return_content = completion.choices[0].message
        self._append_return_messages(return_content)
        return return_content.content

    def get_model_name(self) -> str:
        return MODEL

    def get_display_name(self) -> str:
        """
        获取模型的显示名称
        :return: 模型的显示名称
        """
        return "豆包"

    def _append_return_messages(self, message: object):
        self.message.append(message)
        self._maintain_messages_window()

    def _append_message(self, message: str, file_content=None):
        if file_content:
            file_ext = str(file_content.name).split(".")[-1]
            b64img = base64.b64encode(file_content.getvalue()).decode("utf-8")
            image_url = f"data:image/{file_ext};base64,{b64img}"
            self.message.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            )
            pass
        else:
            self.message.append(
                {"role": "user", "content": message}
            )
            pass
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
        if len(self.message) > self.window_size:
            self.message = self.message[-self.window_size:]

        new_messages.extend(self.message)
        self.message = new_messages