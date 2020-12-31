import eel
import socket
import pandas as pd
import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import datetime
from selenium.webdriver.common.action_chains import ActionChains
import threading
import sys

LOG_FILE_PATH = "./log/log_###DATETIME###.log"
log_file_path=LOG_FILE_PATH.replace("###DATETIME###",datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))



CHROME_ARGS = [
    '--incognit',  # シークレットモード
    '--disable-http-cache',  # キャッシュ無効
    '--disable-plugins',  # プラグイン無効
    '--disable-extensions',  # 拡張機能無効
    '--disable-dev-tools',  # デベロッパーツールを無効にする
]
ALLOW_EXTENSIONS = ['.html', '.css', '.js', '.ico']

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 0))
port = s.getsockname()[1]
s.close()

options = {
        'mode': "chrome",
        'close_callback': exit,
        'port': port,
        'cmdline_args': CHROME_ARGS
}
size=(700,600)

def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)

### ログファイルおよびコンソール出力
def log(txt):
    now=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log',now , txt)
    # ログ出力
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)

def worker1(url,name,price):
    global count
    global success
    global fail
    
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", True)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", True)

    driver.get(url)
    time.sleep(2)
    try:
        timer_and_suggest = driver.find_elements_by_class_name("worksummary__text")
        
        timer = timer_and_suggest[0].text
        suggest = timer_and_suggest[1].text

        timer_list.append(timer)
        name_list.append(name)
        price_list.append(price)
        suggest_list.append(suggest)
        url_list.append(url)
        site_list.append("ランサーズ")

        log("{}件目成功 : {}".format(count,name))
        eel.view_log_js("{}件目成功 : {}".format(count,name))
        success+=1
        
    except Exception as e:
        log("{}件目失敗 : {}".format(count,name))
        eel.view_log_js("{}件目失敗 : {}".format(count,name))
        log(e)
        fail+=1
    finally:
        count+=1
    

    driver.close()



def cw(word,csv_name,check):
    global count
    global success
    global fail

    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", True)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", True)
    
    #マウスオーバーを使うための宣言みたいなもの
    actions = ActionChains(driver)

    # Webサイトを開く
    driver.get("https://crowdworks.jp/public/jobs?category=jobs&order=score&ref=toppage_hedder")
    time.sleep(3)
    word_bar = driver.find_elements_by_class_name("parent.cw-list_nav_subcategory_wrapper")

    scr = 20
    flg = False
    for w in word_bar:
        driver.execute_script("window.scrollTo({}, {})".format(0,scr))
        scr += 15
        actions.move_to_element(w).perform()
        mini_cgr = w.find_elements_by_tag_name("a")
        for a in mini_cgr:
            if a.text == word:
                mini_cgr_url = a.get_attribute("href")
                flg = True
                break
        if flg:
            break
    
    

    try:
        driver.get(mini_cgr_url)
        time.sleep(3)
    except Exception as e:
        log("選択したカテゴリが見つかりません、終了します カテゴリ名: {}".format(word))
        eel.view_log_js("選択したカテゴリが見つかりません、終了します カテゴリ名: {}".format(word))
        log(e)
        return
    
    #募集終了案件を除外する
    if check:
        check_box = driver.find_element_by_class_name("filter.display-options")
        check_box.find_element_by_class_name("cw-checkbox_inline").click()
        time.sleep(3)

    # name_list = []
    # price_list = []
    # suggest_list = []
    # url_list = []
    # timer_list = []
    # cw_list = []

    #次ページがなくなるまで探索
    while True:

        time.sleep(3)

        job_items = driver.find_elements_by_class_name("item_body.job_data_body")
        for job_item in job_items:
            try:
                name_a_url = job_item.find_element_by_class_name("item_title")
                job_name = name_a_url.find_element_by_tag_name("a")
                name_list.append(job_name.text)
                url_list.append(job_name.get_attribute("href"))

                price_list.append(job_item.find_element_by_class_name("entry_data.payment").text)
                suggest_list.append(job_item.find_element_by_class_name("entry_data.entries").text)
                timer_list.append(job_item.find_element_by_class_name("entry_data.expires").text)
                site_list.append("クラウドワークス")
                
                
                log("{}件目成功 : {}".format(count,job_name.text))
                eel.view_log_js("{}件目成功 : {}".format(count,job_name.text))
                success+=1
                print(job_name.text)
                    
            except Exception as e:
                log("{}件目失敗 : {}".format(count,job_name.text))
                eel.view_log_js("{}件目失敗 : {}".format(count,job_name.text))
                log(e)
                fail+=1
            finally:
                count+=1

        next_page = driver.find_elements_by_class_name("to_next_page")
        if len(next_page) >= 1:
            next_page_link = next_page[0].get_attribute("href")
            driver.get(next_page_link)
        else:
            log("クラウドワークス最終ページです。")
            eel.view_log_js("クラウドワークス最終ページです。")
            driver.close()
            # df = pd.DataFrame({"案件名":name_list,
            #            "価格":price_list,
            #            "提案・契約数":suggest_list,
            #            "残り時間":timer_list,
            #            "URL":url_list},
            #            "サイト":cw_list)
            return

