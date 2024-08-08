<h2 align="center">
    <p><img src="./images/logo.png" width="100" alt="logo"></p>
    <a href="https://github.com/52beijixing/smartedu-download">Smartedu-Download</a>
</h2>

<p align="center">
    帮助您下载国家中小学智慧教育平台的文件</br>
    支持视频、教材（课本）、原版课件（ppt、word、pdf格式）下载
</p>

<p align="center">
  <img src="https://img.shields.io/github/downloads/52beijixing/smartedu-download/total" alt="DownloadNum">
</p>

<p align="center">
    <a href="https://github.com/52beijixing/smartedu-download">
        <img src="./images/description.png" alt="description">
    </a>
</p>

## 2024/8/8特别说明
2024年8月7日下午，官方对原本的json文件进行了更新，去除了部分格式的地址信息，换域名大法失效，导致部分ppt、pptx、doc、docx课件无法下载，不登录下载方法失效。

但是，天无绝人之路，还有登录下载方法，该方法需要您输入一些用户信息，如果您对此有任何疑虑，请查看源代码并自行编译。代码开源，不再对此另行解释。

### 使用说明
1、访问 https://basic.smartedu.cn/ 并登录

2、按【F12】或右键【检查】，选择【控制台】执行下面代码（会自动黏贴需要的信息到剪贴板）
> 其中e5649925-441d-4a53-b525-51a2f1c4e0a8为APP-ID，可能会不固定，以软件提示中为准
<p align="center">
  <img src="./images/console.png" alt="Console">
</p>

```
copy(localStorage.getItem("ND_UC_AUTH-e5649925-441d-4a53-b525-51a2f1c4e0a8&ncet-xedu&token"))
```

3、打开软件，黏贴进去

4、和以前一样，输入链接

## 特别推荐和感谢
> 吾爱破解论坛【dtsuifeng】大佬

### 版本优点
1、支持win7、win10、win11系统32位及64位

2、提供GUI（图形界面）

3、其他功能优化和BUG修复

软件地址：https://www.52pojie.cn/thread-1937211-1-1.html

<p align="center">
    <a href="https://www.52pojie.cn/thread-1937211-1-1.html">
        <img src="./images/dtsuifeng.png" alt="dtsuifeng">
    </a>
</p>

## 使用须知
### 声明
版权所有 © 2024 52beijixing star0angel

本软件允许无限制地使用、复制、修改及分发，无论是否涉及费用，前提是上述版权声明及本授权声明在所有副本中得以保留。

本软件按“现状”提供，作者不做任何明示或暗示的保证，包括但不限于对适销性、特定用途的适用性及不侵权的保证。在任何情况下，无论基于合同、疏忽、侵权行为或其他，对于因使用或无法使用本软件而导致的特殊、间接、附带或后果性损害，作者均不承担责任。


## 使用方法
### 1、直接下载打包好的exe文件
https://github.com/52beijixing/smartedu-download/releases

### 2、本地使用python运行
1、下载项目文件（无git用户请自行网页下载）
```
git clone https://github.com/52beijixing/smartedu-download.git
```
2、进入项目代码路径
```
cd smartedu-download
```

3、安装环境依赖
```
pip install -U -r requirements.txt
```

4、运行项目
```
python main.py
```


## windows系统特殊提示
由于m3u8下载与合并比较复杂，所以软件本身下载功能会有一些小问题，所以windows系统用户可以借助【N_m3u8DL-CLI】与【FFmpeg】进行下载。

下载地址：https://github.com/nilaoda/N_m3u8DL-CLI/releases/download/3.0.2/N_m3u8DL-CLI_v3.0.2_with_ffmpeg_and_SimpleG.zip

### 使用exe文件的用户
请将【N_m3u8DL-CLI_v3.0.2.exe】【ffmpeg.exe】两个文件放置到【smartedu-download.exe】同一个目录下，然后运行【smartedu-download.exe】
<p align="center">
  <img src="./images/windows_tip_one.png" alt="windows_tip_one">
</p>

### 使用源代码运行的用户
请将【N_m3u8DL-CLI_v3.0.2.exe】【ffmpeg.exe】两个文件放置到smartedu-download目录下，然后运行【main.py】

<p align="center">
  <img src="./images/windows_tip_two.png" alt="windows_tip_two">
</p>
