from utils.command import welcome_interface, get_text_file_input, get_user_input, download_content, get_user_info, get_app_id

if __name__ == "__main__":
    # 显示欢迎界面
    welcome_interface()

    # 获取APP-ID
    app_id = get_app_id()

    # 获取用户输入的身份验证信息
    user_data = get_user_info(app_id)

    # 获取txt文件中的链接进行处理
    get_text_file_input(user_data, app_id)

    while True:
        # 获取用户输入的url地址
        web_url = get_user_input()
        # 下载
        download_content(web_url, user_data, app_id)
