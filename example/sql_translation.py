import psycopg2
from psycopg2 import sql

"""
CREATE DATABASE workflow;

CREATE USER 'heitong'@'localhost' IDENTIFIED BY 'YRQ21163x!';
GRANT ALL PRIVILEGES ON workflow.* TO 'heitong'@'localhost';
FLUSH PRIVILEGES;


DROP TABLE IF EXISTS translations;
CREATE TABLE translations (
    id SERIAL PRIMARY KEY,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    original_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_language, target_language, original_text(255))
);
CREATE INDEX idx_translations_lookup ON translations (source_language, target_language, original_text(255));


"""


# def get_translation_cache(source_language, target_language, original_text):
#     # 连接到数据库
#     conn = psycopg2.connect(
#         dbname="workflow",
#         user="heitong",
#         password="YRQ21163x!",
#         host="localhost",
#     )
#     cur = conn.cursor()

#     # 查询是否已经存在翻译
#     cur.execute(
#         """
#         SELECT translated_text FROM translations
#         WHERE source_language = %s AND target_language = %s AND original_text = %s
#     """,
#         (source_language, target_language, original_text),
#     )

#     result = cur.fetchone()

#     if result:
#         # 如果存在，返回翻译
#         translated_text = result[0]
#     else:
#         # 如果不存在，进行翻译
#         translated_text = "test yrq"  # 你的翻译函数

#         # 插入新的翻译记录
#         cur.execute(
#             """
#             INSERT INTO translations (source_language, target_language, original_text, translated_text)
#             VALUES (%s, %s, %s, %s)
#         """,
#             (source_language, target_language, original_text, translated_text),
#         )get_translation_cache
#         conn.commit()

#     cur.close()
#     conn.close()

#     return translated_text


import pymysql
import redis
import timeit

cache = redis.StrictRedis(host="localhost", port=6379, db=0)


conn = pymysql.connect(
    host="localhost", user="heitong", password="YRQ21163x!", database="workflow"
)

cursor = conn.cursor()


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
        translated_text = "你好啊"

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


def get_translation(source_language, target_language, original_text):

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
        translated_text = "你好啊"

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

    return translated_text


if __name__ == "__main__":

    timer = timeit.Timer(lambda: get_translation("en", "zh_CN", "Hello, world sajkl"))

    time_taken = timer.timeit(number=10000)
    print(f"Time taken: {time_taken} seconds")

    timer = timeit.Timer(
        lambda: get_translation_cache("en", "zh_CN", "Hello, world jasdn")
    )

    time_taken = timer.timeit(number=10000)

    print(f"Time taken: {time_taken} seconds")

    cursor.close()
    conn.close()
