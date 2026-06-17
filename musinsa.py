import requests
from bs4 import BeautifulSoup

# 웹브라우저 통신
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 시간, 판다스
import time
import pandas as pd
from tqdm import tqdm

# 브라우저의 옵션(크롬 브라우저 옵션)
# 동적으로 selenium을 기반으로 작업할 때 아래와 같은 규칙 적용 ~
option = Options()
option.add_argument('--no-sandbox')                 #샌드박스 비활성화(보안 꺼)
option.add_argument('--disable-dev-shm-usage')      #공유메모리 꺼
option.add_argument('--disable-gpu')                #gpu 사용하지마
option.add_argument('--enable-unsage-swiftshader')  #gpu 사용하지 않으므로 대용

driver = webdriver.Chrome(options=option)
base_url = 'https://www.musinsa.com/categories/item/001'

driver.get(base_url)
time.sleep(2)

# 윈도우 스크롤 내리는 스크립트 추가
# window.scrollTo(시작점, 끝점)
driver.execute_script('window.scrollTo(0,2000)')
time.sleep(2)

# 창에 보이는 아이템 가져오기
# 정적인 홈페이지 : beautifulsoup, 동적인 홈페이지 : selenium .find('구분자')
# html => 웹페이지 '내용' 담당, css => 웹페이지 '디자인' 담당
items = driver.find_elements(By.CSS_SELECTOR, ".sc-bSFBcf.iEkOIH")
item_list = []

for item in items:
    # try : 아래의 코드를 실행해라
    try :
        # 개별 상품에 대한 정보를 get
        # find_element(CSS를 기준으로 찾아줘, a['이름']) : '이름'을 가지고 있는 블럭
        # find_element <- 작은 범위에서 데이터를 찾아오겠다!

        # 예외처리
        # str()
        # replace
        # strip
        
        # a태그가 붙은['이름']을 가진것
        a_tag = item.find_element(By.CSS_SELECTOR, "a[data-original-price]")

        # 상품 이름
        name = a_tag.get_attribute("aria-label")        
        name = ( str(name).replace("상품상세로 이동", "").strip() if name else "이름 없음")

        # 브랜드 이름
        brand = a_tag.get_attribute("data-brand-id")
        brand = str(brand).strip() if brand else "브랜드 없음"

        # 가격
        price = a_tag.get_attribute("data-price")
        price = str(price).strip() if price else "가격 없음"

        # 상세페이지
        # href(html에서 '하이퍼링크'를 의미, 이미지/미디어로 연결되는 태그 href)
        link = a_tag.get_attribute("href")
        link = str(link).strip() if link else "링크 없음"

        item_list.append({'상품명' : name,
                          '브랜드' : brand,
                          '가격' : price,
                          '상품링크' : link
                          })

        # print(f'''
        #       name : {name},
        #       brand : {brand},
        #       price : {price},
        #       link : {link}
        #       ''')
    # 예외처리 : 실행하다가 '에러'가 발생하면 이렇게 해
    except Exception as e:
        print(f'에러가 발생했습니다. :{e}')

# 웹페이지 종료
driver.quit()

df = pd.DataFrame(item_list)

df.to_csv('./musinsa.csv',index=False, encoding='utf-8-sig')
