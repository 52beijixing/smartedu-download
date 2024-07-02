from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import hashlib

def aes_ecb_decrypt(key: bytes, ciphertext_base64: str) -> bytes:
    """
    使用AES-ECB模式解密Base64编码的密文。
    
    参数:
        key (bytes): 密钥，长度必须为16, 24, 或32字节。
        ciphertext_base64 (str): Base64编码的密文字符串。
        
    返回:
        bytes: 解密后的明文数据。
        
    抛出:
        ValueError: 如果密钥长度不是16、24或32字节。
        Exception: 解密过程中可能出现的其他加密相关异常。
    """
    # 验证密钥长度
    if len(key) not in [16, 24, 32]:
        raise ValueError("密钥长度必须为16、24或32字节")
    
    # Base64解码密文
    ciphertext = base64.b64decode(ciphertext_base64)
    
    # 初始化AES-ECB模式的cipher对象
    cipher = AES.new(key, AES.MODE_ECB)
    
    # 解密并去除填充
    decrypted_padded = cipher.decrypt(ciphertext)
    decrypted_text = unpad(decrypted_padded, AES.block_size)
    
    return decrypted_text


def aes_cbc_decrypt(key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
    """
    使用AES-CBC模式解密密文数据。
    
    参数:
        key (bytes): 解密密钥，长度应为16、24或32字节。
        ciphertext (bytes): 待解密的密文数据。
        iv (bytes): 初始向量(Initialization Vector)，长度应等于AES块大小（通常为16字节）。
        
    返回:
        bytes: 解密后的明文数据，已去除PKCS7填充。
        
    抛出:
        ValueError: 如果密钥长度不是16、24或32字节，或者IV长度不正确。
        TypeError: 如果输入参数类型不正确。
        Exception: 解密过程中可能出现的其他加密相关异常。
    """
    # 验证密钥长度
    if not isinstance(key, bytes) or len(key) not in [16, 24, 32]:
        raise ValueError("密钥必须是16、24或32字节长的字节串")
    # 验证IV长度
    if not isinstance(iv, bytes) or len(iv) != AES.block_size:
        raise ValueError(f"IV长度必须为{AES.block_size}字节")
    
    # 使用AES-CBC模式初始化Cipher对象
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 解密并去除PKCS7填充
    decrypted_padded = cipher.decrypt(ciphertext)
    decrypted_text = unpad(decrypted_padded, AES.block_size)
    
    return decrypted_text


def md5_encrypt(text: str) -> str:
    """
    使用MD5算法对输入的字符串进行哈希加密，并返回加密后结果的前16位字符串。
    
    注意:
        MD5算法因其安全性较低，不推荐用于安全认证等需要高安全性的场景。
        在非安全性敏感的应用中，如简单数据一致性校验，此函数仍可适用。
    
    参数:
        text (str): 需要加密的原始字符串。
    
    返回:
        str: MD5哈希值的前16位字符串表示。
    """
    md5_hash = hashlib.md5(text.encode('utf-8'))
    return md5_hash.hexdigest()[:16]


def bytes_to_base64(byte_data: bytes) -> str:
    """
    将字节数据转换为Base64编码的字符串。
    """
    # 使用base64模块的b64encode方法对字节数据进行Base64编码
    base64_encoded_bytes = base64.b64encode(byte_data)
    # 将编码后的字节数据解码为字符串
    base64_encoded_str = base64_encoded_bytes.decode('utf-8')
    return base64_encoded_str