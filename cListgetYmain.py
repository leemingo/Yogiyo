# 'python -m pip install --upgrade pip'
# -*- coding: utf-8 -*-
import argparse
import os
import time
import dbconfig
# import pymysql
import requests
import json
import sys

from tqdm import tqdm

from collections import OrderedDict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

CHROME_DIR_PATH = './../chromedriver'
YOUR_DIRECTORY_NAME = './'
DelayTime1 = 1
DelayTime2 = 2
DelayTime3 = 3
DelayTime5 = 5

menuupdate = 0

# 확인 하기 위한 변수
CallUrlPath = ''
OpenPageCheckNumber = ''
OpenPageCheckErrorCode = 0

member_Num = ''
member_Site = ''
member_ID = ''

MainURL = 'https://www.yogiyo.co.kr/mobile/#/'
SqlRowData = ''
StartStoreNumber_S = 0
StartStoreNumber_E = 0
reviewcntdown1 = 0
reviewcntdown2 = 4000

store_Name = ''
store_subName = ''
store_number = ''

# Chrome driver option
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument('headless')
options.add_argument('disable-gpu')
options.add_argument('lang=euc-KR')

# chrome_path에 chromedriver의 경로를 넣어주시면 됩니다.
# driver = webdriver.Chrome("/home/jin/Documents/PY/chromedriver/chromedriver", options=options)
# driver = webdriver.Chrome(CHROME_DIR_PATH)
path = "./../chromedriver"
driver = ''

# mysql_controller = dbconfig.MysqlController('49.50.165.72', 3306, 'kswer', 'happy@1207', 'crawl')
#mysql_controller = dbconfig.MysqlController('192.168.0.30', 3306, 'jin', 'jj8995', 'crawl')
mysql_controller = dbconfig.MysqlController('192.168.0.13', 3306, 'ucrawl', 'happy@1207', 'crawl')


# json 데이터 만들기 위한 변수.
json_data_storeinfo = OrderedDict()  # 기본 상점 정보
json_data_menuinfolist = []
json_data_reviewinfolist = []  # 리뷰 ( 데이터가 많음. )
# json_data_menuinfo = OrderedDict() # 메뉴 정보
# json_data_reviewinfo = OrderedDict() # 리뷰 ( 데이터가 많음. )
StartAddr_A = ''
StartAddr_B = ''

stoday = '%04d-%02d-%02d' % (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)


# 00. 페이지 하단으로 이동
def page_scroll_bottom():
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")


# 이미지저장할 폴더 생성
def create_dir(lasedir):
    try:
        if not (os.path.isdir(lasedir)):  # 폴더가 있는지 확인
            os.makedirs(os.path.join(lasedir))  # 폴더가 없으면 폴더 만들기.
        return True
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise
        return False


# 초기화 하기
def clear_data():
    global CallUrlPath
    global OpenPageCheckNumber
    global OpenPageCheckErrorCode
    global member_Num
    global member_Site
    global member_ID
    global SqlRowData

    global store_Name
    global store_subName
    global json_data_menuinfolist

    json_data_menuinfolist.clear()

    CallUrlPath = ''
    OpenPageCheckNumber = ''
    OpenPageCheckErrorCode = 0

    member_Num = ''
    member_Site = ''
    member_ID = ''
    SqlRowData = ''

    store_Name = ''
    store_subName = ''


# 함수 만들기

