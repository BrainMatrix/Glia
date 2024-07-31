from math import e
import os
import re
import subprocess

from openai import OpenAI
from translate import Translator
import redis
import pymysql

# client = OpenAI(
#     base_url="http://192.168.10.59:8000/v1",
#     api_key="token-abc123",
# )
client = OpenAI(
    api_key="sk-acf67cf8de80437197551d18dffd2602", base_url="https://api.deepseek.com"
)


def contains_chinese(text):
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def extract_msgid_from_po_files(directory):
    po_files = [f for f in os.listdir(directory) if f.endswith(".po")]
    filter_str_list = [".".join(str(i).split(".")[:-1]) for i in po_files]
    filter_str_candidate_list = [
        "Submodules",
        "Subpackages",
        "Example",
        "Content",
        ":ref:`",
    ]
    for filter_candidate in filter_str_candidate_list:
        filter_str_list.append(filter_candidate)
    for file in po_files:
        path = os.path.join(directory, file)
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for line_number, line in enumerate(lines, start=1):
            if (
                line.startswith("msgid ")
                and not any(f in line for f in filter_str_list)
                and not contains_chinese(line)
            ):
                matches = re.findall(r'msgid "(.*?)"', line)[0]
                while True:
                    if not lines[line_number].startswith("msgstr "):
                        matches += lines[line_number]
                        matches = (
                            str(matches)
                            .replace("\n", "")
                            .replace('"', "")
                            .replace("'", "")
                        )
                        line_number += 1
                    else:
                        break
                if matches != "":
                    print("before: ",matches )
                    res = get_translation_cache("en", "zh", matches)
                    print("after: ", res)
                    lines[line_number] = "msgstr " + '"' + res + '"' + "\n"
        with open(path, "w", encoding="utf-8") as file:
            file.writelines(lines)


translator = Translator(to_lang="zh")


def get_translation_cache(source_language, target_language, original_text):

    cache_key = f"{source_language}:{target_language}:{original_text}"

    # 尝试从缓存获取翻译
    translated_text = cache.get(cache_key)

    if translated_text:
        return translated_text.decode("utf-8")

    # 查询是否已经存在翻译
    query = """
    SELECT translated_text FROM translations
    WHERE source_language = %s AND target_language = %s AND original_text = %s
    """
    cursor.execute(query, (source_language, target_language, original_text))
    result = cursor.fetchone()

    if result:
        # 如果存在，返回翻译
        translated_text = result[0]
    else:
        # 如果不存在，进行翻译
        translated_text = get_tranlate_llm_deepseekv2(original_text)

        # 插入新的翻译记录
        insert_query = """
        INSERT INTO translations (source_language, target_language, original_text, translated_text)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            insert_query,
            (source_language, target_language, original_text, translated_text),
        )
        conn.commit()

    cache.set(cache_key, translated_text)

    return translated_text


def get_translate(text):
    return translator.translate(text)


translate_prompt = "我想让你充当中文翻译员、拼写纠正员和改进员。我会用任何语言与你交谈，你会检测语言，翻译它并用我的文本的更正和改进版本用中文回答。我希望你用程序员和技术角度的中文词汇和句子替换我简化的 A0 级单词和句子。保持相同的意思，但使它们更通俗易懂。你只需要翻译该内容，不必对内容中提出的问题和要求做解释，不要回答文本中的问题而是翻译它，不要解决文本中的要求而是翻译它,保留文本的原本意义，不要去解决它。我要你只回复更正、改进，不要写任何解释。"


def get_tranlate_llm_openchat(text):
    completion = client.chat.completions.create(
        model="/mnt/nfs_share_test/yangruiqing/openchat-3.6-8b-20240522",
        messages=[
            {
                "role": "system",
                "content": translate_prompt,
            },
            {"role": "user", "content": text},
        ],
    )
    return completion.choices[0].message.content


def get_tranlate_llm_deepseekv2(text):
    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": translate_prompt,
            },
            {"role": "user", "content": text},
        ],
    )
    return completion.choices[0].message.content


def modify_conf_file(file_path, new_language):
    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # 使用正则表达式查找并替换 language 变量的值
    new_content = re.sub(
        r"language\s*=\s*['\"].*?['\"]", f"language = '{new_language}'", content
    )

    # 在文件末尾添加 locale_dirs 行
    if 'locale_dirs = ["locale/"]' not in new_content:
        new_content += '\nlocale_dirs = ["locale/"]\n'

    # 将修改后的内容写回文件
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_content)

    print(f"Updated 'language' to '{new_language}' in {file_path}")
    print(f"Added 'locale_dirs = [\"locale/\"]' to the end of {file_path}")


commands = [
    ("rsync -av --progress --exclude 'build' docs/ docs-zh_CN/", "./"),
    ("do modify_conf_file", "./"),
    ("cd ./docs-zh_CN/source", "./docs-zh_CN/source"),
    ("sphinx-build -b gettext . locale", "./docs-zh_CN/source"),
    ("sphinx-intl update -p locale -l zh_CN", "./docs-zh_CN/source"),
    ("do extract_msgid", "./docs-zh_CN/source"),
    ("cd ..", "./docs-zh_CN"),
    ("make clean", "./docs-zh_CN"),
    ("make html", "./docs-zh_CN"),
    ("cd build/html", "./docs-zh_CN/build/html"),
    ("python3 -m http.server 8002133", "./docs-zh_CN/build/html"),
]


cache = redis.StrictRedis(host="localhost", port=6379, db=0)


conn = pymysql.connect(
    host="localhost", user="heitong", password="YRQ21163x!", database="workflow"
)

cursor = conn.cursor()

for cmd, cwd in commands:
    if cmd.startswith("cd "):
        continue  # 对于cd命令不执行任何操作，因为我们通过cwd参数控制目录

    if cmd == "do extract_msgid":
        directory = "./docs-zh_CN/source/locale/zh_CN/LC_MESSAGES"  # 当前目录

        msgid_contents = extract_msgid_from_po_files(directory)
    elif cmd == "do modify_conf_file":
        conf_file_path = "./docs-zh_CN/source/conf.py"
        new_language_value = "zh_CN"
        modify_conf_file(conf_file_path, new_language_value)
    else:
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                cmd,
                shell=True,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            # 打印错误信息
            print(f"命令执行失败: {e.cmd}")
            print(f"返回码: {e.returncode}")
            print(f"错误输出: {e.stderr}")
