from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

# 设置Chrome驱动路径
path = './chromedriver.exe'
browser = webdriver.Chrome(path)
time.sleep(2)

# 设置目标URL
url = 'https://mzj.beijing.gov.cn/col/col10696/index.html###'

# 打开目标网页
browser.get(url)
time.sleep(2)

# 获取当前页面的文件链接
def get_page_link():
    # 获取网页源码
    content = browser.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # 提取所有的<a>标签中的href链接
    links = soup.find('div', class_="bjmz_tylist").find("tr").find_all('a', href=True)

    # 返回文件链接
    return links

#获取当前页面文件信息并保存
def get_page_data(link):
    # 处理相对路径URL：若是相对路径，拼接成完整URL
    href = link['href']
    print(href)
    name = link.get_text()
    if not href.startswith('http'):
        href = 'https://mzj.beijing.gov.cn' + href

    # 打开新链接
    browser.get(href)
    time.sleep(2)
    content = browser.page_source
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(content, 'html.parser')
    # 提取所有文本内容
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
    # 将文本保存到文件中
    with open(name + ".txt", 'w', encoding='utf-8') as f:
       f.write(text)
# 获取第一页数据
links = get_page_link()
for link in links:
    get_page_data(link)

# 尝试翻页，直到没有“下一页”按钮
while True:
    try:
        # 查找“下一页”按钮（需要根据实际的页面结构调整）
        next_button = browser.find_element(By.XPATH, '//*[contains(text(),"下页")]')

        # 点击“下一页”按钮
        next_button.click()
        time.sleep(2)  # 等待页面加载

        # 获取并处理新页面的数据
        links = get_page_link()
        for link in links:
            get_page_data(link)
    except Exception as e:
        print("没有找到翻页按钮或已到最后一页，停止翻页。")
        break

# 关闭浏览器
browser.quit()