def LogPrint(strtmp):
    sTime = '%02d:%02d:%02d' % (time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
    print(stoday, sTime, strtmp)


def ErrorDataFileSave(strtmp):
    stoday = '%04d-%02d-%02d' % (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)
    sTime = '%02d:%02d:%02d' % (time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
    fTmp = stoday + ' ' + sTime + ' ' + strtmp

    fs = open('./../yogiyoDetailError.txt', 'a+t')  # 파일 쓰기
    fs.write(fTmp)
    fs.write('\n')  # 라인 개행.
    fs.close()

    LogPrint(fTmp)


def SuccOpenListFileSave(strtmp):
    stoday = '%04d-%02d-%02d' % (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)
    sTime = '%02d:%02d:%02d' % (time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
    fTmp = stoday + ' ' + sTime + ' ' + strtmp

    fs = open('./../yogiyoDetailSucc.txt', 'a+t')  # 파일 쓰기
    fs.write(fTmp)
    fs.write('\n')  # 라인 개행.
    fs.close()


def getsqldata(sAddr):
    global SqlRowData


#    SqlRowData = mysql_controller.selectisaddr2(sAddr)
# selectisaddr_se
#    LogPrintprint('SqlRowData : ' + str(SqlRowData[0]) + ' | ' + sAddr)
#    for row in SqlRowData:
#        LogPrint(str(row[0]), str(row[1]), str(row[3]))

# 00. 메인페이지
def yMainPageOpen(spagenum):
    try:
        driver.get(MainURL + spagenum)
        #    LogPrint(driver.current_url)
        #        time.sleep(DelayTime3)

        element = WebDriverWait(driver, 10).until(
            # By.ID - 태그에 있는 ID 로 검색 #By.CSS_SELECTOR - CSS Selector 로 검색#By.NAME - 태그에 있는 name 으로 검색
            # By.TAG_NAME - 태그 이름으로 검색
            EC.presence_of_element_located((By.CSS_SELECTOR, "#menu > div > div:nth-child(2)"))
        )
        return True
    except TimeoutException:
        ErrorDataFileSave(spagenum + " | 해당 페이지 열 수 없습니다.")
        return False


# 02. 상점명
def get_store_name():
    global OpenPageCheckErrorCode
    global store_Name
    global store_subName
    global json_data_storeinfo

    try:
        tmpstr = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/div[1]/div[1]/span')  # 상점명-위치
        tmptext = str(tmpstr.text)
        TmpStore_Name = tmptext.split('-')

        store_Name = TmpStore_Name[0]
        store_subName = ''
        if len(TmpStore_Name) != 1:
            store_subName = TmpStore_Name[1]

        json_data_storeinfo["storename"] = store_Name
        json_data_storeinfo["storesubname"] = store_subName
        return True
    except:
        LogPrint('store_name [!!!  없음 !!!]')
        OpenPageCheckErrorCode = 2
        return False


# 02. 상점명
def get_store_Menu():
    global json_data_menuinfolist
    global driver

    LogPrint('메뉴 가져오기 시작')
    try:
        # 메뉴 바 클릭 ( 펼쳐 줘야 메뉴명, 가격 등을 전부 가져 올수 있다. )

        try:
            img = driver.find_element_by_tag_name('div.logo')  # 이미지
            try:
                imgpath = './../images/yogiyo/' + store_number + '/' + store_Name + '.png'
                img.screenshot(imgpath)
            except:
                ErrorDataFileSave('대표이미지 저장 오류')
        except:
            ErrorDataFileSave('대표이미지 없음')

        try:
            menubar = driver.find_elements_by_tag_name('h4.panel-title')
        except:
            LogPrint('bar not found')

        for icnt, item in enumerate(menubar):
            try:  # 메뉴바 클릭하기
                UpDn_Check = 1  # 펼처져 있는 것은 펼치지 않는다.
                try:
                    item_check_UPDN = item.find_element_by_class_name('pull-right.icon-arr-down')
                    UpDn_Check = 1
                except:
                    UpDn_Check = 0

                if UpDn_Check == 1:
                    item.click()
            except:
                LogPrint('메뉴바 클릭 오류')
                continue

        #        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        #        driver.execute_script("window.scrollTo(0,document.body.scrollTop);")

        menugroup_arr = driver.find_elements_by_tag_name('div.panel.panel-default.ng-scope')  # 메뉴 그룹
        #        print(str(len(menugroup_arr)))
        #        for mgitem in tqdm(enumerate(menugroup_arr)):
        for inum, mgitem in tqdm(enumerate(menugroup_arr)):
            try:
                menugroptag = mgitem.find_element_by_tag_name('span.menu-name.pull-left.ng-binding.pop-menu')
                menugroupname = menugroptag.text
            #                print('그룹명0:' + menugroupname)
            except:
                try:
                    #                print(mgitem.page_source)
                    #                menugropclass = mgitem.find_element_by_class_name('menu-name.pull-left.ng-binding')
                    menugroptag = mgitem.find_element_by_tag_name('span.menu-name.pull-left.ng-binding')
                    menugroupname = menugroptag.text
                #                    print('그룹명1:'+ menugroupname)
                except:
                    print('class 로 찾기 실패 1 ')
                    continue

            #            print('Menu Group ' , menugroupname)
            #        review_arr = driver.find_elements_by_tag_name('li.ng-scope.photo-menu')
            review_arr = mgitem.find_elements_by_tag_name('li.ng-scope.photo-menu')
            #            review_arr = mgitem.find_elements_by_class_name('ng-scope.photo-menu')
            # 'panel panel-default ng-scope'

            #           LogPrint('메뉴 반복 시작 (' + str(len(review_arr)) + ')')

            #            for icnt, item in enumerate(review_arr):
            for icnt, mditem in enumerate(review_arr):
                #                print(str(icnt), menugroupname)

                try:  # 메뉴명 가져오기
                    menu_name = mditem.find_element_by_tag_name('div.menu-name.ng-binding')
                except:
                    LogPrint('메뉴명 가져오기 실패 1')
                    continue

                try:  # 가격 가져오기
                    TmpPriceA = mditem.find_element_by_tag_name('span.ng-binding')
                except:
                    LogPrint('가격 가져오기 실패 2')
                    continue

                try:  # 설명
                    tmpmenudesc = mditem.find_element_by_tag_name('div.menu-desc.ng-binding')
                    tmpstr3 = tmpmenudesc.text
                except:
                    LogPrint('가격 가져오기 실패 3')
                    tmpstr3 = ''

                tmpstr = menu_name.text
                tmpstr2 = TmpPriceA.text

                #                print('메뉴 ?:' + tmpstr + ':'+tmpstr2 )
                if tmpstr == '':
                    continue

                #                LogPrint('매뉴 | ' + str(icnt) + ' | ' + tmpstr + ' | ' + tmpstr2 + ' | ' + tmpstr3) # 차후 사용 하지 말것

                json_data_menuinfo = {}
                #      json_data_menuinfo["menucnt"] = str(icnt)
                json_data_menuinfo["menuname"] = tmpstr
                json_data_menuinfo["menuprice"] = tmpstr2
                json_data_menuinfo["menuexplanation"] = tmpstr3
                json_data_menuinfo["menuegroup"] = menugroupname

                #                LogPrint(json_data_menuinfo)
                json_data_menuinfolist.append(json_data_menuinfo)
                # tmpzz = json.dumps(json_data_menuinfolist)
                #       print(tmpzz)
                print('-----img ----')
                try:
                    imgpath = './../images/yogiyo/' + store_number + '/' + tmpstr + '.png'
                    try:  # 이미지가 있는 것만 하기 위함.
                        imgcheck = mditem.find_element_by_tag_name('td.photo-area')  # 이미지
                    except:
                        continue
                    try:
                        img = imgcheck.find_element_by_tag_name('div.photo')  # 이미지
                        print(img.get_attribute('style'))
                        print('AA->' + img.text)
                        sys.exit()
                    except:
                        print('EEE')

                        sys.exit()
                        continue

                #                    try:
                #                        img.screenshot(imgpath)  # 이미지 저장
                #                    except:
                #                        continue

                except:
                    continue

        return True
    except:
        LogPrint('메뉴 오류 ~~~~~~!!!!!')
        time.sleep(1)
        return False

    """
            메뉴[menuinfo]
            - 메뉴명[menuname]
            - 가격[menuprice]
            - 메뉴 설명(설명 없는 경우 있음 )[menuexplanation]
            - 이미지(이미지 전체없음, 상단이미지만 있음, 파일로 저장)
            - 메뉴 그룹 menuegroup
    """


# 04. 정보 클릭
def go_to_info():  # 정보 페이지 클릭

    try:
        driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[3]').click()
        time.sleep(1)
        return True
    except:
        return False

    """
    try:
        driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[3]').click()

        element = WebDriverWait(driver, 10).until(
            # By.ID - 태그에 있는 ID 로 검색 #By.CSS_SELECTOR - CSS Selector 로 검색#By.NAME - 태그에 있는 name 으로 검색
            # By.TAG_NAME - 태그 이름으로 검색
#            EC.presence_of_element_located((By.ID, "div#info.info-list"))
#            EC.presence_of_element_located((By.CSS_SELECTOR, "#info"))
            #EC.presence_of_element_located((By.ID, "div.info-item-title.info-icon1"))'#info > div:nth-child(2) > div
            EC.presence_of_element_located((By.CSS_SELECTOR, "#info > div:nth-child(2) > div"))
        )
        return True
    except TimeoutException:
        ErrorDataFileSave(store_number + " | 정보 페이지 | 열 수 없습니다.")
        return False
    """


# 정보 데이터 가져오기
def getinfo():
    global json_data_storeinfo

    try:
        # 영업시간
        str1 = driver.find_element_by_xpath('//*[@id="info"]/div[2]/p[1]/span')
        # 전화번호
        strTel = driver.find_element_by_xpath('//*[@id="info"]/div[2]/p[2]/span')
        # 주소
        str2 = driver.find_element_by_xpath('//*[@id="info"]/div[2]/p[3]/span')
        # 최소주문 금액
        str3 = driver.find_element_by_xpath('//*[@id="info"]/div[3]/p[1]/span')
        # 결제 수단.
        str4 = driver.find_element_by_xpath('//*[@id="info"]/div[3]/p[2]/span')
        # 상호
        str5 = driver.find_element_by_xpath('//*[@id="info"]/div[4]/p[1]/span')
        # 사업자번호
        str6 = driver.find_element_by_xpath('//*[@id="info"]/div[4]/p[2]/span')
        # 원산지
        str7 = driver.find_element_by_xpath('//*[@id="info"]/div[5]/pre')
        #        LogPrint('정보' + ' ' + str1.text + ' ' + str2.text + ' ' + str3.text + ' ' + str4.text)
        json_data_storeinfo["storetime"] = str1.text  # 영업시간
        json_data_storeinfo["storetel"] = strTel.text  # 전화번호
        json_data_storeinfo["storeaddr"] = str2.text  # 주소
        json_data_storeinfo["storeminprice"] = str3.text  # 최소주문금액
        json_data_storeinfo["storecard"] = str4.text  # 결제수단.
        json_data_storeinfo["storebizname"] = str5.text  # 상호명(사업자등록)
        json_data_storeinfo["storebiznum"] = str6.text  # 사업자등록번호
        json_data_storeinfo["storeorigin"] = str7.text  # 원산지

        try:
            # 부가정보 ( 정보 없을수 있음 : 예; 세스크멤버스 사업장)
            str8 = driver.find_element_by_xpath('//*[@id="info"]/div[2]/p[4]/span')
            json_data_storeinfo["storeaddition"] = str8.text  # 부가정보( 정보 없을수 있음 : 예; 세스크멤버스 사업장)
        except:
            #   LogPrint('기본정보 - 부가정보 없음')
            json_data_storeinfo["storeaddition"] = ' '  # 부가정보( 정보 없을수 있음 : 예; 세스크멤버스 사업장)

        # LogPrint(json_data_storeinfo)
        time.sleep(1)
        return True
    except:
        time.sleep(1)
        return False


# 0x. 클린리뷰 클릭
def go_to_review():  # 클린리뷰 페이지 클릭
    try:
        driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]').click()
        time.sleep(1)
        return True
    except:
        return False
    """
    try:
        driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]').click()

        element = WebDriverWait(driver, 10).until(
            # By.ID - 태그에 있는 ID 로 검색 #By.CSS_SELECTOR - CSS Selector 로 검색#By.NAME - 태그에 있는 name 으로 검색
            # By.TAG_NAME - 태그 이름으로 검색
#            EC.presence_of_element_located((By.ID, "ul#review.list-group.review-list"))
            EC.presence_of_element_located((By.CSS_SELECTOR, "#review"))
        )
        return True
    except TimeoutException:
        ErrorDataFileSave(store_number + " | 리뷰 페이지 | 열 수 없습니다.")
        return False
    """


# 07. 리뷰 더보기 클릭하기 (더보기 버튼 클래스명)
def click_more_review():
    global OpenPageCheckErrorCode

    try:
        #    driver.find_element_by_class_name('btn-more').click()
        #    driver.find_element_by_xpath('//*[@id="review"]/li[12]').click()
        LogPrint('리뷰 더보기 클릭---')
        #        reviewdatacheck = 0
        # page_scroll_bottom()  # 페이지 맨 마지막으로.

        reviewcnt_total = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span')

        pbar = tqdm()
        while True:
            try:
                checkbtn = driver.find_element_by_class_name('list-group-item.btn-more')  # 버튼이 있다.
                if checkbtn.text == '':  # 버튼명이 '더보기' 가 아니면 더 이상 없다.
                    print('더 보기 문자 못 찾음')
                    break

            except Exception as exceptcode:  # 리뷰 더이상 없음.
                LogPrint('리뷰클릭---E[' + exceptcode)
                #                page_scroll_bottom()  # 페이지 맨 마지막으로.
                #                time.sleep(DelayTime1)

                break
            #            '리뷰를 읽어오고 있습니다.'
            # '//*[@id="review"]/li[12]/a'
            try:
                time.sleep(0.2)
                driver.find_element_by_css_selector('#review > li.list-group-item.btn-more').click()  # 더보기 버튼
            #            page_scroll_bottom()  # 페이지 맨 마지막으로.
            #           tempelm = driver.find_element_by_xpath('//*[@id="review"]/li[12]/a').click()  # 더보기 버튼
            except:
                driver.find_element_by_css_selector('#review > li.list-group-item.btn-more').click()  # 더보기 버튼
                time.sleep(0.2)

            #           time.sleep(DelayTime1) # 이걸 써야 하는지는 모르겠다.
            #            page_scroll_bottom() # 페이지 맨 마지막으로.
            checkmessage = driver.find_element_by_xpath('//*[@id="spinner"]/span')  # '리뷰를 읽어오고 있습니다.
            while checkmessage.text != '':
                time.sleep(0.2)
                checkmessage = driver.find_element_by_xpath('//*[@id="spinner"]/span')  # '리뷰를 읽어오고 있습니다.

            pbar.update(1)
        #               LogPrint('리뷰클릭---X')

        pbar.close()
        return True
    except:
        #        LogPrint('리뷰클릭---EEEEEEEEEEE')
        pbar.close()
        OpenPageCheckErrorCode = 6
        return False


def getreview():
    global json_data_reviewinfolist
    #    global driver

    json_data_reviewinfolist.clear()

    try:
        LogPrint('review 시작')

        # 총점 star-point-wrap
        review_staritem = driver.find_element_by_class_name('restaurant-star-point')
        checkpoint = review_staritem.find_element_by_class_name('ng-binding')
        tot_Star_1 = checkpoint.text

        totalstartpoint = driver.find_element_by_class_name('star-point-list')
        total_ABC = totalstartpoint.find_elements_by_class_name('points.ng-binding')
        tmp = ''
        for tct in total_ABC:  # 총별
            tmp = tmp + '|' + tct.text

        tmp2 = tmp.split('|')
        tot_Star_2 = tmp2[1]
        tot_Star_3 = tmp2[2]
        tot_Star_4 = tmp2[3]

        #        print('** : ' + str(tot_Star_1) + ' / ' + str(tot_Star_2) + ' / ' + str(tot_Star_3) + ' / ' + str(tot_Star_4))
        #        LogPrint('리뷰시작--')

        reviewcountcheck = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span')
        review_arr = driver.find_elements_by_tag_name('li.list-group-item.star-point.ng-scope')
        LogPrint('리뷰 갯수 : [' + str(len(review_arr)) + ' / ' + reviewcountcheck.text + ' ]')

        if not (len(review_arr) >= (int(reviewcountcheck.text) - 10)):
            ErrorDataFileSave('!!! 리뷰 갯수 오류(현재/총) | ' + str(len(review_arr)) + ' / ' + reviewcountcheck.text + ' ]')
            return False

        # LogPrint(str(len(review_arr)) + '** : ' + str(tot_Star_1) + ' / ' + str(tot_Star_2) + ' / ' + str(tot_Star_3) + ' / ' + str(tot_Star_4))
        for icnt, item in tqdm(enumerate(review_arr)):
            # ID
            str_id = item.find_element_by_class_name('review-id.ng-binding')
            # 시간
            str_time = item.find_element_by_class_name('review-time.ng-binding')
            # 별점
            staritem = item.find_element_by_tag_name('div.star-point')
            starcount = staritem.find_elements_by_class_name('full.ng-scope')
            review_start1 = str(len(starcount))

            # 맛,양,배달
            reviewstartitem = staritem.find_element_by_class_name('category')
            tmpstar = reviewstartitem.find_elements_by_class_name('points.ng-binding')
            ztmp = ''
            for checktmpstar in tmpstar:
                ztmp = ztmp + '|' + checktmpstar.text

            zztmp = ztmp.split('|')
            review_start2 = zztmp[1]
            review_start3 = zztmp[2]
            review_start4 = zztmp[3]

            # 선택메뉴
            str_menu = item.find_element_by_tag_name('div.order-items.default.ng-binding')
            # 리뷰
            str_review = item.find_element_by_tag_name('p.ng-binding')

            json_data_reviewinfo = {}
            json_data_reviewinfo["totalpoint"] = str(tot_Star_1)  # 총점
            json_data_reviewinfo["totaltastepoint"] = str(tot_Star_2)  # 총 맛점
            json_data_reviewinfo["totalquantitypoint"] = str(tot_Star_3)  # 총 양점
            json_data_reviewinfo["totaldeliverypoint"] = str(tot_Star_4)  # 총 배점

            json_data_reviewinfo["writerid"] = str_id.text  # 작성자
            json_data_reviewinfo["writerdate"] = str_time.text  # 작성일(년월일) * 시간으로 되어 있는 것은 당일로 한다. * 날짜로 나오지 않아 의미 없음.)
            json_data_reviewinfo["writepoint"] = str(review_start1)  # 총점
            json_data_reviewinfo["writetastepoint"] = str(review_start2)  # 맛점
            json_data_reviewinfo["writequantitypoint"] = str(review_start3)  # 양점
            json_data_reviewinfo["writedeliverypoint"] = str(review_start4)  # 매점
            json_data_reviewinfo["orderinfo"] = str_menu.text  # 주문내역
            json_data_reviewinfo["contents"] = str_review.text  # 내용
            json_data_reviewinfolist.append(json_data_reviewinfo)

        LogPrint('리뷰 완료 ')
        return True
    except:
        LogPrint('리뷰 오류 !!!!')
        return False


# -------------------------------
def ydetailmainstart(sGetListAddress, istartnum, iendnum, reviewCnt1, reviewCnt2):
    global SqlRowData
    global driver
    global store_number

    global json_data_menuinfolist
    global json_data_reviewinfolist
    global json_data_storeinfo

    # 추후 각 필요한 텍스트 파일 읽어서 하는 것으로 처리 한다.
    # 임시로 특정 지역을 한다.
    # getsqldata(sGetListAddress)
    SqlRowData = mysql_controller.selectisaddr_se(sGetListAddress, istartnum, iendnum, reviewCnt1, reviewCnt2)
    #    SqlRowData = mysql_controller.selectisaddr2(sGetListAddress)

    LogPrint('가져오기 시작 | ' + str(len(SqlRowData)) + ' |' + sGetListAddress)
    iSqlRowCnt = 0
    for row in SqlRowData:
        try:
            driver = webdriver.Chrome(path, options=options)
        except:
            ErrorDataFileSave(
                'driver 생성 Error | ' + str(row[0]) + ' |번호| ' + str(row[1]) + ' | 검색주소|' + str(row[3]) + '|num|' + str(
                    store_number))
            time.sleep(DelayTime5)
            continue
        errcheckcode = 0
        try:
            # SiteName, KeyData, isCheck, isAddr, isDate
            store_number = str(row[1])

            store_number = '22322'
            #            store_number = '326573'

            LogPrint('조회상세정보 | ' + str(store_number) + ' | ' + str(row[0]) + ' |번호| ' + str(row[1]) + ' | 검색주소|' + str(
                row[3]) + '|' + str(iSqlRowCnt))

            # 초기화
            json_data_menuinfolist.clear()  # 메뉴 전체 치우기
            json_data_reviewinfolist.clear()  # 리뷰

            if yMainPageOpen(store_number) == False:
                ErrorDataFileSave('페이지 열기 실패 | ' + str(store_number) + ' | ' + str(row[0]) + ' |번호| ' + str(
                    row[1]) + ' | 검색주소|' + str(row[3]))
                mysql_controller.update_isCheckData(stoday, str(store_number))
                #                mysql_controller_B.update_isCheckData(stoday,str(store_number))
                driver.quit()
                time.sleep(DelayTime5)
                continue

            if get_store_name() == True:  # 상점명 가져 오기
                try:
                    time.sleep(1)
                    reviewcountcheck = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span')
                    LogPrint(
                        '상점명 : ' + store_Name + ' - ' + store_subName + '|' + store_number + ' | ' + reviewcountcheck.text)

                #                    if not ((int(reviewcountcheck.text) > reviewCnt1) and (int(reviewcountcheck.text) < reviewCnt2)): # 리뷰 갯수
                #                        errcheckcode = 2
                #                        ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | 리뷰갯수 | ' + reviewcountcheck.text + ' | !! [ 리뷰 갯수 '+str(reviewCnt1)+' 개 이상 ' + str(reviewCnt2) + ' 이하] !!')
                #                        LogPrint('!!!! 상점명 : ' + store_Name + ' - ' + store_subName + '|' + store_number)
                #                        continue
                except:
                    errcheckcode = 2
                    LogPrint('!! 상점명 : ' + store_Name + ' - ' + store_subName + '|' + store_number)
                    ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 리뷰 갯수 가져오기 실패  ] !!')
                    continue

                time.sleep(1)
                print('---=-=-=-=-=-==', store_number)

                #            if create_dir('./../images/yogiyo/' + store_Name) == True: #이미지저장 폴더 만들기
                if create_dir('./../images/yogiyo/' + store_number) == True:  # 이미지저장 폴더 만들기(상점번호)
                    if get_store_Menu() == True:  # 메뉴 (메뉴명, 가격, 메뉴 이미지)
                        """
                        if go_to_info() == True: # 정보텝으로 이동
                            if getinfo()==True: # 기본정보 가져오기
                                if go_to_review() == True: #리뷰 페이지 이동
                                    click_more_review() # 리뷰 더보기 클릭
                                    if getreview()==False: #리뷰 데이터 가져 오기
                                        errcheckcode = 5
                                        ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 리뷰 가져오기 오류. ] !!')
                                else:
                                    errcheckcode = 6
                                    ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 리뷰 페이지 못 찾음. ] !!')
                            else:
                                errcheckcode = 3
                                ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 기본정보 가져오기 오류. ] !!')
                        else:
                            errcheckcode = 4
                            ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 정보 페이지 못 찾음. ] !!')
                        """
                    else:
                        errcheckcode = 7
                        ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 메뉴 못찾음. ] !!')
                else:
                    errcheckcode = 8
                    ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 이미지 폴더 생성 못합. ] !!')
            else:
                errcheckcode = 9
                ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 상점 번호에서 상점명 못 찾음 ] !! ')
        except:
            errcheckcode = 1
            ErrorDataFileSave(str(errcheckcode) + ' | 알수 없는 오류|')
        finally:
            driver.quit()
            time.sleep(2)

        LogPrint('가져오기 완료 ( ' + str(iSqlRowCnt) + ' )')
        iSqlRowCnt = iSqlRowCnt + 1
        print('eeeee')
        break
        print('aaaaaa')
        exit()

        if errcheckcode == 0:
            try:  # 상세 데이터 저장
                jsontext1 = json.dumps(json_data_storeinfo, indent=4, ensure_ascii=False)
                stmpjson1 = jsontext1.replace('\\n', ' ')
                #                print(stmpjson1)

                json_data_ = OrderedDict()  # 기본 상점 정보
                json_data_["cnt"] = len(json_data_menuinfolist)
                json_data_["menu"] = json_data_menuinfolist
                jsontext2 = json.dumps(json_data_, indent=4, ensure_ascii=False)
                stmpjson2 = jsontext2.replace('\\n', ' ')
                #               print(stmpjson2)

                json_data2_ = OrderedDict()  #
                json_data2_["cnt"] = len(json_data_reviewinfolist)
                json_data2_["review"] = json_data_reviewinfolist
                jsontext3 = json.dumps(json_data2_, indent=4, ensure_ascii=False)
                stmpjson3 = jsontext3.replace('\\n', ' ')
                #                print(stmpjson3)

                #                print('DB 기록 - |', store_number, store_Name)
                mysql_controller.insertDeatil_Y(store_number, store_Name, stmpjson1, stmpjson2, stmpjson3,
                                                sGetListAddress)
            #                mysql_controller_B.insertDeatil_Y(store_number, store_Name, stmpjson1, stmpjson2, stmpjson3, sGetListAddress)
            except:
                errcheckcode = 2
                ErrorDataFileSave(store_number + '| ' + str(errcheckcode) + ' | 상세정보 저장 오류 !!')
                ErrorDataFileSave('======== DB Data Check Start')
                try:
                    ErrorDataFileSave(stmpjson1)
                except:
                    ErrorDataFileSave('!!!! stmpjson1 Error !!!!')
                ErrorDataFileSave('-------')
                try:
                    ErrorDataFileSave(stmpjson2)
                except:
                    ErrorDataFileSave('!!!! stmpjson2 Error !!!!')
                ErrorDataFileSave('-------')
                try:
                    ErrorDataFileSave(stmpjson3)
                except:
                    ErrorDataFileSave('!!!! stmpjson3 Error !!!!')
                ErrorDataFileSave('======= DB Data Check End')

        if errcheckcode == 0:
            try:  # 저장 완료 key 날짜 저장
                mysql_controller.update_isCheck(stoday, store_number)
                #                mysql_controller_B.update_isCheck(stoday, store_number)
                SuccOpenListFileSave(store_number + ' | ' + store_Name)
            except:
                ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | Key Data Update 오류 ')

        time.sleep(1)
        # 저장

        """
        print('페이지 확인 1 ->')
        jsontext = json.dumps(json_data_storeinfo, indent=4, ensure_ascii=False)
        LogPrint(jsontext)
        #    tmpz1 = json.dumps(json_data_reviewinfolist)
        #    print(tmpz1)
        LogPrint('페이지  확인 2 ->')

        json_data_ = OrderedDict()  # 기본 상점 정보
        json_data_["cnt"] = len(json_data_menuinfolist)
        json_data_["menu"] = json_data_menuinfolist

        jsontext = json.dumps(json_data_, indent=4, ensure_ascii=False)
        # tmpzz = json.dumps(json_data_menuinfolist)
        LogPrint(jsontext)

        json_data2_ = OrderedDict()  #
        json_data2_["cnt"] = len(json_data_reviewinfolist)
        json_data2_["review"] = json_data_reviewinfolist

        jsontext = json.dumps(json_data2_, indent=4, ensure_ascii=False)
        LogPrint(jsontext)

        # print('페이지  확인 2-1->')
        # print(json_data_menuinfolist)
        LogPrint('페이지 완료 확인 <-')
        """
    LogPrint(' 가져오기 끝 | ' + sGetListAddress)


