import requests as r #个人书写习惯
import requests
import re
import wget
import zipfile
import hashlib
import os
import shutil
from html2docx import html2docx


def get_10(url):
    return r.get(url,timeout=10)

def get_md5(filename):
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()

def get_md5_from_str(s):
    md5_hash = hashlib.md5()
    md5_hash.updtae(s)
    return md5_hash.hexdigest()

def getExam(resource_id: str):
    try:
        SPLIT = ""

        #我测试出来是12都有，这里暂时用1
        basic_info_url = f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/examinationpapers/resources/details/{resource_id}.json"
        res = get_10(basic_info_url)
        res.raise_for_status()

        basic_info_data = res.json()
        container_id = basic_info_data.get("container_id")

        #我测试出来是12都有，这里暂时用1
        detailed_info_url = f"https://bdcs-file-1.ykt.cbern.com.cn/xedu_cs_paper_bank/api_static/papers/{container_id}_{resource_id}/data.json"
        res = get_10(detailed_info_url)
        res.raise_for_status()

        detailed_info_data = res.json()
        
        #先拉取题目信息然后匹配出顺序
        #每个dict的结构分布
        """
        {{对应id的唯一id}:{"ref_path":资源地址，由location给出, ##其实后来用不到，但是万一哪天有用了呢
         "question_html":题目的html原格式，合并题目和选项，题目为首行,list格式表示可能有多题
         "source_zip":题目的解析视频的zip，里面包含多种文件}
         "source_zip_md5":zip的md5方便验证文件准确性}}
        """
        ques_datas = {}
        for ques_part_url in detailed_info_data["question_path_list"]:
            ques_url = f"https://bdcs-file-1.ykt.cbern.com.cn/{ques_part_url}"
            res = get_10(ques_url)
            res.raise_for_status()
            data = res.json()
            #遍历数据
            for per in data:
                ##开始构造ques_data dict
                ques_data = {}
                content = per["content"]
                ##获取ref_path
                location = content["location"]
                ref_path = re.match(r"[\w]*://[-.\w\d]*/*",location).group() #正则匹配地址
                ref_path = ref_path[:-1:] #去尾
                ##zip相关
                sys_packing_result = per["source"]["custom_properties"]["sys_packing_result"]
                source_zip = sys_packing_result["result"]
                source_zip = source_zip.replace("${ref-path}",ref_path)
                pre = "cs_path:"
                if source_zip.startswith(pre):
                    source_zip = source_zip[len(pre)::]
                source_zip_md5 = sys_packing_result["md5"]
                ##题目相关
                question_html = []
                items = content["items"]
                for item in items:
                    prompt = item["prompt"]#题干
                    choices = item["choices"]#选项
                    #遍历并找出选项html
                    choices_text = list(map(lambda x: f"<div><p style=\"text-align: justify;\"><span>{x["identifier"]}.</span></p></div>" + x["text"], choices))
                    text_list = [prompt] + choices_text
                    text = SPLIT.join(text_list)
                    text = text.replace("${ref-path}",ref_path)
                    question_html.append(text)
                ##获取唯一id
                id = content["identifier"]
                ques_datas[id] = {"ref_path":ref_path,"question_html":question_html,"source_zip":source_zip,"source_zip_md5":source_zip_md5}

        html = ""
        title = detailed_info_data["title"]
        output_folder = f"{title}-习题及解析"
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        parts = detailed_info_data["parts"]
        count = 1
        for part in parts:
            part_html = []
            title = part["title"]
            title = f"<div><p style=\"text-align: justify;\"><span>{title}</span></p></div>"
            part_html.append(title)

            paper_questions = part["paper_questions"]
            for ques in paper_questions:
                id = ques["id"]
                if id in ques_datas.keys():
                    que_data = ques_datas[id]
                    part_html += list(map(lambda x: f"<div><p style=\"text-align: justify;\"><span>{count}.</span></p></div>" + x, que_data["question_html"]))
                    zip_url = que_data["source_zip"]
                    zip_md5 = que_data["source_zip_md5"]
                    wget.download(zip_url,f"{zip_md5}.zip")
                    if not get_md5(f"{zip_md5}.zip") == zip_md5:
                        print(f"下载试卷时出现问题，resourceId={resource_id}\n请到https://github.com/52beijixing/smartedu-download/issues反馈，并附上截图！")
                        raise
                    with zipfile.ZipFile(f"{zip_md5}.zip") as zip_ref:
                        zip_ref.extractall(zip_md5)
                    mp4_path = os.path.join(zip_md5, "xitimp4")
                    for time in os.listdir(mp4_path):
                        inner_mp4_path = os.path.join(mp4_path, time)
                        for filename in os.listdir(inner_mp4_path):
                            file = os.path.join(inner_mp4_path, filename)
                            target = os.path.join(output_folder, f"{count}-{filename}")
                            shutil.copy(file,target)
                    
                    os.remove(f"{zip_md5}.zip")
                    shutil.rmtree(zip_md5)
                    count += 1
                else:
                    print(f"下载试卷时出现问题，resourceId={resource_id}\n请到https://github.com/52beijixing/smartedu-download/issues反馈，并附上截图！")
                    raise

            html += SPLIT.join(part_html)
        
        print("")
        #print(html)
        #print("\n\n\n")

        title = detailed_info_data["title"]
        filename = os.path.join(output_folder,f"习题-{title}.docx")
        buf = html2docx(html, title=title)
        with open(filename, "wb") as fp:
            fp.write(buf.getvalue())
        #TODO: 还未实现对于latex的解析
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求过程中发生错误: {req_err}")
    except ValueError:
        print("解析错误：响应内容不是有效的JSON格式。")
    except Exception as e:
        print(f"未知错误: {e}")
