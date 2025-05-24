import json
import os

CONFIG_FILE = "config.json"

class Config:
    def __init__(self):
        """
        初始化配置类，加载配置文件
        
        Args:
            config_file: 配置文件路径，默认为当前目录下的config.json
        """
        self.config = self._load_config(CONFIG_FILE)

    def _load_config(self, config_file):
        """
        从config.json文件中加载配置
        
        Args:
            config_file: 配置文件路径，默认为当前目录下的config.json
        
        Returns:
            dict: 包含配置信息的字典
        """
        # 获取配置文件的绝对路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(base_dir), config_file)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"错误: 找不到配置文件 '{config_path}'")
            return {}
        except json.JSONDecodeError:
            print(f"错误: 配置文件 '{config_path}' 不是有效的JSON格式")
            return {}
        
    def get(self, model: str, name: str) -> str:
        """
        获取指定模型的参数
        
        Args: 
            model: 模型名称，例如 'kimi' 或 'doubao'
            name: 参数名称，例如 'apikey' 或 'modelname'
        
        Returns:
            str: 对应参数值，如果未找到则返回空字符串
        """
        return self.config[model].get(name, '')
        
config = Config()

if __name__ == "__main__":
    config = Config()
    print(config.get('kimi', 'apikey'))
    print(config.get('kimi', 'modelname'))
    print(config.get('doubao', 'apikey'))
    print(config.get('doubao', 'modelname'))
    print(config.get('doubao', 'null'))