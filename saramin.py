import requests
from bs4 import BeautifulSoup     #정적인 크롤링

# 웹브라우저 통신
from selenium import webdriver    #인터넷 내용 크롤링
import re                         #정규표현식

# 시간, 판다스
import time
import pandas as pd
from tqdm import tqdm

from html import unescape       #html형식의 깨진 글자를 복원

def clean_text(text):
    #text를 넣어서 clean_text를 실행했는데, text가 none이라면?
    if not text:
        return ""
     #text가 있다면(빈 값이 아니라면) 정제
    text = unescape(text.text)
    
    #re(정규표현식, regular expression) : 텍스트를 특정한 패턴으로 찾아서 변형
    #re.sub(패턴, 바꿀 문자, 문장) -> '문장'에서 '패턴'을 찾아서 '바꿀 문자'로 변형
    #a-zA-Z : 영문자 전체, ㄱ-ㅎ가-힣 : 한글전체
    #\s (공백) // \s+ : 한 칸 이상의 모든 공백
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def crawling_data(search_word):
    # 크롤링
    # 1. 크롤링할 '주소'를 정함 ( 가져올 정보가 있는 인터넷 주소)
    # 2. requests.get(주소) -> '주소'에 있는 html을 받아옴
    # **** html : 인터넷에서 정보를 표현하는 파일 형식
    # 3. bs4 -> 받아온 html을 '파싱(parsing)', 필요정보 추출
    # 4. bs4.select(구분자) <div></div>
    # 5. bs4.select_one(구분자)
    # 6. 얻어낸 정보 -> re(정규표현식)으로 '정제' or pandas로 정리 후 저장

    #'헤더' : 브라우저가 서버에 무언가 요청할때 '나 이런 브라우저예요' 라는 내용
    base_url = 'https://www.saramin.co.kr/zf_user/search'
    headers = {
                #요청하는 브라우저의 종류
                "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
                ),
                #요청하는 언어의 종류
                "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                }

    # 리퀘스트를 보냄
    # headers : 웹페이지에 정보를 요청하는 브라우저에 대한 내용
    # params : 웹페이지에 ~~한 정보를 요청합니다~ '검색어, 검색조건'
    # timeout : 웹페이지로부터 회신이 올 때까지 기다리는 시간 최대치
    response = requests.get(base_url, headers=headers,
                            params={'searchword':search_word},
                            timeout=10
                            )

    # 만약 response가 <200>이라면 -> 정상
    # 400에러 (서버 에러, 웹페이지) / 500에러(클라이언트 에러)
    # bs4에게 html을 파싱하도록 객체 생성 BeautifulSoup(html, 파서)
    soup = BeautifulSoup(response.text, 'html.parser')

    # print(response.text)

    # 검색 결과 선별
    rows = []

    # find : 전통적인 선택 방식
    # select : 현대적인 선택 방식
    # soup.select(구분자) : '구분자'가 들어가는 모든 내용을 select(선택)
    # soup.find_all('div', class_ = 'item_recruit')
    for item in soup.select('div.item_recruit'):

        # 1. 회사명
        # select_one(구분자) : 구분자 이름을 갖는 딱 하나만 가져와
        corp_name = item.select_one('div.area_corp')

        # 2. 채용 정보
        job_area = item.select_one('div.area_job')

        # 3. 공고 제목
        # <div>로 시작하지 않음 / div가 아니어도 괜찮다
        # job_tit을 찾아서 one 한개만 가져올 것
        job_title = job_area.select_one('.job_tit')

        # 4. 조건
        conditions = job_area.select_one('.job_condition')
        location = ''
        condition1 = ''

        if conditions :
            span = conditions.select('span')
            # 조건이 1개 이상 있다면
            if len(span) > 0:
                # 첫번째 조건은 무조건 위치이다
                location = span[0].get_text(strip=True)

            if len(span) > 1:
                # 두번째 조건은 신입/경력
                condition1 = span[1].get_text(strip=True)

        # 5. 직무분야
        job_sector = job_area.select_one('.job_sector')
        job_sector = (job_sector.get_text(strip=True) if job_sector else "")

        # 내가 모은 정보를 '정제'함
        job_title = clean_text(job_title)
        location = clean_text(location)
        job_sector = clean_text(job_sector)
        condition1 = clean_text(condition1)
        corp_name = clean_text(corp_name)

        rows.append({
                    '공고 이름' : job_title,
                    '회사 위치' : location,
                    '조건 1' : condition1,
                    '조건 2' : job_sector,
                    '회사 이름' : corp_name
                    })

    # 최종적으로 얻어진 rows를 pd.DataFrame으로 감싸서 df를 만들어줌
    df = pd.DataFrame(rows)
    print(df)

#진입점(이 파이썬 파일의 '실제 실행되는 부분')
if __name__ == '__main__':
    crawling_data('인공지능')