import requests
from utils.tool import replace_starting_pattern, get_info_parse
import random
import time
from utils.crypt import auth_encrypt
import re


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
        if (item.get("ti_file_flag") == "href" or
            (item.get("ti_size") == file_size and file_format != "mp4")):
            ti_storage = item.get("ti_storage")
            return replace_starting_pattern(ti_storage, prefix)
    
    # 未找到符合条件的URL，则返回None
    return None


def fetch_resources(resource_key, relations, dir_name, teacher_name, user_data, app_id):
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
        if file_url is None:
            container_id = item.get("container_id")
            id =item.get("id")
            access_token = get_info_parse(user_data, "access_token")
            mac_key = get_info_parse(user_data, "mac_key")
            save_info(container_id, id, access_token, mac_key, app_id)
            file_url = get_courseware_url(id, access_token, mac_key, app_id)

        items.append({
            "dir_name": dir_name,
            "file_name": file_name,
            "file_url": file_url,
            "file_format": file_format,
            "file_size": file_size,
            "teacher_name": teacher_name
        })
    return items


def get_textbook_info(content_id: str, user_data: str, app_id: str):
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


def get_courseware_info(resource_id: str, user_data: str, app_id: str):
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


def get_bookcoursebag_info(activity_id: str, user_data: str, app_id: str):
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
        teacher_list = data.get("teacher_list")
        teacher_name = teacher_list[0]["name"]
        if not teacher_name:
            teacher_name = "未知教师"
        bookcoursebag_info_list = fetch_resources("national_course_resource", relations, dir_name, teacher_name, user_data, app_id)
        
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


def get_experiment_course_info(course_id: str, user_data: str, app_id: str):
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
        teacher_list = data.get("teacher_list")
        teacher_name = teacher_list[0]["name"]
        if not teacher_name:
            teacher_name = "未知教师"
        
        # 处理lesson_1资源
        lesson_1_items = fetch_resources("lesson_1", relations, name, teacher_name, user_data, app_id)
        # 处理实验视频资源
        experiment_video_items = fetch_resources("experiment_video", relations, name, teacher_name, user_data, app_id)

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



def get_one_teacher_info(lesson_id: str, user_data: str, app_id: str):
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
        teacher_list = data.get("teacher_list")
        teacher_name = teacher_list[0]["name"]
        if not teacher_name:
            teacher_name = "未知教师"
        
        # 分别处理不同类型的资源
        lesson_plan_design_items = fetch_resources("lesson_plan_design", relations, dir_name, teacher_name, user_data, app_id)
        classroom_record_items = fetch_resources("classroom_record", relations, dir_name, teacher_name, user_data, app_id)
        teaching_assets_items = fetch_resources("teaching_assets", relations, dir_name, teacher_name, user_data, app_id)
        
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


def get_subject_info(course_id: str, user_data: str, app_id: str):
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
        teacher_list = data.get("teacher_list")
        teacher_name = teacher_list[0]["name"]
        if not teacher_name:
            teacher_name = "未知教师"

        subject_list = fetch_resources("course_resource", relations, dir_name, teacher_name, user_data, app_id)

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


def get_basis_info(course_id: str, user_data: str, app_id: str):
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
        teacher_list = data.get("teacher_list")
        teacher_name = teacher_list[0]["name"]
        if not teacher_name:
            teacher_name = "未知教师"

        basis_list = fetch_resources("course_resource", relations, dir_name, teacher_name, user_data, app_id)

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


def get_homework_info(content_id: str, user_data: str, app_id: str):
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

def get_thematic_infos(content_id: str, user_data: str, app_id: str):
    try:
        json_url = f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/special_edu/thematic_course/{content_id}/resources/list.json"
        response = requests.get(json_url, timeout=10)
        response.raise_for_status()

        datas = response.json()
        ret = []

        for data in datas:
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
            
            per_ret = [{
            "dir_name": "",
            "file_name": file_name,
            "file_url": file_url,
            "file_format": file_format,
            "file_size": file_size
            }]
            ret.append(per_ret)
        
        # 返回资源信息
        return ret
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")