def lc(word,csv_name,check):
    global count
    global success
    global fail
    
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", True)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", True)

    #マウスオーバーを使うための宣言みたいなもの
    actions = ActionChains(driver)
    
    # Webサイトを開く
    driver.get("https://www.lancers.jp/work/search?open=1&ref=header_menu")
    time.sleep(3)

    #仕事を受けるをクリック
    driver.find_element_by_class_name("css-1ptmxrx").click()
    time.sleep(1)

    #仕事のカテゴリバーを出す
    word_bar = driver.find_element_by_class_name("css-d2rq9g")
    actions.move_to_element(word_bar).perform()
    category_list = driver.find_element_by_class_name("MuiPopover-root")
    category_search = category_list.find_element_by_class_name("css-0")
    word_bar = category_search.find_elements_by_tag_name("a")
    
    
    flg = False
    for w in word_bar:
        if word == w.text:
            mini_cgr_url = w.get_attribute("href")
            break

        actions.move_to_element(w).perform()
        mini_category_list = driver.find_element_by_class_name("MuiPopover-root")
        mini_category_search = mini_category_list.find_elements_by_class_name("css-0")[2]
        mini_word_bar = mini_category_search.find_elements_by_tag_name("a")
        
        for mini_w in mini_word_bar:
            if word == mini_w.text:
                mini_cgr_url = mini_w.get_attribute("href")
                flg = True
                break

        if flg:
            break

    try:
        driver.get(mini_cgr_url)
        time.sleep(3)
    except Exception as e:
        log("選択したカテゴリが見つかりません、終了します カテゴリ名: {}".format(word))
        eel.view_log_js("選択したカテゴリが見つかりません、終了します カテゴリ名: {}".format(word))
        log(e)
        return
    
    #募集終了案件を除外する
    if check == False:
        driver.find_element_by_xpath("/html/body/div[3]/div[2]/main/section/section/div[1]/div[1]/nav/div[5]/dl/dd[1]/ul/li/div/label/a").click()
        time.sleep(3)

    #固定報酬のみにする
    job_cat = driver.find_element_by_class_name("p-search-sidenav__list.js-sp-jobStyle-toggle-target")
    price_fix = job_cat.find_elements_by_class_name("c-link")[2]
    driver.get(price_fix.get_attribute("href"))
    time.sleep(3)

    #次ページがなくなるまで探索
    while True:
        
        time.sleep(3)
        #広告を除外
        job_items = driver.find_elements_by_class_name("c-media-list__item:not(.p-search-pr):not(.c-media--clickable )")
        one_page_name_list = []
        one_page_url_list = []
        one_page_price_list = []
        

        for job_item in job_items:
            
            job_name = job_item.find_element_by_class_name("c-media__title")
            one_page_name_list.append(job_name.text)
            url = job_name.get_attribute("href")
            one_page_url_list.append(url)
            one_page_price_list.append(job_item.find_element_by_class_name("c-media__job-price").text)

        # スレッドを 要素数 分つくる
        threads = []
        i = 0
        for one_page_url in one_page_url_list:
            t = threading.Thread(target=worker1,args=(one_page_url,one_page_name_list[i],one_page_price_list[i]))
            t.setDaemon(True)
            t.start()
            threads.append(t)
            i+=1

        for thread in threads:
            thread.join()


        next_page = driver.find_elements_by_class_name("pager__item.pager__item--next")
        if len(next_page) >= 1:
            next_page_aTag = next_page[0].find_element_by_tag_name("a")
            next_page_link = next_page_aTag.get_attribute("href")
            driver.get(next_page_link)
        else:
            log("ランサーズ最終ページです。")
            eel.view_log_js("ランサーズ最終ページです。")
            driver.close()
            break
        
    # #csvファイルに出力    
    # df = pd.DataFrame({"案件名":name_list_lc,
    #                    "価格":price_list_lc,
    #                    "提案・契約数":suggest_list_lc,
    #                    "残り時間":timer_list_lc,
    #                    "URL":url_list_lc},
    #                    "サイト":lc_list)
    return

@eel.expose
def main(cw_word,lc_word,csv_name,check):
    global count
    global success
    global fail
    log("スタートします")
    lc_df = threading.Thread(target=lc,args=(lc_word,csv_name,check))
    lc_df.setDaemon(True)
    cw_df = threading.Thread(target=cw,args=(cw_word,csv_name,check))
    cw_df.setDaemon(True)
    lc_df.start()
    cw_df.start()
    
    lc_df.join()
    cw_df.join()
    
    df = pd.DataFrame({"案件名":name_list,
                       "価格":price_list,
                       "提案・契約数":suggest_list,
                       "残り時間":timer_list,
                       "URL":url_list,
                       "サイト":site_list})

    df.to_csv("{}".format(csv_name),encoding="utf_8-sig")
    log("処理完了 成功件数: {} 件 / 失敗件数: {} 件".format(success,fail))

count = 0
success = 0
fail = 0
name_list = []
price_list = []
suggest_list = []
url_list = []
timer_list = []
site_list = []

eel.init('web',allowed_extensions=ALLOW_EXTENSIONS)
eel.start('index.html',options=options,size=size, suppress_error=True)