def ydetailmainstart_MenuUpDate(sGetListAddress, stmpdate):
    global SqlRowData
    global driver
    global store_number

    global json_data_menuinfolist
    global json_data_reviewinfolist
    global json_data_storeinfo

    # 메뉴만 업데이트 하기 위해서 사용한다.
    SqlRowData = mysql_controller.selectisaddr_MenuupDate(stmpdate)
    #    SqlRowData = mysql_controller.selectisaddr2(sGetListAddress)

    LogPrint('가져오기 시작 2 | ' + str(len(SqlRowData)) + ' |' + sGetListAddress)
    iSqlRowCnt = 0
    for row in SqlRowData:
        try:
            driver = webdriver.Chrome(path, options=options)
        except:
            ErrorDataFileSave(
                'driver 생성 Error 2| ' + str(row[0]) + ' |번호| ' + str(row[1]) + ' | 검색주소|' + str(row[3]) + '|num|' + str(
                    store_number))
            time.sleep(DelayTime5)
            continue
        errcheckcode = 0
        try:
            # SiteName, KeyData, isCheck, isAddr, isDate
            store_number = str(row[1])

            LogPrint('조회상세정보 2| ' + str(store_number) + ' | ' + str(row[0]) + ' |번호| ' + str(row[1]) + ' | 검색주소|' + str(
                row[3]) + '|' + str(iSqlRowCnt))

            # 초기화
            json_data_menuinfolist.clear()  # 메뉴 전체 치우기
            json_data_reviewinfolist.clear()  # 리뷰

            if yMainPageOpen(store_number) == False:
                errcheckcode = 99
                ErrorDataFileSave('페이지 열기 실패 2 | ' + str(store_number) + ' | ' + str(row[0]) + ' |번호| ' + str(
                    row[1]) + ' | 검색주소|' + str(row[3]))
                mysql_controller.update_isCheckData(stoday, str(store_number))
                #                mysql_controller_B.update_isCheckData(stoday,str(store_number))
                driver.quit()
                time.sleep(DelayTime3)
                continue

            if get_store_name() == True:  # 상점명 가져 오기
                try:
                    time.sleep(1)
                    reviewcountcheck = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span')
                    LogPrint(
                        '상점명2 : ' + store_Name + ' - ' + store_subName + '|' + store_number + ' | ' + reviewcountcheck.text)

                except:
                    errcheckcode = 2
                    LogPrint('!! 상점명 2: ' + store_Name + ' - ' + store_subName + '|' + store_number)
                    ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 리뷰 갯수 가져오기 실패 2 ] !!')
                    continue

                time.sleep(1)

                if create_dir('./../images/yogiyo/' + store_number) == True:  # 이미지저장 폴더 만들기(상점번호)
                    if get_store_Menu() == False:  # 메뉴 (메뉴명, 가격, 메뉴 이미지)
                        errcheckcode = 7
                        ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 메뉴 못찾음. 2] !!')
                else:
                    errcheckcode = 8
                    ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 이미지 폴더 생성 못합. 2] !!')
            else:
                errcheckcode = 9
                ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 상점 번호에서 상점명 못 찾음 2] !! ')
        except:
            errcheckcode = 1
            ErrorDataFileSave(str(errcheckcode) + ' | 알수 없는 오류| 2')
        finally:
            driver.quit()
            time.sleep(2)

        LogPrint('가져오기 완료 ( ' + str(iSqlRowCnt) + ' )')
        iSqlRowCnt = iSqlRowCnt + 1
        #        break

        if errcheckcode == 0:
            try:  #
                json_data_ = OrderedDict()  # 기본 상점 정보
                json_data_["cnt"] = len(json_data_menuinfolist)
                json_data_["menu"] = json_data_menuinfolist
                jsontext2 = json.dumps(json_data_, indent=4, ensure_ascii=False)
                stmpjson2 = jsontext2.replace('\\n', ' ')
                #               print(stmpjson2)

                #                print('DB 기록 - |', store_number, store_Name)
                mysql_controller.insertDeatil_Menu_UpDate(store_number, stmpjson2)
            #                mysql_controller_B.insertDeatil_Menu_UpDate(store_number, stmpjson2)
            except:
                errcheckcode = 2
                ErrorDataFileSave(store_number + '| ' + str(errcheckcode) + ' | 상세정보 저장 오류 2 !!')
                ErrorDataFileSave('======== DB Data Check Start 2')
                try:
                    ErrorDataFileSave(stmpjson2)
                except:
                    ErrorDataFileSave('!!!! stmpjson2 Error !!!! 2')
                ErrorDataFileSave('======= DB Data Check End 2')

        if errcheckcode == 0:
            try:  # 저장 완료 key 날짜 저장
                mysql_controller.update_isCheck('2020-06-05', store_number)
                #                mysql_controller_B.update_isCheck('2020-06-05', store_number)
                SuccOpenListFileSave(store_number + ' | ' + store_Name)
            except:
                ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | Key Data Update 오류 2')

        time.sleep(1)
        # 저장
    LogPrint(' 가져오기 메뉴 끝 2 | ' + sGetListAddress)




