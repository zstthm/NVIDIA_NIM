import pymysql
from openai import OpenAI


# 修改数据库连接函数
def connect_to_db():
    """
    使用 pymysql 连接到 MySQL 数据库
    """
    try:
        connection = pymysql.connect(
            host='localhost',  # 根据你的配置修改
            database='wiki_data',  # 你的数据库名
            user='root',  # 你的用户名
            password='123',  # 你的密码
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("成功连接到数据库")
        return connection
    except pymysql.MySQLError as e:
        print(f"数据库连接失败: {e}")
        return None


# 连接到数据库
connection = connect_to_db()


# 定义模糊查询函数
def exact_search(connection, search_keyword):
    """
    执行精确查询数据库，并返回结果。

    Args:
    - connection: 数据库连接对象
    - search_keyword (str): 查询关键字

    Returns:
    - list: 查询结果列表
    """
    if connection is None:
        print("数据库连接未成功，无法执行查询。")
        return []

    try:
        with connection.cursor() as cursor:
            # SQL查询语句，使用=进行精确匹配
            query = "SELECT text FROM wikipedia_pages WHERE title = %s;"
            # 执行查询，不需要在search_keyword两边添加%
            cursor.execute(query, (search_keyword,))
            results = cursor.fetchall()
            return results
    except pymysql.MySQLError as e:
        print(f"查询失败: {e}")
        return []


# 查询关键字
search_keyword = "天琴座"

# 执行模糊查询
search_results = exact_search(connection, search_keyword)

print("search_results:",search_results)

# 初始化OpenAI客户端
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="你的api"
)

# 创建聊天完成请求，将查询结果作为上下文传递给OpenAI
for result in search_results:
    # 截取前4000个字符以避免超出模型的最大上下文长度
    summary_prompt = "总结后续主要内容到100字以内，若是英语，翻译成中文：" + str(result['text'])[:3000]

    completion = client.chat.completions.create(
        model="microsoft/phi-3-mini-4k-instruct",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )

    # 流式处理生成的结果
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
