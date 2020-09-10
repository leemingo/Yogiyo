# -*- coding: utf-8 -*-
import argparse
#import os
import time
#import requests
import random
import dbconfig
#import pymysql

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from bs4 import BeautifulSoup
#from urllib import parse

from tqdm import tqdm

StartSi_Name = ''
StartGu_Name = ''

options = webdriver.ChromeOptions()
# webdriver 안보이게 하는 옵션
options.headless = True
options.add_argument('SameSite=None')
options.add_argument('headless')
options.add_argument('disable-gpu')
#options.add_argument('lang=euc-KR')
options.add_argument('lang=utf8')

#path = "/Users/seungwonkim/Craw_Py/chromedriver"
path = "./../chromedriver"
globalAddr = ''
driver = ''

#mysql_controller_C = dbconfig.MysqlController('49.50.165.72', 3306, 'kswer', 'happy@1207', 'crawl')

mysql_controller_C = dbconfig.MysqlController('192.168.0.30', 3306, 'jin', 'jj8995', 'crawl')
mysql_controller_B = dbconfig.MysqlController('192.168.0.13', 3306, 'ucrawl', 'happy@1207', 'crawl')


stoday = '%04d-%02d-%02d' % (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)

def LogPrint(strtmp):
    sTime = '%02d:%02d:%02d' % (time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
    print(stoday, sTime, strtmp)

def ErrorDataFileSave(strtmp):
    stoday = '%04d-%02d-%02d' % (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)
    sTime = '%02d:%02d:%02d' % (time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
    fTmp = stoday + ' ' + sTime + ' ' + strtmp

    print(fTmp)

    fs = open('./../yogiyolistError.txt', 'a+t')  # 파일 쓰기
    fs.write(fTmp)
    fs.write('\n')  # 라인 개행.
    fs.close()

def SuccOpenListFileSave(strtmp):
    stoday = '%04d-%02d-%02d' % (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)
    sTime = '%02d:%02d:%02d' % (time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
    fTmp = stoday + ' ' + sTime + ' ' + strtmp

    fs = open('./../yogiyoListSucc.txt', 'a+t')  # 파일 쓰기
    fs.write(fTmp)
    fs.write('\n')  # 라인 개행.
    fs.close()

def delaySec(startSec, endSec):
    # 잠시 멈추기
    try:
        wait = random.randint(startSec, endSec)
        WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.CLASS_NAME, "temp waitting...")))
    except TimeoutException:
        pass
#    finally:
#        print('잠시 멈춤 (%d)' % wait)

def selectSort(name):
    #
    # 거리순 컴포넌트 체크
    #
    try:
        # 옵션 목록 확인
        #
        ele = WebDriverWait(driver, random.randint(5, 5)).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-option-inner")))
        ele.click()
        delaySec(1, 3)

        # 옵션 선택
        #
        ele = driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[1]/div[2]/div/select/option[text()="%s"]' % name)
        ele.click()
        delaySec(1, 3)

        # 다른 곳 클릭
        #
        ele = WebDriverWait(driver, random.randint(1, 3)).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nav-top.clearfix")))
        ele.click()
        try:
            delaySec(1, 3)
        except:
            time.sleep(3)

    except TimeoutException:
        LogPrint('Time Out')
        return False
        pass
    finally:
        LogPrint('%s 선택......' % name)

    return True

def searchAddr(addr):
    global driver

    try:
        # 검색어 입력
        eleItem = driver.find_element_by_xpath('//*[@id="search"]/div/form/input')
        eleItem.clear()
        delaySec(1, 2)

        eleItem.send_keys(addr)
        delaySec(1, 2)

        #  검색 클릭
        eleItem = driver.find_element_by_xpath('//*[@id="button_search_address"]/button[2]')
        eleItem.click()
        delaySec(2, 4)

        #LogPrint('%s 검색어 입력.....' % addr)
#        delaySec(2, 3)
        return True
    except:
        return False

def StartMain(spostaddr_sido, spostaddr_sigungu):
    global globalAddr
    global mysql_controller_C
    global mysql_controller_B
    global driver

    try:
        #
        #  처음시작할 URL 로 이동
    #    url = 'https://yogiyo.co.kr/mobile/#/' + parse.quote('서울특별시') + '/135244/'
#        searchCmpStr = '관악구'

#        url = 'https://yogiyo.co.kr/mobile/#/'
#        driver.get(url)
#        delaySec(1, 3)

        # 주소 DB  검색.
#        spostaddr_sido = '서울특별시'
#        spostaddr_sigungu = '관악구'

        try:
            LogPrint('검색 시작 - ' + spostaddr_sido + ' ; ' + spostaddr_sigungu)

            post_row = mysql_controller_C.selectpostgroup(spostaddr_sido, spostaddr_sigungu)
            for loop_post_row in tqdm(post_row):
                try:
                    spostaddr_roadname = loop_post_row[2]
#                    LogPrint(spostaddr_roadname)

                    sql_roadname = mysql_controller_C.selectpostgrouplimit(spostaddr_sido, spostaddr_sigungu, spostaddr_roadname)
                    if len(sql_roadname) < 0:
                        LogPrint('없음['+spostaddr_sido + ' '+ spostaddr_sigungu + ' '+ spostaddr_roadname)
                        continue

                    try:
                        # sido, sigungu, hName, roadname, buildingCode1, buildingCode2
                        SuccOpenListFileSave(sql_roadname[0][3] + ' | ' +  sql_roadname[0][4]+ ' | ' +  sql_roadname[0][5])
                        # 크롬 오픈.
                        driver = webdriver.Chrome(path, options=options)
                        time.sleep(1)

                        # 처음 페이지 오픈.
                        url = 'https://yogiyo.co.kr/mobile/#/'
                        driver.get(url)
                        delaySec(3, 5)
                        # 오픈된 페이지 주소 검색
                        if sql_roadname[0][5] != '0':  # 건물번호부번 있는 경우 (0 이 아님)
                            sAddr = sql_roadname[0][3] + sql_roadname[0][4] + sql_roadname[0][5]
                        else:
                            sAddr = sql_roadname[0][3] + sql_roadname[0][4]

                        sigungu_addr = sql_roadname[0][0] + ' ' + sql_roadname[0][1]