# XX. 메뉴 이미지만 저장 하기 위함.
def filegetsave(spath, sfilename, sorgurl):
    try:
#        print(sorgurl)
        stmp = sorgurl
        stmp_sp1 = stmp.split('"')
        stmp_sp2 = stmp_sp1[1]
        stmp_sp3 = stmp_sp2.split("?")
        stmp_split4 = requests.get(stmp_sp3[0])
        open(spath + '/' + sfilename + '.jpg', 'wb').write(stmp_split4.content)
    except:
        ErrorDataFileSave('Image Save Fail : ' + spath + ' | ' + sfilename + ' | ' + sorgurl
                          )

def get_store_MenuImg():
    global json_data_menuinfolist
    global driver

    LogPrint('메뉴 가져오기 시작')
    try:
        # 메뉴 바 클릭 ( 펼쳐 줘야 메뉴명, 가격 등을 전부 가져 올수 있다. )

        try:
            img = driver.find_element_by_tag_name('div.logo')  # 이미지
            try:
                imgpath = './../images/yogiyo/' + store_number + '/' + store_Name + '.png'
                filegetsave('./../images/yogiyo/' + store_number, store_Name, img.get_attribute('style'))
                #img.screenshot(imgpath)
            except:
                ErrorDataFileSave('대표이미지 저장 오류')
        except:
            ErrorDataFileSave('대표이미지 없음')

        try:
            menubar = driver.find_elements_by_tag_name('h4.panel-title')
        except:
            LogPrint('bar not found')

        for icnt, item in enumerate(menubar):
            try:  # 메뉴바 클릭하기
                UpDn_Check = 1  # 펼처져 있는 것은 펼치지 않는다.
                try:
                    item_check_UPDN = item.find_element_by_class_name('pull-right.icon-arr-down')
                    UpDn_Check = 1
                except:
                    UpDn_Check = 0

                if UpDn_Check == 1:
                    item.click()
            except:
                LogPrint('메뉴바 클릭 오류')
                continue

        menugroup_arr = driver.find_elements_by_tag_name('div.panel.panel-default.ng-scope')  # 메뉴 그룹
        #        print(str(len(menugroup_arr)))
        #        for mgitem in tqdm(enumerate(menugroup_arr)):
        for inum, mgitem in tqdm(enumerate(menugroup_arr)):
            try:
                menugroptag = mgitem.find_element_by_tag_name('span.menu-name.pull-left.ng-binding.pop-menu')
                menugroupname = menugroptag.text
            #                print('그룹명0:' + menugroupname)
            except:
                try:
                    #                print(mgitem.page_source)
                    #                menugropclass = mgitem.find_element_by_class_name('menu-name.pull-left.ng-binding')
                    menugroptag = mgitem.find_element_by_tag_name('span.menu-name.pull-left.ng-binding')
                    menugroupname = menugroptag.text
                #                    print('그룹명1:'+ menugroupname)
                except:
                    print('class 로 찾기 실패 1 ')
                    continue

            review_arr = mgitem.find_elements_by_tag_name('li.ng-scope.photo-menu')
            for icnt, mditem in enumerate(review_arr):
                #                print(str(icnt), menugroupname)

                try:  # 메뉴명 가져오기
                    menu_name = mditem.find_element_by_tag_name('div.menu-name.ng-binding')
                except:
                    LogPrint('메뉴명 가져오기 실패 1')
                    continue

                try:  # 가격 가져오기
                    TmpPriceA = mditem.find_element_by_tag_name('span.ng-binding')
                except:
                    LogPrint('가격 가져오기 실패 2')
                    continue

                try:  # 설명
                    tmpmenudesc = mditem.find_element_by_tag_name('div.menu-desc.ng-binding')
                    tmpstr3 = tmpmenudesc.text
                except:
                    LogPrint('가격 가져오기 실패 3')
                    tmpstr3 = ''

                tmpstr = menu_name.text
                tmpstr2 = TmpPriceA.text

                #                print('메뉴 ?:' + tmpstr + ':'+tmpstr2 )
                if tmpstr == '':
                    continue

                #print('-----img ----')
                try:
                    imgpath = './../images/yogiyo/' + store_number + '/' + tmpstr + '.png'
                    try:  # 이미지가 있는 것만 하기 위함.
                        imgcheck = mditem.find_element_by_tag_name('td.photo-area')  # 이미지
                    except:
                        continue
                    try:
                        img = imgcheck.find_element_by_tag_name('div.photo')  # 이미지
                        filegetsave('./../images/yogiyo/'+ store_number, tmpstr, img.get_attribute('style'))
                    except:
                        print('img errr1')
                        continue
                except:
                    continue

        return True
    except:
        LogPrint('메뉴 오류 ~~~~~~!!!!!')
        time.sleep(1)
        return False


