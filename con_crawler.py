# 디시/아카콘 크롤러

import requests
from bs4 import BeautifulSoup
import re
import asyncio, aiohttp
import os

DC_CON_URL = 'https://dccon.dcinside.com/#'
AKA_CON_URL = 'https://arca.live/e/'

def crawl_con(site_name, con_number):
    if site_name == 'dc' or site_name == '디시':
        dccon_crawler(con_number)
    elif site_name == 'arca' or site_name == '아카':
        arcacon_crawler(con_number)
    else:
        return '잘못된 사이트 이름입니다.'
    
    return '콘 다운로드가 완료되었습니다.'
    pass

def dccon_crawler(con_number):
    pass





# 파일 이름을 추출 함수
def get_file_name_arca(url):
    # //ac-p2.namu.la/20231129sac/d75a68067307970c3cf7836a0c28a62c534b2d7d992abc5632520bb864a465e7.mp4?expires=1701392400&key=IAPmUUIj83AHvk6ZsnYS1A
    # 위와 같은 url에서 파일 이름을 추출한다.
    # b029e78d50f68bd997dc430fcba4cde21e522092059ac28b453d6d2e010dc50c.png
    # 위와 같은 파일 이름을 추출한다.
    file_name = re.findall(r'[^/]*$', url)[0]
    file_name = file_name.split("?")[0]
    return file_name

def get_urls_arca(con_number):
    con_url = AKA_CON_URL + str(con_number)

    res = requests.get(con_url)
    soup = BeautifulSoup(res.content, 'lxml')

    img_selector = "img.emoticon"
    video_selector = "video.emoticon"

    img_urls = soup.select(img_selector)
    video_urls = soup.select(video_selector)

    img_urls = [img_url['src'] for img_url in img_urls]
    video_urls = [video_url['data-src'] for video_url in video_urls]

    urls = img_urls + video_urls
    # https: 를 붙여준다.
    urls = ['https:' + url for url in urls]
    return urls

def con_download(urls):
    # 파일을 저장할 폴더를 생성한다.
    if not os.path.exists('./img'):
        os.makedirs('./img')

    # urls를 이용해 파일을 다운로드한다.
    for url in urls:
        res = requests.get(url)
        file_name = get_file_name_arca(url)
        with open('./img/' + file_name, 'wb') as f:
            f.write(res.content)
    
def arcacon_crawler(con_number):
    urls = get_urls_arca(con_number)
    con_download(urls)
    pass

# 완료된 콘 파일 삭제
def del_con():
    # ./img 폴더에 있는 모든 파일을 삭제한다.
    file_list = os.listdir('./img')
    for file in file_list:
        os.remove('./img/' + file)
    