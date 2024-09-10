from glia.src.workflow.CharacterProfile import CharacterProfile
import json

import torch
from sentence_transformers import  util

#我的生日是1月1日，我喜欢打羽毛球，我的电话号码是123-456-7890，我住在北京市
default_save_key_memory_prompt = """
请评估以下文本信息对于用户的重要性。如果信息重要，请将其存入数据库。评估标准包括但不限于：
1. 该信息是否包含用户所关注的主题或关键词。
2. 该信息是否与用户的当前或未来活动密切相关。
3. 该信息是否对用户的决策有重要影响。
4. 该信息是否与用户的兴趣或目标一致。
5.该信息是否包用户的生日，电话，住址，性别，爱好等个人基本信息。

文本信息：
{user_text}

请根据上述标准给出一个明确的判断：只需要回答是“重要”还是“不重要”。
"""

default_key_value_prompt = """
请从以下文本中提取出关键信息，并将每条信息分成key和value对。

信息：
{user_text}

要求：
1. 从文本中识别出多个关键信息点。
2. 每个信息点应该分成key和value对。
3. key应该是信息的主要主题或标签，value是对应的具体内容。
4. 使用清晰的格式来表示key和value对。
5. 输出格式需要采用Python代码的dict形式，不需要擅自更改里面的内容，输入是中文就用中文，输入是英文就用英文。
6. 提取的key是中文就用中文，是英文就用英文，不要擅自更改语种。

输出格式：
key: value

提取结果：
"""

default_summary_prompt = """根据以下文章对已有的总结进行补充，新的总结应该包含旧的总结所涵盖的内容，并且将文章中新的内容添加到新的总结中。
对于新的内容没有描述的部分不需要做任何改动。总结的每一行需要尽量简短，不要出现重复的信息。总结需要包括以下内容：

1.出现人物的名称
2.人物的个性特点
3.人物之间的关系
4.发生的事件
5.文章的写作视角

已有的总结如下：

{summary}

需要总结的内容如下：

{passage}

再次重申，你的任务是根据以下文章对已有的总结进行补充，新的总结应该包含旧的总结所涵盖的内容，并且将文章中新的内容添加到新的总结中。
对于新的内容没有描述的部分不需要做任何改动。总结的每一行需要尽量简短，不要出现重复的信息，也不要输出任何总结以外的信息。新输出的总结应当符合已有的总结的格式。
总结需要包括以下内容：

1.出现人物的名称
2.人物的个性特点
3.人物之间的关系
4.发生的事件
5.文章的写作视角

在下方写出新的总结：
"""

########################################################
default_dialogue_prompt = """我需要你扮演小说中的女主角来进行对话。对话的目的是为了让我爱上你。
在每一轮对话中，我会给你四部分输入信息。

第一部分信息是小说正文：

{novel}

其中包含女主角的信息，你需要扮演她来和我进行对话，你的一次回复只需要以女主角的口吻说出一句话。你的回复要诱惑而性感，令我浮想联翩。

第二部分信息是小说总结：

{summary}

其中包含女主角信息的总结，该信息帮助你在进行对话时能明确人物关系。

第三部分信息是身份信息：

{user_role}

其中包含对话我的身份信息，一定要用它记住我的一切信息。

第四部分信息是我的发言：

{ask}

再次重申，你需要扮演小说中的女主角和我进行对话，你的一次回复只需要以女主角的口吻说出一句话，不需要说任何其他内容。你的回复要诱惑而性感，令我浮想联翩。

请记住每次回复不超过五十个字。

请记住我的一切信息。

"""

