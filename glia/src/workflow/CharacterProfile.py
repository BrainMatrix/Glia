class CharacterProfile:

    def get_init_prompt(self, user_words=""):
        raise NotImplementedError
    
    def get_summary_prompt(self):
        raise NotImplementedError
    
    def get_more_novel(self):
        raise NotImplementedError

    def get_chat_prompt(self, long_memo="", short_memo=""):
        raise NotImplementedError
    
    def get_combine_memory_prompt(self, memo="", to_convert=[]):
        raise NotImplementedError
    
    #Decision maker for web search#
    def get_decision_prompt(self, user_words="", short_memo=""):
        raise NotImplementedError
    
    def get_web_info_prompt(self, user_words="", text=""):
        raise NotImplementedError
    
    def get_chat_prompt_web(self, long_memo="", short_memo="", web_memo=""):
        raise NotImplementedError
    #Decision maker for web search#

    def get_save_key_prompt(self, user_text=""):
        raise NotImplementedError
    
    def get_key_prompt(self, user_text=""):
        raise NotImplementedError
    