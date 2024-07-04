from utils.command import welcome_interface, get_text_file_input, get_user_input, download_content

if __name__ == "__main__":
    # 显示欢迎界面
    welcome_interface()

    # 获取txt文件中的链接进行处理
    get_text_file_input()

    while True:
        # 获取用户输入的url地址
        web_url = get_user_input()
        # 下载
        download_content(web_url)
