import requests
from utils.tool import replace_starting_pattern


def get_download_url(ti_items, file_size, file_format):
    """
    根据文件格式和大小从资源项中获取下载URL。
    
    :param ti_items: 资源项目列表，每个项目是一个字典
    :param file_size: 目标文件的大小
    :param file_format: 目标文件的格式
    :return: 下载URL，如果找不到则返回None
    """
    # 定义可能的URL前缀映射，减少硬编码并提高扩展性
    url_prefixes = {
        "mp4": "https://r1-ndr.ykt.cbern.com.cn",
        "default": "https://cdncs.ykt.cbern.com.cn/v0.1/static"
    }

    # 遍历资源项，寻找匹配的文件
    for item in ti_items:
        # 确定URL前缀，mp4格式有特殊处理
        prefix = url_prefixes.get(file_format, url_prefixes["default"]) if file_format != "mp4" else url_prefixes[file_format]
        
        # 检查文件格式和大小条件，一旦满足则立即返回URL
        if ((file_format == "mp4" and item.get("ti_file_flag") == "href") or
            (item.get("ti_size") == file_size and file_format != "mp4")):
            ti_storage = item.get("ti_storage")
            return replace_starting_pattern(ti_storage, prefix)
    
    # 未找到符合条件的URL，则返回None
    return None


def fetch_resources(resource_key, relations, dir_name):
    """提取特定资源列表中的文件信息"""
    resource_list = relations.get(resource_key, [])
    items = []
    for item in resource_list:
        #file_name = item.get("title")
        global_title = item.get("global_title", {})
        title_zh_cn = global_title.get("zh-CN", "")
        show_title = item.get("title", "")
        file_name = f"{title_zh_cn}_{show_title}"
        custom_properties = item.get("custom_properties", {})
        file_format = custom_properties.get("format", "")
        file_size = custom_properties.get("size", "")
        ti_items = item.get("ti_items", [])
        file_url = get_download_url(ti_items, file_size, file_format)
        items.append({
            "dir_name": dir_name,
            "file_name": file_name,
            "file_url": file_url,
            "file_format": file_format,
            "file_size": file_size
        })
    return items


def get_textbook_info(content_id: str) -> list[dict]:
    """
    根据内容ID获取教科书资源信息。
    
    参数:
        content_id (str): 教科书内容的唯一标识符。
        
    返回:
        list[dict]: 包含资源信息的字典列表，如果发生错误则返回None。
    """
    try:
        # 构建请求URL
        json_url = f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/details/{content_id}.json"
        
        # 发起GET请求并检查响应状态
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()
        
        # 解析JSON响应数据
        data = response.json()
        
        # 获取资源基本信息
        file_name = data.get("title", content_id)
        custom_props = data.get("custom_properties", {})
        file_format = custom_props.get("format")
        file_size = custom_props.get("size")

        # 遍历资源项以查找正确的文件URL
        ti_items = data.get("ti_items", [])
        file_url = get_download_url(ti_items, file_size, file_format)

        # 返回资源信息
        return [{
            "dir_name": "",  # 目录名默认为空，根据实际需求可调整
            "file_name": file_name,
            "file_url": file_url,
            "file_format": file_format,
            "file_size": file_size
        }]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None


def get_courseware_info(resource_id: str)  -> list[dict]:
    """
    根据资源ID获取课件资源信息。
    
    参数:
        resource_id (str): 课件内容的唯一标识符。
        
    返回:
        list[dict]: 包含资源信息的字典列表，如果发生错误则返回None。
    """
    try:
        # 构建请求URL
        json_url = f"https://s-file-2.ykt.cbern.com.cn/zxx/ndrv2/prepare_sub_type/resources/details/{resource_id}.json"

        # 发起GET请求并检查响应状态
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()

        # 解析JSON响应数据
        data = response.json()

        # 获取资源基本信息
        file_name = data.get("title", resource_id)
        custom_props = data.get("custom_properties", {})
        file_format = custom_props.get("format")
        file_size = custom_props.get("size")

        # 遍历资源项以查找正确的文件URL
        ti_items = data.get("ti_items", [])
        file_url = get_download_url(ti_items, file_size, file_format)

        # 返回资源信息
        return [{
            "dir_name": "",  # 目录名默认为空，根据实际需求可调整
            "file_name": file_name,
            "file_url": file_url,
            "file_format": file_format,
            "file_size": file_size
        }]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None


