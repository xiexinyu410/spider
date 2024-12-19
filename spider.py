from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
from selenium.webdriver.support.ui import Select
import os
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
    content = browser.page_source
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    # 提取文本内容
    if soup.find("div", {"id":"htmlContent"}):
        data = soup.find("div", {"id":"htmlContent"})
        text = data.get_text(separator='\n', strip=True)
    elif soup.find("div", {"id":"mainText"}):
        data = soup.find("div", {"id":"mainText"})
        text = data.get_text(separator='\n', strip=True)
    elif soup.find("div", class_="pages_content"):
        data = soup.find("div", class_="pages_content")
        text = data.get_text(separator='\n', strip=True)
    elif soup.find("div", {"id":"UCAP-CONTENT"}):
        data = soup.find("div", {"id": "UCAP-CONTENT"})
        text = data.get_text(separator='\n', strip=True)
    elif soup.find("div", {"id":"zoom"}):
        data = soup.find("div", {"id":"zoom"})
        text = data.get_text(separator='\n', strip=True)
    #提取信息项内容

    # 将文本保存到文件中
    # 构造文件路径
    file_path = os.path.join(folder_path, f"{name}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
       f.write(text)



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
