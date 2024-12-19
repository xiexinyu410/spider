from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
from selenium.webdriver.support.ui import Select
import os
import json
# 设置Chrome驱动路径
path = './chromedriver.exe'
browser = webdriver.Chrome(path)
time.sleep(2)

# 设置目标URL
#url = 'https://mzj.beijing.gov.cn/col/col10696/index.html###'
url = 'https://mzj.beijing.gov.cn/col/col10694/index.html'
#url = 'https://mzj.beijing.gov.cn/col/col10692/index.html'
# 打开目标网页
browser.get(url)
time.sleep(2)

#清理文件名中的非法字符
def clean_filename(filename):
    # 定义非法字符
    invalid_chars = r'[\\/:*?"<>|]'
    # 替换非法字符为下划线
    return re.sub(invalid_chars, '_', filename)

# 获取当前页面的文件链接
def get_page_link():
    # 获取网页源码
    content = browser.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # 提取所有的<a>标签中的href链接
    links = soup.find('div', class_="bjmz_tylist").find("tr").find_all('a', href=True)

    # 返回文件链接
    return links

# 模拟点击转换页面
def click_page(page):
    # 找到选择框并点击所需页数
    browser.get(url)
    select_element = browser.find_element_by_xpath("//select[@class='pager']")
    # 创建 Select 对象并选择页数
    select = Select(select_element)
    select.select_by_visible_text(str(page))

# 获取当前页面总页数
def get_total_pages():
    # 获取网页源码
    content = browser.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # 提取总页数信息
    pagination = soup.find('div', class_="bjmz_tylist").find("table").find_all('tr')[-1].find('td', class_='rowspace')
    pagination_text = pagination.text.strip()
    match = re.search(r'共 (\d+) 页', pagination_text)
    if match:
        total_pages = int(match.group(1))
        print(total_pages)
    return total_pages

#获取当前页面文件信息并保存
def get_page_data(link):
    # 处理相对路径URL：若是相对路径，拼接成完整URL
    href = link['href']
    print(href)
    name = link.get_text()
    name = clean_filename(name)
    # 定义文件夹路径
    folder_path = './content'
    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if not href.startswith('http'):
        href = 'https://mzj.beijing.gov.cn' + href

    # 打开新链接
    browser.get(href)
    time.sleep(2)
    html_content = browser.page_source
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {}
    data["链接"] = href
    data["公文名称"] = name
    # 提取文本内容
    if soup.find("div", {"id":"htmlContent"}):
        text = soup.find("div", {"id":"htmlContent"}).get_text(separator='\n', strip=True)
        data["内容"] = text
    elif soup.find("div", {"id":"mainText"}):
        text = soup.find("div", {"id":"mainText"}).get_text(separator='\n', strip=True)
        data["内容"] = text
    elif soup.find("div", class_="pages_content"):
        text = soup.find("div", class_="pages_content").get_text(separator='\n', strip=True)
        data["内容"] = text
    elif soup.find("div", {"id":"UCAP-CONTENT"}):
        text = soup.find("div", {"id": "UCAP-CONTENT"}).get_text(separator='\n', strip=True)
        data["内容"] = text
    elif soup.find("div", {"id":"zoom"}):
        text = soup.find("div", {"id":"zoom"}).get_text(separator='\n', strip=True)
        data["内容"] = text

    #提取其他信息项
    if soup.find("div", class_="txtbox"):
        rows = soup.find("div", class_="txtbox").find().find_all('tr')
        # 遍历每一行并提取表格数据
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:  # 一般有两列数据
                key = cols[0].get_text(strip=True).replace("：", "").replace("\u00a0", "").replace(" ", "")  # 移除不需要的空白字符
                value = cols[1].get_text(strip=True)
                data[key] = value
                # 如果当前行有4列（其他行的情况）
            elif len(cols) == 4:
                key1 = cols[0].get_text(strip=True).replace("：", "").replace("\u00a0", "").replace(" ", "")  # 获取第1列
                value1 = cols[1].get_text(strip=True)  # 获取第2列
                key2 = cols[2].get_text(strip=True).replace("：", "").replace("\u00a0", "").replace(" ", "")  # 获取第3列
                value2 = cols[3].get_text(strip=True)  # 获取第4列
                data[key1] = value1
                data[key2] = value2
    elif soup.find("ol", class_="doc-info clearfix"):
        list_items = soup.find("ol", class_="doc-info clearfix").find_all('li')
        # 遍历每个<li>元素
        for item in list_items:
            # 获取每个<li>中的标题和对应的值
            label = item.get_text(strip=True).split(']')[0].strip('[')  # 提取标签部分
            if item.find('span'):
                value = item.find('span').get_text(strip=True)  # 提取span中的内容
            elif item.find('a'):
                value = item.find('a').get_text(strip=True)  # 如果是链接，提取a标签中的文本
            # 存储到字典中
            data[label] = value
    elif soup.find("table", class_="border-table"):
        # 获取所有的<tr>元素
        rows = soup.find("table", class_="border-table").find_all('tr')
        # 遍历每一行并提取数据
        for row in rows:
            # 获取所有的<td>元素
            cols = row.find_all('td')
            # 如果该行有数据列
            if len(cols) == 2:
                # 提取左侧标签和右侧值
                key = cols[0].get_text(strip=True).replace("：", "")  # 获取标签并去掉冒号
                value = cols[1].get_text(strip=True)  # 获取值
                data[key] = value
            elif len(cols) == 4:
                # 处理包含四列数据的情况
                key1 = cols[0].get_text(strip=True).replace("：", "")  # 第一列标签
                value1 = cols[1].get_text(strip=True)  # 第一列值
                key2 = cols[2].get_text(strip=True).replace("：", "")  # 第二列标签
                value2 = cols[3].get_text(strip=True)  # 第二列值
                data[key1] = value1
                data[key2] = value2
    elif soup.find("ol", class_="doc-info clearfix"):
        # 获取所有的<li>元素
        list_items = soup.find("ol", class_="doc-info clearfix").find_all('li')
        # 遍历每一个<li>标签，提取信息
        for item in list_items:
            # 提取文本内容并去除空格
            label = item.get_text(strip=True)
            # 去除不需要的样式标签
            label = label.replace("：", "").replace("\u00a0", "").replace(" ", "")  # 去除多余空格
            # 提取<span>标签中的内容
            span = item.find('span')
            if span:
                value = span.get_text(strip=True).replace("\u00a0", "").replace(" ", "")
            else:
                value = ''
            # 将标签和对应的值保存到字典中
            if label and value:
                data[label] = value
    # 将文本保存到文件中
    # 构造文件路径
    file_path = os.path.join(folder_path, f"{name}.json")
    # 将数据保存为JSON文件
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


total_pages = get_total_pages()
# 逐页抓取数据
for page_num in range(1, total_pages + 1):
    print(f"抓取第 {page_num} 页数据")
    # 抓取当前页面的数据
    links = get_page_link()
    for link in links:
        get_page_data(link)
    if page_num < total_pages:
        # 模拟下拉选择框，选择下一页
        click_page(page_num+1)
        # 等待页面加载完成
        time.sleep(2)  # 等待2秒，避免页面加载不完全

# 关闭浏览器
browser.quit()
