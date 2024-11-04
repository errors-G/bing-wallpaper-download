import requests
import re
from bs4 import BeautifulSoup
import random
import os
from concurrent.futures import ThreadPoolExecutor

User_Agent = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',   
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'
]

def get_random_user_agent():
    """
    随机返回一个User-Agent字典
    
    该函数从一个预定义的User-Agent列表中随机选择一个User-Agent字符串，
    并将其作为字典返回。字典的键为'User-Agent'，值为随机选中的User-Agent字符串。
    
    Returns:
        dict: 包含随机User-Agent的字典
    """
    return {'User-Agent': User_Agent[random.randrange(0, len(User_Agent))]}

def fetch_url(session, url):
    """
    使用给定的session对象请求指定的URL，并返回响应对象。

    参数:
    - session: requests.Session实例，用于发起请求。
    - url: 字符串，指定要请求的URL。

    返回:
    - response: 如果请求成功，返回响应对象。
    - None: 如果请求失败，打印错误信息并返回None。
    """
    try:
        # 发起GET请求，并使用随机的User-Agent头信息
        response = session.get(url, headers=get_random_user_agent())
        # 检查响应状态码，如果状态码表示请求失败，则抛出异常
        response.raise_for_status()
        # 返回响应对象
        return response
    except requests.RequestException as e:
        # 捕获请求异常，打印错误信息，并返回None
        print(f"请求 {url} 失败: {e}")
        return None

def download_image(session, img_url, img_path):
    """
    使用给定的session从img_url下载图片，并保存到img_path。

    参数:
    - session: requests.Session实例，用于发起HTTP请求。
    - img_url: 字符串，指定图片的URL。
    - img_path: 字符串，保存图片的文件路径。

    此函数不会返回任何值，但如果下载过程中发生请求异常，会打印错误信息。
    """
    try:
        # 发起GET请求，获取图片资源
        response = session.get(img_url, headers=get_random_user_agent(), stream=True)
        response.raise_for_status()  # 检查响应状态，确保请求成功
        with open(img_path, 'wb') as f:
            # 分块读取响应内容，写入文件
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
    except requests.RequestException as e:
        # 处理请求异常，打印错误信息
        print(f"下载图片 {img_url} 失败: {e}")

def bing_img_download():
    """
    下载必应壁纸图片。
    
    该函数通过请求必应壁纸网站，获取并下载网站上的壁纸图片。
    它首先获取页面上的所有日期链接，然后对每个日期页面进行请求以获取图片URL，
    并使用多线程下载所有图片。
    """
    bing_url = 'https://bing.wdbyte.com/zh-cn/'
    next_urls = []
    
    # 使用Session管理请求，以保持会话状态。
    with requests.Session() as session:
        # 更新Session的User-Agent头部，模拟随机浏览器。
        session.headers.update(get_random_user_agent())
        
        # 请求必应壁纸首页。
        response = fetch_url(session, bing_url)
        if not response:
            return
        
        # 使用BeautifulSoup解析响应内容，获取所有日期链接。
        soup = BeautifulSoup(response.text, 'lxml')
        lines = soup.find_all('a')
        for line in lines:
            href = line.get('href')
            # 检查链接是否符合日期格式，并添加到待访问链接列表。
            if re.match(r'\d{4}-\d{2}', href):
                next_urls.append(bing_url + href)
        
        # 去除重复的链接并按降序排列。
        next_urls = list(set(next_urls))
        next_urls.sort(reverse=True)
        
        # 遍历每个日期链接，下载该日期的图片。
        for next_url in next_urls:
            img_name = next_url.replace(bing_url, '').replace('.html', '')
            print(f'正在下载 {img_name} 的图片')
            
            # 请求日期页面。
            response = fetch_url(session, next_url)
            if not response:
                continue
            
            # 解析日期页面内容，获取图片URL。
            soup = BeautifulSoup(response.text, 'lxml')
            current_lines = soup.find_all('a')
            i = 1
            # 使用多线程下载图片。
            with ThreadPoolExecutor(max_workers = 5) as executor:
                for line in current_lines:
                    href = line.get('href')
                    # 检查链接是否为图片URL，并提交下载任务。
                    if 'https://cn.bing.com/th' in href:
                        img_path = os.path.join('D:/images/必应壁纸', f'{img_name}-{i}.jpg')
                        executor.submit(download_image, session, href, img_path)
                        i += 1
            print(f'{img_name} 的图片下载完成')
    print('所有图片下载完成')
    
if __name__ == '__main__':
    bing_img_download()