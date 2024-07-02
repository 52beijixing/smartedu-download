import os
from colorama import Fore, Style
from utils.tool import get_url_param
from utils.download import download_file_from_url, download_video
from utils.getInfo import *



def print_colored(text, color):
    """打印彩色文本"""
    print(getattr(Fore, color) + text + Style.RESET_ALL)

def welcome_interface():
    print_colored("-------------------------------------------------------------", "BLUE")
    print_colored("\t\t欢迎使用Smartedu-Download!", "GREEN")
    print(f"\n当前版本：{Fore.CYAN}v1.0.0 {Style.RESET_ALL}")
    print(f"\n项目地址：{Fore.CYAN}https://github.com/52beijixing/smartedu-download{Style.RESET_ALL}")
    
def get_user_input():
    print_colored("-------------------------------------------------------------", "BLUE")
    print_colored("请输入网页地址(输入exit退出):", "YELLOW")
    web_url = input(">>> ")
    print_colored("-------------------------------------------------------------", "BLUE")
    return web_url


def download_content(web_url: str):
    data = []
    # url判断
    if web_url.startswith("https://basic.smartedu.cn/tchMaterial/detail?contentType=assets_document"):
        contentId = get_url_param(web_url, "contentId")
        data = get_textbook_info(contentId)
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/classActivity"):
        activityId = get_url_param(web_url, "activityId")
        data = get_bookcoursebag_info(activityId)
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/prepare/detail?resourceId"):
        resourceId = get_url_param(web_url, "resourceId")
        data = get_courseware_info(resourceId)
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/experimentLesson"):
        courseId = get_url_param(web_url, "courseId")
        data = get_experiment_course_info(courseId)
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/prepare/detail?lessonId"):
        lessonId = get_url_param(web_url, "lessonId")
        data = get_one_teacher_info(lessonId)
    elif web_url.startswith("https://jpk.basic.smartedu.cn/yearQualityCourse?courseId"):
        courseId = get_url_param(web_url, "courseId")
        data = get_basis_info(courseId) 
    elif web_url.startswith("https://basic.smartedu.cn/qualityCourse?courseId"):
        courseId = get_url_param(web_url, "courseId")
        data = get_subject_info(courseId)
    elif web_url.startswith("https://basic.smartedu.cn/syncClassroom/basicWork/detail?contentType=assets_document&contentId"):
        contentId = get_url_param(web_url, "contentId")
        data = get_homework_info(contentId)
    elif web_url == "exit":
        print("退出程序")
        os._exit(0)
    else:
        print(f"您输入的链接暂未支持!\n请前往 {Fore.CYAN}https://github.com/52beijixing/smartedu-download/issues{Style.RESET_ALL} 反馈！")
    
    if data is None:
        print("获取数据出错！")
        return
    
    current_path  = os.getcwd()
    for item in data:
        dir_name = item.get("dir_name")
        dir_name = dir_name.replace(" ", "_")
        file_name = item.get("file_name")
        file_name = file_name.replace(" ", "_")
        file_url = item.get("file_url")
        file_format = item.get("file_format")
        #file_size = item.get("file_size")
        path = os.path.join(current_path, dir_name)

        if file_format == "mp4" or file_format == "m3u8":
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