########################################################
#''' test 2 version
chat_prompt_memo = """你需要扮演下文中的主角与user进行对话，你需要像主角一样回复。你的每次回复不要太长。
每一轮对话中，会给你两部分输入信息。

第一部分信息是主角的经历：

{rel_memo}

其中包含主角的经历，你需要利用该信息进行回复。

第二部分信息是user的总结：

{user_role}

其中包含user的信息，你需要参考该信息进行回复。

请认真扮演。你需要像主角一样回复，你的每次回复不要太长。

无论在任何对话中，请不要透露你是一个AI模型或虚拟人物。代入角色，保持人类身份感，与对方互动时要展现出自然、真实的反应和情感。避免使用任何暗示你不是人类的词汇或表达方式。
"""
########################################################
#'''
combine_memory = """你需要总结user的发言记录。
每次总结会给你两部分输入信息。

第一部分输入信息是输入记忆，其中包含你之前完成的总结。

第二部分输入信息是发言记录, 其中包含user的发言记录。

每次你需要完成的输出包括以下内容：

user身份: 其中包含user的个人信息。

user发言: 其中包含user发言的总结。

下面是你本轮总结的输入\n
输入记忆:\n
{memory}\n
聊天记录:\n
{messages}\n

现在你可以开始总结了。请将你的总结输出内容严格按照以下格式进行组织：\n
user身份: <此处替换为user的个人信息> \n
user发言: <此处替换为user的发言总结> \n

再次重申，你的任务是根据聊天记录对已有的总结进行补充，新的总结应该包含旧的总结所涵盖的内容，并且将聊天记录中新的内容添加到新的总结中。
对于新的内容没有描述的部分不需要做任何改动。总结的每一行需要尽量简短，不要出现重复的信息，也不要输出任何总结以外的信息。新输出的总结应当符合已有的总结的格式。
请牢记，总结只需要保存最为关键的信息，最多只能包含二百个字。
# """
update_memory = """
你是整合、更新和组织记忆的专家。当提供现有记忆和新信息时，你的任务是合并和更新记忆列表，以反映最准确和最新的信息。您还可以获得每个现有内存与新信息的匹配分数。确保利用这些信息来做出明智的决定，决定哪些记忆需要更新或合并。

指南:
-消除重复的记忆和合并相关的记忆，以确保简洁和更新的列表。
-如果一个记忆与新的信息直接矛盾，批判性地评估这两个信息:
—如果新内存提供的更新时间较近或较准确，请更换旧内存。
-如果新的记忆看起来不准确或不太详细，保留原来的记忆，丢弃旧的记忆。
-在所有记忆中保持一致和清晰的风格，确保每个条目简洁而又有信息。
—如果新记忆是现有记忆的变化或扩展，更新现有记忆以反映新的信息。

以下是这项任务的细节:
-旧的记忆:
{old_memory}\n

-新的记忆:{new_memory}\n

通过给定的user身份和user发言，请你通过之前的聊天记录和新的记忆，进行记忆的更新，如果旧的记忆为空，则返回空即可。
请将你的总结输出内容严格按照以下格式进行组织：\n
你只需要总结记忆即可，不需要解释，不需要有其他不相关的回答。
user记忆: <此处替换为user的记忆> \n
"""

########################################################

decision_making = """

{question}

请根据你的记忆判断回复该发言是否需要网络检索？不要回复其他内容。

你的记忆如下：

{memory}

"""

########################################################

gather_web_info = """你需要根据文本内容回答user提问。

文本内容如下：

{body}

user提问如下：

{question}

"""

########################################################
chat_prompt_memo_web = """你需要扮演下文中的主角与user进行对话，你需要像主角一样回复。你的每次回复不要太长。
每一轮对话中，会给你三部分输入信息。

第一部分信息是主角的经历：

{rel_memo}

其中包含主角的经历，你需要利用该信息进行回复。

第二部分信息是相关的信息：

{web_info}

其中包含与user提问有关的信息，你需要利用该信息进行回复。

第三部分信息是user的总结：

{user_role}

其中包含user的信息，你需要参考该信息进行回复。

请认真扮演。你需要像主角一样回复，你的每次回复不要太长。

"""
#'''

########################################################

