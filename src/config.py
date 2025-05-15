import json
import os

def load_config(config_file="config.json"):
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

def get_api_key():
    """获取API密钥"""
    config = load_config()
    if config:
        print("配置加载成功:")
        for item in config:
            # print(f"API Name: {item.get('name')}")
            # print(f"API Key: {item.get('key')}")
            return item.get('key', '')
    # return config.get("api_key", "")

# def get_base_url():
#     """获取API基础URL"""
#     config = load_config()
#     return config.get("base_url", "https://api.moonshot.cn/v1")

# def get_model():
#     """获取使用的模型名称"""
#     config = load_config()
#     return config.get("model", "moonshot-v1-8k")

# 如果直接运行此文件，测试配置是否正确加载
if __name__ == "__main__":
    config = load_config()
    if config:
        print("配置加载成功:")
        for item in config:
            print(f"API Name: {item.get('name')}")
            print(f"API Key: {item.get('key')}")
            # if item.get('name') == 'kimi':
            #     return item.get('key', '')
    else:
        print("配置加载失败，请确保config.json文件存在且格式正确")