def yGet_MenuImage(iStartStoreNumber_S, iStartStoreNumber_E):
    global SqlRowData
    global driver
    global store_number

    global json_data_menuinfolist
    global json_data_reviewinfolist
    global json_data_storeinfo

    # 이미지만 가져오기위해서 사용한다.
    SqlRowData = mysql_controller.select_yogiyo_num(int(iStartStoreNumber_S), int(iStartStoreNumber_E))

    LogPrint('가져오기 시작 | ' + str(len(SqlRowData)) + ' |' + str(iStartStoreNumber_S) + '|' + str(iStartStoreNumber_E))

    iSqlRowCnt = 0
    for row in SqlRowData:
        try:
            driver = webdriver.Chrome(path, options=options)
        except:
            ErrorDataFileSave(#seq, Store_Name, Store_num
                'driver 생성 Error | ' + str(row[0]) + ' |번호| ' + str(row[1]) + '|' + str(row[2]))
            driver.quit()
            time.sleep(DelayTime5)
            continue

        errcheckcode = 0
        try:
            #seq, Store_Name, Store_num
            store_number = str(row[2])

#            store_number = '22322'
            #            store_number = '326573'
            # 초기화
            json_data_menuinfolist.clear()  # 메뉴 전체 치우기
            json_data_reviewinfolist.clear()  # 리뷰

            if yMainPageOpen(store_number) == False:
                ErrorDataFileSave('페이지 열기 실패 | ' + str(store_number) + ' | ' + str(row[0]) + ' |번호| ' + str(
                    row[1]) + ' | Num|' + str(row[2]))
