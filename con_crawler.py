# 디시/아카콘 크롤러

import requests
from bs4 import BeautifulSoup
import re
import asyncio, aiohttp
import os

DC_CON_URL = 'https://dccon.dcinside.com/#'
AKA_CON_URL = 'https://arca.live/e/'

def get_con_name_dc(con_number):
    pass

def dccon_crawler(con_number):
    pass

def get_file_name_dc(url):
    pass

def get_urls_dc(con_number):
    pass


# 콘 이름 추출 함수
def get_con_name_arca(con_number):
    con_url = AKA_CON_URL + str(con_number)

    res = requests.get(con_url)
    soup = BeautifulSoup(res.content, 'lxml')

    con_name_selector = "div.title-row > div.title"
    con_name = soup.select(con_name_selector)[0].text

    # 앞뒤 /n 제거
    con_name = con_name.strip()
    return con_name

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

def arcacon_crawler(con_number):
    urls = get_urls_arca(con_number)
    con_download(urls, 'arca', con_number)
    pass

# 완료된 콘 파일 삭제
def del_con(con_number):
    # ./img 폴더에 있는 모든 파일을 삭제한다.
    file_list = os.listdir('./img')
    for file in file_list:
        os.remove('./img/' + file)
        
        
def get_con_info(txt):
    try:
        site_name, con_number = txt.split(' ')
    except:
        return False, None, None, None, '사이트 이름과 콘 번호를 입력해주세요.'
    
    if site_name == 'dc' or site_name == '디시':
        con_title = get_con_name_dc(con_number)
        site_name = 'dc'
    elif site_name == 'arca' or site_name == '아카':
        con_title = get_con_name_arca(con_number)
        site_name = 'arca'
    else:
        return False, None, None, None, '사이트 이름을 잘못 입력하셨습니다.'
    
    return True, site_name, con_number, con_title, '성공적으로 콘 이름을 추출하였습니다.'
        
crawler_func = {
    'dc': dccon_crawler,
    'arca': arcacon_crawler
}

def crawl_con(site_name, con_number):
    if crawler_func[site_name](con_number):
        return False, '사이트 이름을 잘못 입력하셨습니다.'
    return True, '성공적으로 다운로드하였습니다.'

def con_download(urls, site_name, con_number):
    CON_PATH = f'./temp/{site_name}_{con_number}'
    # 파일을 저장할 폴더를 생성한다.
    if not os.path.exists(f'{CON_PATH}/img'):
        os.makedirs(f'{CON_PATH}/img')
    
    # urls를 이용해 파일을 다운로드한다.
    # for url in urls:
    for i, url in enumerate(urls):
        res = requests.get(url)
        file_ext = re.findall(r'[^.]*$', get_file_name_arca(url))[0]
        file_name = f'{i:03d}.' + file_ext
        # 이미 파일이 존재하면 넘어간다.
        if os.path.exists(f'{CON_PATH}/img/' + file_name):
            continue
        with open(f'{CON_PATH}/img/' + file_name, 'wb') as f:
            f.write(res.content)