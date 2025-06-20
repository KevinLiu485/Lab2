from .kimi import Kimi
from .doubao import Doubao
from .deepseek import Deepseek
from .gpt import GPT
from typing import List

# 提供统一的接口
GPT_MODELS: List[GPT] = [Kimi(), Doubao(), Deepseek()]