#                mysql_controller.update_isCheckData(stoday, str(store_number))
                driver.quit()
                time.sleep(DelayTime5)
                continue

            if get_store_name() == True:  # 상점명 가져 오기
                try:
                    time.sleep(1)
                    reviewcountcheck = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span')
                    LogPrint(
                        '상점명 : ' + store_Name + ' - ' + store_subName + '|' + store_number + ' | ' + reviewcountcheck.text)

                except:
                    errcheckcode = 2
                    LogPrint('!! 상점명 : ' + store_Name + ' - ' + store_subName + '|' + store_number)
                    ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 리뷰 갯수 가져오기 실패  ] !!')
                    continue

                time.sleep(1)
                print('---=-=-=-=-=-==', store_number)

                #            if create_dir('./../images/yogiyo/' + store_Name) == True: #이미지저장 폴더 만들기
                if create_dir('./../images/yogiyo/' + store_number) == True:  # 이미지저장 폴더 만들기(상점번호)
                    if get_store_MenuImg() == False:  # 메뉴 (메뉴명, 가격, 메뉴 이미지)
                        errcheckcode = 7
                        ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 메뉴 못찾음. ] !!')
                else:
                    errcheckcode = 8
                    ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 이미지 폴더 생성 못합. ] !!')
            else:
                errcheckcode = 9
                ErrorDataFileSave(store_number + ' | ' + str(errcheckcode) + ' | !! [ 상점 번호에서 상점명 못 찾음 ] !! ')
        except:
            errcheckcode = 1
            ErrorDataFileSave(str(errcheckcode) + ' | 알수 없는 오류|')
        finally:
            driver.quit()
            time.sleep(2)


        time.sleep(1)
        # 저장

    LogPrint(' 메뉴 이미지 가져오기 끝 | ' )