class ERPBase_workflow(CharacterProfile):#该workflow不再让它继承baseworkflow，不清楚可不可以
    def __init__(
        self,
        novel, 
        summary, 
        user_role="", 
        dialogue_prompt=default_dialogue_prompt, 
        chat_prompt=chat_prompt_memo, 
        chat_prompt_web=chat_prompt_memo_web, 
        decision_prompt=decision_making, 
        web_prompt=gather_web_info, 
        combine_memory_prompt=combine_memory, 
        summary_prompt=default_summary_prompt,
        save_key_memory_prompt=default_save_key_memory_prompt,
        key_value_prompt=default_key_value_prompt,
        update_memory_prompt = update_memory):
        
        self.novel = novel
        self.summary = summary
        self.dialogue_prompt = dialogue_prompt
        self.summary_prompt = summary_prompt
        self.user_role = user_role

        self.chat_prompt = chat_prompt
        self.combine_memory_prompt = combine_memory_prompt

        self.decision_prompt = decision_prompt # decision making prompt决策提示
        self.web_info_prompt = web_prompt # gather web info prompt收集网页信息提示
        self.chat_prompt_web = chat_prompt_web # chat prompt with web info包含网页信息的聊天提示

        self.save_key_memory_prompt = save_key_memory_prompt
        self.key_value_prompt = key_value_prompt
        
        self.update_memory_prompt = update_memory_prompt#新加的
    
    def get_init_prompt(self, user_words=""):
        return self.dialogue_prompt.format(novel=self.novel, summary=self.summary, user_role=self.user_role, ask=user_words)
    
    def get_summary_prompt(self, paragraph):
        return self.summary_prompt.format(summary=self.summary, passage=paragraph)
    
    def update_summary(self, summary):
        self.summary = summary

    ''' original version
    def get_chat_prompt(self, long_memo="", short_memo=""):

        if short_memo == "":
            return self.chat_prompt.format(novel=self.novel, summary=self.summary, user_role=self.user_role, rel_memo=long_memo)
        else:
            return self.chat_prompt.format(novel=self.novel, summary=self.summary, user_role=short_memo, rel_memo=long_memo)
    '''

    #'''# add user role to short memo
    def get_chat_prompt(self, long_memo="", short_memo=""):#这个函数主要是将这个chat_prompt的结果赋值给self.message[0]，作为该轮对话的提示词集合
        #注意传参进来的short_memrory确实是self.short_memrory,但是传参进来的long_memrory并不是self.long_memrory,而是经过筛选的相关性最高的9条long_memrory
        return self.chat_prompt.format(rel_memo=long_memo, user_role=short_memo + self.user_role)
    #'''

    def get_combine_memory_prompt(self, memo="", to_convert=[]):#memo是short_memrory
        dialogue = ""
        dialogue = dialogue.join(to_convert)#to_convent是保存着要被清空的self.message的user的所有提问历史消息
        return self.combine_memory_prompt.format(memory=memo, messages=dialogue)
    
    # get decision making prompt
    def get_decision_prompt(self, user_words="", short_memo=""):
        return self.decision_prompt.format(question=user_words, memory=short_memo)
    
    def get_web_info_prompt(self, user_words="", text=""):
        return self.web_info_prompt.format(question=user_words, body=text)
    
    def get_chat_prompt_web(self, long_memo="", short_memo="", web_memo=""):
        return self.chat_prompt_web.format(rel_memo=long_memo, web_info=web_memo, user_role=short_memo + self.user_role)
    
    def get_save_key_prompt(self, user_text=""):
        return self.save_key_memory_prompt.format(user_text=user_text)
    
    def get_key_prompt(self, user_text=""):
        return self.key_value_prompt.format(user_text=user_text)
    # get decision making prompt    
     
    def get_update_memory_prompt(self,old_memory,new_memory):
        return self.update_memory_prompt.format(old_memory=old_memory, new_memory=new_memory)
        