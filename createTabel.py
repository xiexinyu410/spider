import pymysql
#用于创建表
# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'demo'
}

# 创建数据库连接
try:
    # 使用pymysql.connect()连接到MySQL数据库
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # 创建表的 SQL 语句
    create_table_query = """
    CREATE TABLE IF NOT EXISTS govendata(
    id INT AUTO_INCREMENT PRIMARY KEY,
    link VARCHAR(255) NOT NULL,
    document_name VARCHAR(255) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    subject_classification VARCHAR(255),
    issuing_agency VARCHAR(255),
    implementation_date DATE,
    drafting_date DATE,
    repeal_date DATE,
    release_date DATE,
    document_number VARCHAR(255),
    validity VARCHAR(255),
    source VARCHAR(255),
    index_number VARCHAR(255),
    subject_terms VARCHAR(255)
);

    """

    # 执行创建表的 SQL 语句
    cursor.execute(create_table_query)

    # 提交事务并关闭连接
    conn.commit()
    print("表 'govendata' 创建成功！")

except pymysql.MySQLError as err:
    print(f"数据库错误: {err}")

finally:
    if conn.open:
        cursor.close()
        conn.close()
