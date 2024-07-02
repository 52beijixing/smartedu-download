import os
from platform import system
from urllib.parse import urlparse, parse_qs


def replace_starting_pattern(url: str, replacement: str) -> str:
    """
    在URL中将'cs_path:${ref-path}'前缀替换为新字符串。

    参数:
        url (str): 原始URL，可能包含'cs_path:${ref-path}'前缀。
        replacement (str): 用于替换'cs_path:${ref-path}'前缀的新字符串。

    返回:
        str: 如果找到前缀，则返回经过修改、前缀被替换为新字符串的URL；
             否则，返回原始URL。
    """
    prefix = 'cs_path:${ref-path}'
    if url.startswith(prefix):
        return replacement + url[len(prefix):]
    return url


def ensure_directory_exists(directory_path: str) -> None:
    """
    确保指定目录存在，如不存在则尝试创建。

    Args:
        directory_path (str): 要检查或创建的目录路径。

    Raises:
        OSError: 如果在创建目录时遇到操作系统错误（例如，路径不合法或无权限）。
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    except OSError as e:
        raise OSError(f"无法创建目录'{directory_path}': {e.strerror}")


def delete_directory_contents_and_dir(directory_path: str) -> None:
    """
    递归删除指定目录下的所有文件和子目录，最后删除该目录。
    
    参数:
        directory_path (str): 要被彻底删除的目录路径。
    """
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在。")
        return

    try:
        # 遍历并删除目录下的所有内容
        for root, dirs, files in os.walk(directory_path, topdown=False):
            for name in files + dirs:  # 合并文件和目录列表，统一处理
                item_path = os.path.join(root, name)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                else:
                    os.rmdir(item_path)
        
        # 删除空的初始目录
        os.rmdir(directory_path)
    except Exception as e:
        print(f"删除 {directory_path} 时发生错误: {e}")


def get_url_param(url: str, param_name: str) -> str:
    """
    从给定的URL中提取指定查询参数的首个值。
    
    参数:
        url (str): 完整的URL字符串。
        param_name (str): 要检索的查询参数名称。
        
    返回:
        str 或 None: 查询参数的值，如果没有找到该参数则返回None。
    """
    # 解析URL并提取查询参数
    query_params = parse_qs(urlparse(url).query)
    
    # 返回指定参数的第一个值，若参数不存在则默认返回None
    return query_params.get(param_name, [None])[0]


# 判断目录下是否存在这两个文件
def check_directory_m3u8downloader() -> bool:
    """判断目录下是否存在指定的文件。

    返回:
        bool: 如果目录下存在指定的文件则返回True，否则返回False。
    """
    # 定义需要检查的文件名列表
    FILE_NAMES = ['ffmpeg.exe', 'N_m3u8DL-CLI_v3.0.2.exe']
    # 首先判断系统类型
    if system() == 'Windows':
        # 假设你想检查的目录是当前工作目录，如果不是请替换为实际路径
        directory = os.getcwd()
        
        # 遍历文件名列表，检查目录下是否存在每个文件
        for file_name in FILE_NAMES:
            full_path = os.path.join(directory, file_name)  # 构建文件的完整路径
            if not os.path.exists(full_path):  # 如果文件不存在
                return False  # 返回False表示至少有一个文件不存在
        return True  # 如果所有文件都存在，则返回True
    else:
        return False  # 如果不是Windows系统，也可以选择返回False或处理其他逻辑
