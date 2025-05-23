from openai import OpenAI
from config import config
from api.gpt import GPT

MODEL = 'doubao'

class Doubao(GPT):
    def __init__(self):
        self.client = OpenAI(
            api_key=config.get(MODEL, 'apikey'),
            base_url=config.get(MODEL, 'baseurl'),
            )
        
    def chat(self, message: str) -> str:
        """
        与模型进行多轮或单轮对话
        :param message: 用户输入的消息
        :return: 模型的回复
        """
        completion = self.client.chat.completions.create(
            model=config.get(MODEL, 'modelname'),
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return completion.choices[0].message.content
    
    def get_model_name(self) -> str:
        return MODEL
    
doubao = Doubao()