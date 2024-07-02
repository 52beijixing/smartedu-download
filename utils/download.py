import os
import requests
import re
import binascii
import time
from urllib.parse import urljoin
from utils.tool import ensure_directory_exists, delete_directory_contents_and_dir, check_directory_m3u8downloader
from utils.crypt import aes_ecb_decrypt, aes_cbc_decrypt, md5_encrypt, bytes_to_base64
from multiprocessing.dummy import Pool


def download_file_from_url(url: str, save_path: str, filename: str = None) -> str:
    """
    从指定URL下载文件并保存到指定路径。
    
    参数:
    - url (str): 要下载的文件的URL。
    - save_path (str): 本地保存文件的目录路径。
    - filename (str, optional): 保存时使用的文件名。默认为None，此时将从URL中提取文件名。
    
    返回:
    - str: 成功时返回文件的完整保存路径；失败返回None。
    """

    ensure_directory_exists(save_path)

    try:
        # 如果文件名未提供，从URL中提取
        if filename is None:
            filename = url.split('/')[-1]
        else:
            format = url.split('/')[-1].split('.')[-1]
            filename = filename + '.' + format
                
        # 发起GET请求，设置流式传输
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 确保请求成功
        
        # 使用os.path.join确保路径正确拼接（跨平台）
        full_path = os.path.join(save_path, filename)
        
        # 写入文件
        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 过滤空块
                    file.write(chunk)
        
        return full_path
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"连接错误: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"超时错误: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"下载请求过程中发生错误: {req_err}")
    except IOError as io_err:
        print(f"文件写入错误: {io_err}")
    
    return None


def downloader_m3u8(m3u8_url: str, save_path: str, file_name: str, key: bytes) -> None:
    key_base64 = bytes_to_base64(key)
    cmd = f'N_m3u8DL-CLI_v3.0.2.exe {m3u8_url} --workDir {save_path} --saveName {file_name} --useKeyBase64 {key_base64} --enableDelAfterDone'
    os.system(cmd)
    

def download_video(m3u8_url: str, save_path: str, file_name: str) -> None:
    """
    下载M3U8格式的视频并将其保存为指定文件。
    
    步骤：
    1. 解析M3U8链接获取TS片段、密钥URL、密钥ID及初始化向量。
    2. 使用密钥URL和ID获取解密密钥。
    3. 在保存路径下创建以密钥ID命名的文件夹以存储下载的TS片段。
    4. 下载加密的M3U8内容，包括TS片段，并应用解密。
    5. 将所有下载的TS片段合并成单个视频文件。
    
    参数:
    - m3u8_url (str): M3U8播放列表的URL。
    - save_path (str): 视频文件保存的目录路径。
    - file_name (str): 保存视频文件的名称（包含扩展名）。
    """
    # 解析M3U8链接获取所需数据
    m3u8_info = parse_m3u8(m3u8_url)
    ts_segments = m3u8_info.get('ts_segments')
    key_url = m3u8_info.get('key_url')
    key_id = m3u8_info.get('key_id')
    initialization_vector = m3u8_info.get('iv')
    
    # 获取解密密钥
    decryption_key = get_signs(key_url, key_id)
    
    if check_directory_m3u8downloader():
        downloader_m3u8(m3u8_url, save_path, file_name, decryption_key)
        print(f"下载完成，文件保存在 {os.path.join(save_path, file_name)}.mp4")
        return
    
    # 准备TS片段存储的文件夹路径
    ts_segment_folder = os.path.join(save_path, key_id)
    
    # 下载并解密TS片段
    download_encrypted_m3u8(m3u8_url, ts_segments, save_path, key_id, decryption_key, initialization_vector)
    
    # 合并所有TS片段为最终视频文件
    merge_ts_files(ts_segment_folder, save_path, file_name)



def parse_m3u8(m3u8_url: str) -> dict:
    """
    解析M3U8链接以提取加密密钥URL、密钥及TS片段列表。
    
    参数:
        m3u8_url (str): M3U8文件的网址。
    
    返回:
        dict: 包含密钥URL、密钥及TS片段列表的字典。
              格式: {'key_url': str, 'key': str, 'ts_segments': List[str]}
    """
    # 获取M3U8内容
    response = requests.get(m3u8_url)
    m3u8_content = response.text
    
    # 初始化列表和变量
    ts_segments = []  # TS片段列表
    key_url = None  # 密钥URL
    key_id = None  # 密钥ID
    iv_bytes = None
    
    # 遍历M3U8内容的每一行
    for line in m3u8_content.splitlines():
        if line.startswith('#'):
            # 如果行包含密钥信息，则提取之
            if 'EXT-X-KEY' in line:
                key_url_match = re.search(r'URI="([^"]+)"', line)
                key_match = re.search(r'_keys/([^"]+)"', line)
                iv_match = re.search(r'IV=(.*?)(?=\n|$)', line) 

                # 设置密钥URL和密钥id
                if key_url_match:
                    key_url = key_url_match.group(1)
                if key_match:
                    key_id = key_match.group(1)
                if iv_match:
                    iv = iv_match.group(1)
                    iv_bytes = binascii.unhexlify(iv.replace('0x', "")).hex()[:16].encode('utf-8')
        else:
            # 非注释行视为TS片段URL，加入列表
            ts_segments.append(urljoin(m3u8_url, line))
    
    # 返回包含所有提取信息的字典
    return {'key_url': key_url, 'key_id': key_id, 'ts_segments': ts_segments, 'iv': iv_bytes}


