import re
import pymysql
import json
import os
#将信息插入数据库
# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'demo'
}

# 存放 JSON 数据的文件夹路径
json_folder_path = './content'

# 创建数据库连接
try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # 插入数据的 SQL 语句
    insert_query = """
    INSERT INTO govendata (link, document_name, content, subject_classification, issuing_agency, implementation_date, drafting_date, repeal_date, release_date, document_number, validity, source, index_number, subject_terms)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    # 遍历文件夹中的所有 JSON 文件
    for filename in os.listdir(json_folder_path):
        # 只处理 JSON 文件
        if filename.endswith('.json'):
            file_path = os.path.join(json_folder_path, filename)

            # 打开并读取 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    json_data = json.load(file)

                    # 从 JSON 数据中提取字段
                    link = json_data.get('链接', None)
                    document_name = json_data.get('公文名称', None)
                    content = json_data.get('内容', None)
                    subject_classification = json_data.get('主题分类', None)
                    issuing_agency = json_data.get('发文机构', json_data.get('制发单位', None))

                    # 对部分字段进行条件判断处理
                    valid_date_pattern = r"(\d{4}-\d{2}-\d{2})( \d{2}:\d{2}:\d{2})?|(\d{4}年\d{2}月\d{2}日)"
                    implementation_date = json_data.get('实施日期', None) if json_data.get('实施日期') != '----' else None
                    if implementation_date and implementation_date != '----':
                        implementation_date = re.match(valid_date_pattern, implementation_date).group(1)
                    drafting_date = json_data.get('成文日期', None) if json_data.get('成文日期') != '----' else None
                    if drafting_date and drafting_date != '----':
                        drafting_date = re.match(valid_date_pattern, drafting_date).group(1)
                    # 获取废止日期，优先获取“废止日期”，如果没有则尝试获取“失效日期”
                    repeal_date = json_data.get('废止日期', None)
                    if repeal_date == '----':  # 如果废止日期是'----'，则设置为None
                        repeal_date = None
                    if repeal_date is None:  # 如果废止日期为空，尝试获取失效日期
                        repeal_date = json_data.get('失效日期', None)
                        if repeal_date == '----':  # 如果失效日期是'----'，则设置为None
                            repeal_date = None
                    if repeal_date and repeal_date != '----':
                        repeal_date = re.match(valid_date_pattern, repeal_date).group(1)
                    release_date = json_data.get('发布日期', None)
                    if release_date and release_date != '----':
                        release_date = re.match(valid_date_pattern, release_date).group(1)
                    document_number = json_data.get('文号', json_data.get('发文字号', None))
                    validity = json_data.get('有效性', None)
                    source = json_data.get('文件来源', json_data.get('信息来源', None))
                    index_number = json_data.get('索引号', None)
                    subject_terms = json_data.get('主题词', None)

                    # 执行插入操作
                    cursor.execute(insert_query, (link, document_name, content, subject_classification, issuing_agency, implementation_date, drafting_date, repeal_date, release_date, document_number, validity, source, index_number, subject_terms))
                    # 提交事务
                    conn.commit()

                    print(f"数据成功插入: {filename}")

                except json.JSONDecodeError as e:
                    print(f"错误: 无法解析文件 {filename}. 错误信息: {e}")
                    continue

    print("所有数据插入完成！")

except pymysql.MySQLError as err:
    print(f"数据库错误: {err}")

finally:
    if conn.open:
        cursor.close()
        conn.close()
