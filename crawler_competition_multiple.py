# 인터넷 요청 -> requests
import requests
# 정적 웹페이지 크롤링 -> bs
from bs4 import BeautifulSoup
# 동적 웹페이지 크롤링 -> 들어온 사람에 따라 내용이 바뀌는 웹페이지
from selenium import webdriver

# 시간 라이브러리
import time
# 진행률을 표시하는 라이브러리 + for문
from tqdm import tqdm

# 크롤링한 내용을 엑셀 파일로 저장
# xlsx -> openpyxl(파이썬으로 엑셀 컨트롤)
# csv -> pandas를 사용
import pandas as pd

# requests 라이브러리를 사용해서 웹페이지를 읽어와라(get)

max_page = int(input('몇 페이지까지 크롤링할까요?\n'))
all_corpus = [] #1,2,3, ... max_pages까지의 크롤링 내역을 한꺼번에 저장 list

# tqdm이 for문 뒤로 오면 전체 실행시간 대비, 현재 진행 상황을 알려줌
for page in tqdm(range(1, max_page+1), desc='크롤링 진행중...') :
    url = f'https://www.cheongwon.go.kr/portal/petition/open/view?PageIndex={page}'
    response = requests.get(url)
    # print(response)

    # 웹페이지를 분해할 bs4 객체 생성
    # 파싱 = 어떤 정보 덩어리에서 원하는 정보를 추출하는 것
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(response.text)

    # soup라는 파싱 객체가 'span'이라는 양식의 class를 찾아서
    # class = 'category'라고 적힌 내용을 category라는 변수 이름에 저장
    category = soup.find_all('span', class_ = 'category')
    subject = soup.find_all('span', class_ = 'subject')
    petition = soup.find_all('span', class_ = 'text')
    date = soup.find_all('span', class_ = 'date')
    # print(category, subject, petition)

    # 크롤링한 결과물을 보기 쉬운 형태로 변환
    corpus = []
    for c, s, d, t in zip(category, subject, date, petition) :
        corpus.append([c.text, s.text, d.text, t.text])

    # corpus가 리스트 형태기 때문에 append가 아닌 extend를 사용해서 all_corpus에 추가
    all_corpus.extend(corpus)
    time.sleep(2) #2초 정도 정지

    #corpus : 말뭉치(딥러닝에서 자연어 데이터의 뭉치)
    df = pd.DataFrame(all_corpus, columns=['카테고리', '제목', '의견수렴기간', '청원내용'])

# print(df.head())
# 엑셀파일로 내보내기, 한글 안나오는 것 : 인코딩 이슈
df.to_csv('./crawling_sample.csv',index=False, encoding='utf-8-sig')