def get_default_infos(default_dir: str, user_data: str, app_id: str):
    #吐槽一下：就我目前测试js看来，每次请求页面的时候就去所有大视频集合里面找，找出来符合要求的视频，怪不得nt东西网站这么卡
    try:
        #先获取default_id 就是课程下任意链接的 teachingmaterialId
        default_ids = []
        features = default_dir.split("/")
        #测试发现123都有并且相同，目前暂时使用1
        data_json = "https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/national_lesson/teachingmaterials/version/data_version.json"
        response = requests.get(data_json, timeout=10)
        response.raise_for_status()

        search_lists = response.json()

        for search in search_lists.get("urls"):
            #print(search)
            response = requests.get(search, timeout=10)
            response.raise_for_status()
            datas = response.json()
            for data in datas:
                #先获得特征表
                tag_list = []
                for tag in data.get("tag_list"):
                    tag_list.append(tag.get("tag_id"))
                #再匹配特征相同的
                state = True
                for per in features:
                    state = state and per in tag_list
                if state:
                    default_ids.append(data.get("id"))
        #print(default_ids)
        #raise
        if len(default_ids) == 0:
            print("无法解析，请将源链接复制并前往 https://github.com/52beijixing/smartedu-download/issues 反馈！")
            return []

        ret = []
        for default_id in default_ids:
        #测试发现123都有并且相同，目前暂时使用1
            json_url = f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/national_lesson/teachingmaterials/{default_id}/resources/parts.json" 
            response = requests.get(json_url, timeout=10)
            response.raise_for_status()

            search_lists = response.json()

            for search in search_lists:
                response = requests.get(search, timeout=10)
                response.raise_for_status()
                
                contained_title = []
                datas = response.json()
                for data in datas:
                    if data["resource_type_code"] == "national_lesson":#这里只包含国家课程
                        activityId = data.get("id")
                        title = data.get("title")
                        print(f"获取到视频：{title}\tid = {activityId}")
                        ret.append(get_bookcoursebag_info(activityId,user_data,app_id))
                        contained_title.append(data["title"])
                    elif data["resource_type_code"] == "elite_lesson":#这里只包含精品课
                        courseId = data.get("id")
                        title = data.get("title")
                        print(f"获取到视频：{title}\tid = {courseId}")
                        ret.append(get_subject_info(courseId,user_data,app_id))
                        contained_title.append(title)
                
                #double check一下防止有遗漏资源文件
                state = True
                for i in range(len(datas)):
                    data = datas[i]
                    if not data["title"] in contained_title:
                        print(f"第{i}项目出现问题\ntype:{data["resource_type_code"]}暂未支持\n请将控制台信息和链接复制并前往 https://github.com/52beijixing/smartedu-download/issues 反馈！")
                        state = False
                if not state:
                    raise

        # 返回资源信息
        return ret
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")

def get_wisdom_info(content_id: str, user_data: str, app_id: str):
    try:
        json_url = f"https://s-file-1.ykt.cbern.com.cn/ldjy/ndrs/special_edu/resources/details/{content_id}.json"
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

def get_courseware_url(resource_id, access_token, mac_key, app_id):
    """
    获取资源的下载链接。

    :param resource_id: 资源ID。
    :param access_token: 访问令牌。
    :param mac_key: MAC密钥。
    :param app_id: 应用程序ID。
    :return: 包含文件URL的字典列表或None。
    """
    # 获取当前时间的时间戳（毫秒）
    current_time_ms = int(time.time() * 1000)
    # 生成一个700-900之间的随机数
    diff = str(random.randint(700, 900))
    # 构建请求URL
    request_url = f"https://doc-center.ykt.eduyun.cn/v1.0/c/document/{resource_id}?path=&_r={current_time_ms}"

    # 请求类型
    method_type = "GET"
    
    # 获取授权头
    authorization_header = auth_encrypt(request_url, access_token, mac_key, diff, method_type)
    
    # 设置请求头
    headers = {
        'Authorization': authorization_header,
        'sdp-app-id': app_id
    }
    try:
        # 发起GET请求并检查响应状态
        response = requests.get(url = request_url, headers = headers, timeout=10)
        response.raise_for_status()

        # 解析JSON响应数据
        data = response.json()

        custom_props = data.get("custom_properties", {})
        file_format = custom_props.get("format")
        file_size = custom_props.get("size")

        # 遍历资源项以查找正确的文件URL
        ti_items = data.get("ti_items", [])
        file_url = get_download_url(ti_items, file_size, file_format)

        # 返回资源信息
        return file_url
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None

def save_info(container_id: str, resource_id: str, access_token: str, mac_key: str, app_id: str):
    request_url = "https://doc-center.ykt.eduyun.cn/v1.0/c/document/actions/add_to_center/batch?auto_rename=true"
    data = {
        "parent_id":"0",
        "container_id": container_id,
        "resource_list":[
            {
                "resource_id":resource_id,
                "type":"get"
            }
        ]
    }

    # 生成一个700-900之间的随机数
    diff = str(random.randint(700, 900))

    # 请求类型
    method_type = "POST"

    # 获取授权头
    authorization_header = auth_encrypt(request_url, access_token, mac_key, diff, method_type)
    
    # 设置请求头
    headers = {
        'Authorization': authorization_header,
        'sdp-app-id': app_id
    }
    try:
        # 发起GET请求并检查响应状态
        response = requests.post(url = request_url, json = data, headers = headers, timeout=10)
        response.raise_for_status()

        # 返回资源信息
        return True
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return False
    