def get_bookcoursebag_info(activity_id: str) -> list[dict]:
    """
    根据活动ID获取书课包中的课件信息列表。
    
    参数:
        activity_id (str): 书课包的唯一活动ID。
        
    返回:
        list[dict]: 课件信息列表，每个元素包含课件的目录名、文件名、下载链接、文件格式、文件大小。
                     若发生错误，则返回None。
    """
    try:
        bookcoursebag_info_list = []  # 存储书课包课件信息的列表
        
        # 构造请求URL以获取详细信息
        json_url = f"https://s-file-2.ykt.cbern.com.cn/zxx/ndrv2/national_lesson/resources/details/{activity_id}.json"
        
        # 发起HTTP GET请求并验证响应状态
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()
        
        # 解析响应中的JSON数据
        data = response.json()
        
        # 提取书课包标题和资源关系
        dir_name = data.get("title")
        relations = data.get("relations", {})

        bookcoursebag_info_list = fetch_resources("national_course_resource", relations, dir_name)
        
        return bookcoursebag_info_list
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None


def get_experiment_course_info(course_id: str) -> list[dict]:
    """
    根据课程ID获取实验课程的资源信息列表。
    
    参数:
        course_id (str): 课程的唯一ID。
        
    返回:
        list[dict]: 包含课程资源信息的列表，每个元素代表一个资源，包含文件名、下载链接等。
                    若发生错误，则返回None。
    """
    try:
        experiment_course_list = []

        json_url = f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/experiment/resources/details/{course_id}.json"
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        relations = data.get("relations", {})
        name = data.get("title", "")
        
        # 处理lesson_1资源
        lesson_1_items = fetch_resources("lesson_1", relations, "")
        # 处理实验视频资源
        experiment_video_items = fetch_resources("experiment_video", relations, "")

        experiment_course_list = lesson_1_items + experiment_video_items
                
        return experiment_course_list
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None



def get_one_teacher_info(lesson_id: str) -> list[dict]:
    """
    根据章节ID获取一师一课的资源信息列表。
    
    参数:
        lesson_id (str): 章节的唯一ID。
        
    返回:
        list[dict]: 包含章节资源信息的列表，每个元素代表一个资源，包含文件名、下载链接等。
                    若发生错误，则返回None。
    """
    try:
        json_url = f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/prepare_lesson/resources/details/{lesson_id}.json"
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        relations = data.get("relations", {})
        dir_name = data.get("title")
        
        # 分别处理不同类型的资源
        lesson_plan_design_items = fetch_resources("lesson_plan_design", relations, dir_name)
        classroom_record_items = fetch_resources("classroom_record", relations, dir_name)
        teaching_assets_items = fetch_resources("teaching_assets", relations, dir_name)
        
        # 合并所有资源列表
        one_teacher_list = lesson_plan_design_items + classroom_record_items + teaching_assets_items
        
        return one_teacher_list
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None


def get_subject_info(course_id: str) -> list[dict]:
    """
    根据课程ID获取学科课程精品课的资源信息列表。
    
    参数:
        course_id (str): 课程的唯一ID。
        
    返回:
        list[dict]: 包含课程资源信息的列表，每个元素代表一个资源，包含文件名、下载链接等。
                    若发生错误，则返回None。
    """
    try:
        json_url = f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/{course_id}.json"
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        relations= data.get("relations", {})
        dir_name = data.get("title")

        subject_list = fetch_resources("course_resource", relations, dir_name)

        return subject_list
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None


def get_basis_info(course_id: str) -> list[dict]:
    """
    根据课程ID获取基础教育精品课的资源信息列表。
    
    参数:
        course_id (str): 课程的唯一ID。
        
    返回:
        list[dict]: 包含课程资源信息的列表，每个元素代表一个资源，包含文件名、下载链接等。
                    若发生错误，则返回None。
    """
    try:
        json_url = f"https://s-file-1.ykt.cbern.com.cn/competitive/elite_lesson/resources/{course_id}.json"
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        relations= data.get("relations", {})
        dir_name = data.get("title")

        basis_list = fetch_resources("course_resource", relations, dir_name)

        return basis_list
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None


def get_homework_info(content_id: str) -> list[dict]:
    """
    根据内容ID获取作业的资源信息列表。
    
    参数:
        content_id (str): 作业资源的唯一ID。
        
    返回:
        list[dict]: 包含作业资源信息的列表，每个元素代表一个资源，包含文件名、下载链接等。
                    若发生错误，则返回None。
    """
    try:
        json_url = f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/special_edu/resources/details/{content_id}.json"
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()

        data = response.json()        

        # 获取资源基本信息
        file_name = data.get("title")
        custom_props = data.get("custom_properties", {})
        file_format = custom_props.get("format")
        file_size = custom_props.get("size")
        file_url = None

        # 遍历资源项以查找正确的文件URL
        ti_items = data.get("ti_items", [])
        for item in ti_items:
            if ((file_format == "mp4" and item.get("ti_file_flag") == "href") or
            (item.get("ti_size") == file_size and file_format != "mp4")):
                file_url = item.get("ti_storages")[0]
        
        # 返回资源信息
        return [{
            "dir_name": "",
            "file_name": file_name,
            "file_url": file_url,
            "file_format": file_format,
            "file_size": file_size
        }]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None