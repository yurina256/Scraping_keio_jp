from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service # Serviceをインポート
import os
import time
import datetime
from dotenv import load_dotenv

def parse_lesson_data(data_string):
    cleaned_string = ' '.join(data_string.replace('　', ' ').split())
    parts = cleaned_string.split(' ')
    if len(parts) >= 6:
        teacher_name = parts[-1]
        lesson_name_parts = parts[3:-1]
        lesson_name = ' '.join(lesson_name_parts)
        lesson_time = parts[1]
        lesson_date = parts[0]
        if(lesson_name == "科目名 担当者"): return False
        return {
            'course':lesson_name,
            'date':lesson_date,
            'period':lesson_time[1]+"限",
            'canceled':True,
            'source':"K-Support",
            'message':"None"
        }
 
def get_classinfo(alluser:bool = True) -> object:
    """
    当日の休講情報を{'course':授業名,……}の配列で返す
    """
    load_dotenv()
    ID = os.environ.get("KEIO_ID") # keio id
    PW = os.environ.get("KEIO_PW") # keio id pw

    try:
        # Optional settings of chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu') #この辺は適宜コメントアウトを入り切り

        # ChromeDriverのパスを指定(通ってれば省略可)
        service = Service()

        # Boot chrome driver
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(15) # Time out 15 sec

        # GET (init)
        print("Accessing https://keio.jp...")
        driver.get("https://keio.jp")

        print("Waiting for redirection to Okta authentication page...")
        WebDriverWait(driver, 20).until(
            EC.url_contains("okta.com")
        )
        print(f"Redirected to: {driver.current_url}")

        id_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='identifier']"))
        )
        id_element.send_keys(ID)

        #Click next button
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='次へ']"))
        )
        next_button.click()

        #PW element
        pw_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='credentials.passcode']"))
        )
        pw_element.send_keys(PW)

        # Click login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='確認']"))
        )
        login_button.click()
        WebDriverWait(driver, 20).until(
            EC.staleness_of(login_button) # 前のログインボタンがDOMから消えるのを待つ
        )
        print("login ok")
        WebDriverWait(driver, 20).until(
            EC.url_contains("my.site.com")
        )
        print("k-support ok")
        driver.get("https://gacad.keio.jp/rishu/login-lecinfo");

        #履修中科目のみのボタンを外す
        if(not alluser):
            radio_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#condition_filter"))
                )
            radio_button.click()
        today = datetime.date.today()

        formatted_date = today.strftime("%Y/%m/%d")
        #formatted_date = "2025/7/15"

        print(f"今日の日付: {formatted_date}")
        #開始日
        startdate_input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#startdate_filter"))
        )
        startdate_input_field.clear()
        startdate_input_field.send_keys(formatted_date) #"YYYY/MM/DD"で指定
        #終了日
        enddate_input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#enddate_filter"))
        )
        enddate_input_field.clear()
        enddate_input_field.send_keys(formatted_date) #"YYYY/MM/DD"で指定        
        #検索ボタンを押す
        search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#lecinfoSearch"))
            )
        search_button.click()
        try:
            search_result_list_div = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#search-result-list"))
                )
            print(search_result_list_div.text)

            parsed_results = []
            for line in search_result_list_div.text.strip().split('\n'):
                if line: # 空行をスキップ
                    result = parse_lesson_data(line)
                    if result: # パースに成功した場合のみ追加
                        parsed_results.append(result)
            for item in parsed_results:
                print(item)
            print(parsed_results)
            return parsed_results
        except:
            print("休講情報なし")
            print([])
            return []

        # time.sleep(5)
    except Exception as e:
        print(f"スクレイピング中に何らかのエラーが発生しました : {e}")
# おわり #

if __name__ == "__main__":
    get_classinfo(False)