#                        LogPrint('검색할주소 :' + sAddr)

                        if searchAddr(sAddr) == True:  # 주소 검색

                            idx = 0

                            sitemlist = driver.find_elements_by_class_name('item.clearfix')
                            MaxCount = len(sitemlist)

#                            LogPrint('-----item.clearfix count [' + str(MaxCount) + ']')

                            for icnt, sitem in tqdm(enumerate(sitemlist)):
                                # 상세정보 들어가기
                                # 상점 선택
                                try:
#                                    LogPrint('Count - ' + str(icnt) + '/' + str(MaxCount))
                                    sitemlistNext = driver.find_elements_by_class_name('item.clearfix')
                                    #                            print(sitemlistNext[icnt].text)
                                    #                            print('  ---------------- ')
                                    sitemlistNext[icnt].click()
                                    delaySec(3, 5)
                                    #                            idx += 1

                                    #                           print(str(idx))
                                    # DB 저장
                                    #
                                    reviewcountcheck = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span')
                                    key = driver.current_url
                                    #            LogPrint('Check Url : ' + key)
                                    keySplit = key.split('/')
                                    #                            LogPrint('url number :[ ' + str(idx) +  ' ] ' + keySplit[5] + ' [ ' + addr + ' / ' + Sql_address + ']')
                                    SuccOpenListFileSave('url number :[ ' + str(icnt) + '/'+str(MaxCount) + ']' + keySplit[5] +'|'+reviewcountcheck.text+ ' [ ' + sAddr + ' / ' + sigungu_addr + ']')
                                    #                            mysql_controller_C.searchinsert_key(keySplit[5])
                                    try:
                                        mysql_controller_C.searchinsert_key3(keySplit[5], sigungu_addr, reviewcountcheck.text)
                                    except:
                                        ErrorDataFileSave('DB Cur 기록 오류')

                                    try:
                                        mysql_controller_B.searchinsert_key3(keySplit[5], sigungu_addr, reviewcountcheck.text)
                                    except:
                                        ErrorDataFileSave('DB Backup 기록 오류')
                                except:
                                    ErrorDataFileSave('페이지오류:' + sAddr + ' | ' + str(idx) + ' | '+ str(MaxCount))
                                    break
                                finally:
                                    try:
                                        driver.back()
                                        delaySec(3, 4)
                                    except:
                                        ErrorDataFileSave('driver.back error:( ) ' + sAddr + ' | ' + str(idx) + ' | ')
                                        break

                                delaySec(1, 1)
                        #                       delaySec(2, 4)
                        #                else:
                        #                    ErrorDataFileSave('정렬오류:( ' + str(fs_lineCount) + ' ) ' + addr + ' [ ' + sigungu_addr + ' ]')
                        else:
                            ErrorDataFileSave('검색오류주소:( ) ' + sAddr + ' [ ' + sigungu_addr + ' ]')
                    except:
                        ErrorDataFileSave('검색상세:( ) ' + sAddr + ' [ ' + sigungu_addr + ' ]')
                    finally:
                        driver.quit()

                except:
                    ErrorDataFileSave('검색  Error [' +  loop_post_row[0] + ' ' + loop_post_row[1] + ' ' +spostaddr_roadname + ']')
        except:
            ErrorDataFileSave('처음 DB Error')

    finally:
#        driver.quit()
        print('end.................')


#spostaddr_sido = '서울특별시'
#spostaddr_sigungu = '관악구'


def main():
    global StartSi_Name
    global StartGu_Name

    parser = argparse.ArgumentParser()
    parser.add_argument('S', type=str, help="StartSi_Name StartGu_Name (2 argc)")
    parser.add_argument('E', type=str, help="StartSi_Name StartGu_Name (2 argc)")

    try:
        args = parser.parse_args()
        StartSi_Name = args.S
        StartGu_Name = args.E
    except:
        print('종료')
        exit()

if __name__ == "__main__":
    main()
    print('시작 주소:' + StartSi_Name + ' | ' + StartGu_Name)
    StartMain(StartSi_Name, StartGu_Name) # 처음으로 목록을 가져 오도록 한다.
#StartErrorListMain() # 목록 오류를 가져 온다. 특정 목록


#세종특별자치시 는 (구) 가 없다.
# 1. 다음과 같은 방법 으로 조회를 한다음.
#select sido, sigungu, roadname  from post where sido='서울특별시' and sigungu='관악구' group by roadname order by roadname asc;
#select sido, sigungu, roadname  from post where sido='서울특별시' and sigungu='강남구' group by roadname order by roadname asc;

# 2. 도로명 주소 1개를 가져와 조회를 한다.
# select sido, sigungu, hName, roadname from post where sido='서울특별시' and sigungu='관악구' group by hname, roadname;
# select sido, sigungu, hName, roadname, buildingCode1, buildingCode2 from post
#    where sido='서울특별시' and sigungu='관악구' and roadname='대학14길' limit 1;




