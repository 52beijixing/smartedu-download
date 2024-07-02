from utils.command import welcome_interface,get_user_input, download_content

if __name__ == "__main__":
    # 显示欢迎界面
    welcome_interface()

    while True:
        # 获取用户输入的url地址
        web_url = get_user_input()
        # 下载
        download_content(web_url)
