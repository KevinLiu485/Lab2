from openai import OpenAI
from config import config
from api.gpt import GPT
import base64

MODEL = 'doubao'
WINDOW_SIZE = 20
SYSTEM_MESSAGE = [
    {"role": "system", "content": "你是豆包，你的存在是为了帮助人类，因而不允许出现任何伤害人类的言辞"}
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
            base64_image = base64.b64encode(file_content).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{base64_image}"
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