def main():
    global StartStoreNumber_S
    global StartStoreNumber_E
    global reviewcntdown1
    global reviewcntdown2
    global StartAddr_A
    global StartAddr_B
    global menuupdate

    parser = argparse.ArgumentParser()
    parser.add_argument('A', type=str, help="시도 구군 Start End recnt_S recnt_E Number(6 argc)")
    parser.add_argument('B', type=str, help="시도 구군 Start End recnt_S recnt_E Number(6 argc)")
    parser.add_argument('S', type=int, help="시도 구군 Start End recnt_S recnt_E Number(6 argc)")
    parser.add_argument('E', type=int, help="시도 구군 Start End recnt_S recnt_E Number(6 argc)")
    parser.add_argument('C', type=int, help="시도 구군 Start End recnt_S recnt_E Number(6 argc)")
    parser.add_argument('X', type=int, help="시도 구군 Start End recnt_S recnt_E Number(6 argc)")
    #    parser.add_argument('M', type=str, help="시도 구군 Start End recnt_S recnt_E Number(6 argc)")

    try:
        args = parser.parse_args()
        StartAddr_A = args.A
        StartAddr_B = args.B
        StartStoreNumber_S = args.S
        StartStoreNumber_E = args.E
        reviewcntdown1 = args.C
        reviewcntdown2 = args.X
        #       menuupdate = args.M

        if reviewcntdown1 > reviewcntdown2:
            print('Test' + str(reviewcntdown1) + ' / ' + str(reviewcntdown2))
            exit()

    except:
        print('종료')
        exit()

