import redis


class RedisDatabase:
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        """
        初始化Redis连接
        :param host: Redis服务器地址
        :param port: Redis服务器端口
        :param db: 选择的数据库编号
        :param password: Redis密码（如果有）
        """
        self.client = redis.Redis(host=host, port=port, db=db, password=password)
        self.ping()  # 尝试连接到Redis服务器

    def ping(self):
        """
        检查Redis服务器是否可达
        """
        try:
            return self.client.ping()
        except redis.ConnectionError:
            print("无法连接到Redis服务器")
            return False

    def get(self, key):
        """
        获取一个键的值
        :param key: 键名
        :return: 键对应的值
        """
        return self.client.get(key)

    def set(self, key, value):
        """
        设置一个键值对
        :param key: 键名
        :param value: 值
        """
        self.client.set(key, value)

    def delete(self, key):
        """
        删除一个键
        :param key: 键名
        """
        return self.client.delete(key)

    def keys(self, pattern="*"):
        """
        查找所有符合给定模式的键
        :param pattern: 匹配模式
        :return: 符合模式的键列表
        """
        return self.client.keys(pattern)

    def exists(self, key):
        """
        检查键是否存在
        :param key: 键名
        :return: 如果键存在返回True，否则返回False
        """
        return self.client.exists(key)


# 使用示例
if __name__ == "__main__":
    db = RedisDatabase()  # 使用默认参数连接到本地Redis服务器

    # 设置键值对
    db.set("my_key", "my_value")

    # 获取键的值
    value = db.get("my_key")
    print(f"my_key: {value.decode('utf-8')}")  # 注意：Redis返回的是字节串，需要解码

    # 检查键是否存在
    print(f"Exists 'my_key': {db.exists('my_key')}")

    # 删除键
    db.delete("my_key")
    print(f"Exists 'my_key' after deletion: {db.exists('my_key')}")


'''HF 链接：https://huggingface.co/cloud-district/miqu-2
磁链：magnet:?xt=urn:btih:c0e342ae5677582f92c52d8019cc32e1f86f1d83&dn=miqu-2&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80
种子：https://files.catbox.moe/d88djr.torrent
来源：https://boards.4chan.org/g/thread/101514682#p101516633
   https://files.catbox.moe/d88djr.torrent

'''