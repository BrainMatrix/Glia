import asyncio

from .base_workflow import BaseWorkflow
import os

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


class ExtractMsgIDWorkflow(BaseWorkflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def contains_chinese(self,text):
        return bool(re.search(r"[\u4e00-\u9fff]", text))

    async def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        directory = self.prev_result
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
                    and not self.contains_chinese(line)
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
                        print("before: ", matches)
                        res = get_translation_cache("en", "zh", matches)
                        print("after: ", res)
                        lines[line_number] = "msgstr " + '"' + res + '"' + "\n"
            with open(path, "w", encoding="utf-8") as file:
                file.writelines(lines)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )
        return self.process_result