def main_2():
    global StartStoreNumber_S
    global StartStoreNumber_E

    parser = argparse.ArgumentParser()
    parser.add_argument('S', type=str, help="S E(2 argc)")
    parser.add_argument('E', type=str, help="S E(2 argc)")

    try:
        args = parser.parse_args()
        StartStoreNumber_S = args.S
        StartStoreNumber_E = args.E

    except:
        print('종료')
        exit()

if __name__ == "__main__":
#    main()
    main_2()

    if create_dir('./../images') == False:
        LogPrint('이미지 폴더 생성 오류 1')
        quit()

    if create_dir('./../images/yogiyo') == False:
        LogPrint('이미지 폴더 생성 오류 2')
        quit()

    #    StartStoreNumber_S = 100000
    #    StartStoreNumber_E = 250000
    #    reviewcntdown1 = 4000
    #    reviewcntdown2 = 100000

    if StartAddr_A == 'ALL':
        seAddress = 'ALL'
    else:
        seAddress = StartAddr_A + ' ' + StartAddr_B

    # 시작.
    LogPrint(' ----- 시작 ----- [ ' + str(StartStoreNumber_S) + ' ~ ' + str(StartStoreNumber_E))

    #    if menuupdate != '0':
    #    ydetailmainstart_MenuUpDate(seAddress, menuupdate)
    #    else:
    #    ydetailmainstart(seAddress, StartStoreNumber_S, StartStoreNumber_E, reviewcntdown1, reviewcntdown2)

#    StartStoreNumber_S = 900
#    StartStoreNumber_E = 1000

    yGet_MenuImage(StartStoreNumber_S, StartStoreNumber_E)

    LogPrint(' ----- 완료 ----- [ ' + str(StartStoreNumber_S) + ' ~ ' + str(StartStoreNumber_E))

"""
 # json 배열 만들기.
lst = []
za = {}
za['te1'] = 'asdf'
za['te2'] = '1234'
lst.append(za)
za = {}
za['te1'] = 'ddddf'
za['te2'] = '1zxc'
lst.append(za)
#print(lst)
json_list = json.dumps(lst)
print(json_list)
"""

# driver.close()
# driver.quit()
"""
정보[storeinfo]
 - 상점명[storename]
 - 기본점수 ( 0 점 있음. ) [storepoint]
 - 영업시간[storetime]
 - 전화번호 ( 요기요 제공 번호 만 있음. )[storetel]
 - 주소[storeaddr]
 - 최소주문금액[storeminprice]
 - 상호명[storebizname]
 - 사업자등록번호[storebiznum]
 - 원산지 정보 ( 정보 없음 )[storeorigin]
 - 부가정보 (예:세스코멤버스 사업장, 없는 경우 있음.)[storeaddition]

메뉴[menuinfo]
 - 메뉴명 [menuname]
 - 가격[menuprice]
 - 메뉴 설명 ( 설명 없는 경우 있음 )[menuexplanation]
 - 이미지 ( 이미지 전체 없음, 상단이미지만 있음, 파일로 저장)

리뷰 ( * 리뷰가 없는 경우 있음 )[reviewinfo]
 - 총점[totalpoint]
 - 총 맛점[totaltastepoint]
 - 총 양점[totalquantitypoint]
 - 총 배점[totaldeliverypoint]

 - 작성자[writerid]
 - 작성일(년월일) * 시간으로 되어 있는 것은 당일로 한다.)[writerdate]
 - 총점[writepoint]
 - 맛점[writetastepoint]
 - 양점[writequantitypoint]
 - 배점[writedeliverypoint]
 - 주문내역[orderinfo]
 - 내용[contents]

** 주소 검색시 나올수 있는 확인 창.
  [알림] 서비스 가능 지역이 아닙니다. [확인]
"""

"""
driver = webdriver.Chrome(path, options=options)

driver.get('https://www.yogiyo.co.kr/mobile/#/78213/')
try:
    # id가 cMain인 tag를 10초 내에 검색, 그렇지 않으면 timeoutexception 발생
    element = WebDriverWait(driver, 0.1).until(
        # By.ID 는 ID로 검색, By.CSS_SELECTOR 는 CSS Selector 로 검색
#By.ID - 태그에 있는 ID 로 검색
#By.CSS_SELECTOR - CSS Selector 로 검색
#By.NAME - 태그에 있는 name 으로 검색
#By.TAG_NAME - 태그 이름으로 검색
#        EC.presence_of_element_located((By.ID, "panel.panel-default.ng-scope"))
        EC.presence_of_element_located((By.CSS_SELECTOR, "#menu > div > div:nth-child(2)"))
    )
    print(element.text)

except TimeoutException:
    print("해당 페이지에 cMain 을 ID 로 가진 태그가 존재하지 않거나, 해당 페이지가 10초 안에 열리지 않았습니다.")

finally:
    driver.quit()
"""