def get_signs(key_url: str,key_id: str):
    get_sign_url = key_url + "/signs"
    try:
        response = requests.get(get_sign_url)
        response.raise_for_status()
        nonce = response.json()["nonce"]
        sign = md5_encrypt(nonce+key_id)
        get_key_id_url = f"{key_url}?nonce={nonce}&sign={sign}"
        response = requests.get(get_key_id_url)
        response.raise_for_status()
        key = response.json()["key"]
        return aes_ecb_decrypt(sign.encode('utf-8'), key)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")

def download_encrypted_m3u8(m3u8_url, ts_segments, save_path, key_id , key = None, iv = None):
    """下载加密的M3U8视频流"""
    output_folder = os.path.join(save_path, key_id)
    os.makedirs(output_folder, exist_ok=True)
    
    ts_list = [(urljoin(m3u8_url.rsplit('/', 1)[0], ts_url),
          os.path.join(str(output_folder), urljoin(m3u8_url.rsplit('/', 1)[0], ts_url).split('-')[-1]), 
          key, 
          iv) for ts_url in ts_segments]

    num_processes = os.cpu_count() or 4
    # 多线程下载
    with Pool(num_processes) as pool:
        pool.starmap(download_ts_segment, ts_list)

    print("ts视频流下载完成.")



def download_ts_segment(ts_url: str, ts_temp_folder: str, key:str = None, iv:str = None):
    """
    下载并（可选）解密单个TS片段。
    
    :param ts_url: TS片段的下载URL
    :param ts_temp_folder: 保存下载文件的本地路径
    :param key: 解密密钥，如果TS片段加密了的话
    :param iv: 解密初始化向量，与密钥一起使用
    """
    print(f"正在下载：{ts_url.split('-')[-1]}")
    
    max_retries = 3  # 最大重试次数
    retry_delay = 1  # 重试间隔时间（秒）
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(ts_url, timeout=10)  # 添加超时限制以避免长时间等待
            encrypted_data = response.content
            break  # 成功下载，跳出循环
        except requests.RequestException as e:
            print(f"下载失败，尝试第{attempt}/{max_retries}次，原因：{e}")
            if attempt < max_retries:
                time.sleep(retry_delay)  # 等待一段时间后重试
            else:
                raise  # 所有重试均失败，重新抛出异常
    
    # 根据是否提供密钥决定是否解密
    if key is not None:
        decrypted_data = aes_cbc_decrypt(key, encrypted_data, iv)
    else:
        decrypted_data = encrypted_data  # 未提供密钥，直接使用加密数据
    
    # 保存数据到本地文件
    with open(ts_temp_folder, 'wb') as file:
        file.write(decrypted_data)


def merge_ts_files(ts_folder_path: str, save_folder: str, output_file: str):
    """
    合并指定目录下的所有 .ts 文件到一个 MP4 文件中。
    
    :param ts_folder_path: 包含 .ts 文件的目录路径
    :param save_folder: 合并后文件保存的目录路径
    :param output_file: 合并后文件的名称（不含扩展名）
    """
    # 构建输出文件的完整路径
    outfile_name = os.path.join(save_folder, f"{output_file}.mp4")
    
    try:
        # 确保保存目录存在，如果不存在则创建
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        
        # 打开输出文件用于写入二进制数据
        with open(outfile_name, 'wb') as outfile:
            # 遍历并排序 ts 文件夹中的所有文件
            for filename in sorted(os.listdir(ts_folder_path)):
                if filename.endswith('.ts'):
                    # 构建 ts 文件的完整路径
                    filepath = os.path.join(ts_folder_path, filename)
                    
                    try:
                        # 打开并读取当前 ts 文件的二进制内容，追加到输出文件中
                        with open(filepath, 'rb') as infile:
                            outfile.write(infile.read())
                    except IOError as e:
                        # 处理读取文件时可能发生的错误
                        print(f"读取文件 {filename} 出错: {e}")
                        return
                
    except Exception as e:
        # 处理其他可能的异常情况
        print(f"合并过程中出现错误: {e}")
    else:
        print(f"所有.ts文件已成功合并至: {outfile_name}")
    finally:
        # 清理ts临时目录
        delete_directory_contents_and_dir(ts_folder_path)