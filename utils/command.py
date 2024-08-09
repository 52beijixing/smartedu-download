import os
from utils.tool import get_url_param, sanitize_filename, replace_domain
from utils.download import download_file_from_url, download_video
from utils.getInfo import *


def welcome_interface():
    print("-------------------------------------------------------------")
    print("\t\t欢迎使用Smartedu-Download!")
    print(f"\n当前版本：v1.1.0 ")
    print(f"\n项目地址：https://github.com/52beijixing/smartedu-download")
    

def get_user_input():
    print("-------------------------------------------------------------")
    print("请输入网页地址(输入exit退出):")
    web_url = input(">>> ")
    print("-------------------------------------------------------------")
    return web_url


def get_text_file_input(user_data: str, app_id: str):
    file_name = "smartedu_download.txt"
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            # 遍历文件的每一行
            for line in file:
                # 去除每行末尾的换行符（如果有的话）
                line = line.rstrip('\n')
                if line:  # 这里检查line是否非空
                    print("-------------------------------------------------------------")
                    download_content(line, user_data, app_id)


def download_content(web_url: str, user_data: str, app_id: str):
    # 域名替换
    web_url = replace_domain(web_url)
    data = []
    # url判断
    if web_url.startswith("https://basic.smartedu.cn/tchMaterial/detail?contentType=assets_document"):
        contentId = get_url_param(web_url, "contentId")
        data = [get_textbook_info(contentId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/classActivity"):
        activityId = get_url_param(web_url, "activityId")
        data = [get_bookcoursebag_info(activityId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/prepare/detail?resourceId"):
        resourceId = get_url_param(web_url, "resourceId")
        data = [get_courseware_info(resourceId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/experimentLesson"):
        courseId = get_url_param(web_url, "courseId")
        data = [get_experiment_course_info(courseId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/prepare/detail?lessonId"):
        lessonId = get_url_param(web_url, "lessonId")
        data = [get_one_teacher_info(lessonId, user_data, app_id)]
    elif web_url.startswith("https://jpk.basic.smartedu.cn/yearQualityCourse?courseId"):
        courseId = get_url_param(web_url, "courseId")
        data = [get_basis_info(courseId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/qualityCourse?courseId"):
        courseId = get_url_param(web_url, "courseId")
        data = [get_subject_info(courseId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/basicWork/detail?contentType=assets_document&contentId"):
        contentId = get_url_param(web_url, "contentId")
        data = [get_homework_info(contentId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/sedu/detail?contentType=assets_video&contentId"):
        contentId = get_url_param(web_url, "contentId")
        data = [get_homework_info(contentId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/wisdom/detail?contentType=assets_video&contentId"):
        contentId = get_url_param(web_url, "contentId")
        data = [get_wisdom_info(contentId, user_data, app_id)]
    elif web_url.startswith("https://basic.smartedu.cn/schoolService/detail?contentType=thematic_course&contentId"):
        contentId = get_url_param(web_url, "contentId")
        data = get_thematic_infos(contentId, user_data, app_id)
    elif web_url == "exit":
        print("退出程序")
        os._exit(0)
    else:
        print(f"您输入的链接暂未支持!\n请前往 https://github.com/52beijixing/smartedu-download/issues 反馈！")
    
    if data is None:
        print("获取数据出错！")
        return
    
    current_path  = os.getcwd()
    for per_data in data:
        for item in per_data:
            teacher_name = item.get("teacher_name", "")
            dir_name = item.get("dir_name")
            if not teacher_name:
                dir_name = sanitize_filename(dir_name)
            else:
                dir_name = sanitize_filename("["+teacher_name+"]"+dir_name)
            file_name = item.get("file_name")
            file_name = sanitize_filename(file_name)
            file_url = item.get("file_url")
            file_format = item.get("file_format")
            #file_size = item.get("file_size")
            path = os.path.join(current_path, dir_name)

            if file_format == "mp4" or file_format == "m3u8" or file_format == "avi" or file_format == "flv":
                try:
                    download_video(file_url, path, file_name)
                except Exception as e:
                    print(f"下载视频时发生错误: {e}")
            else:
                print(f"正在下载 {file_name}.{file_format} ...")
                try:
                    full_path = download_file_from_url(file_url, path, file_name)
                    print(f"下载完成，文件保存在 {full_path}")
                except Exception as e:
                    print(f"下载课件时发生错误: {e}")


def get_user_info(app_id):
    print("-------------------------------------------------------------")
    print("请登录网站，打开控制台，执行获取用户身份验证信息的命令:\n")
    print(f'copy(localStorage.getItem("ND_UC_AUTH-{app_id}&ncet-xedu&token"))\n')
    print("-------------------------------------------------------------")
    print("请输入您的身份验证信息:")
    user_info = input(">>> ")
    return user_info


def get_app_id():
    url = 'https://auth.smartedu.cn/uias/login'
    try:
        # 发起GET请求并检查响应状态
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
         # 正则表达式模式，用于匹配 sdpAppId 的值
        pattern = r'sdpAppId: "([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"'
        
        # 使用 re.search 在 HTML 内容中搜索匹配项
        match = re.search(pattern, html_content)
        
        # 如果找到了匹配项，则返回 UUID；否则返回 None
        return match.group(1) if match else None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
    
    return None
