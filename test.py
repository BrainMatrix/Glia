from math import e
import os
import re
import subprocess

from openai import OpenAI
from translate import Translator


def contains_chinese(text):
    # 使用正则表达式匹配中文字符
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
                    print(matches)
                    lines[line_number] = "msgstr " + '"' + matches + '"' + "\n"
        with open(path, "w", encoding="utf-8") as file:
            file.writelines(lines)
        # print(file)
        # print("===" * 22)
        # for line in lines:
        #     print(line)
        # print("===" * 22)

extract_msgid_from_po_files(
    "/root/hgln_project/Glia/docs-zh_CN/source/locale/zh_CN/LC_MESSAGES"
)
