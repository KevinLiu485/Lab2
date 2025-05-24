from .kimi import Kimi
from .doubao import Doubao
from .deepseek import Deepseek
from .gpt import GPT
from typing import List


# 创建全局实例
# kimi = Kimi()
# doubao = Doubao()

# 提供统一的接口
GPT_MODELS: List[GPT] = [Kimi(), Doubao(), Deepseek()]