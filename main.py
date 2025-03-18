# -*- coding: utf-8 -*-
import api
import os
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from selenium.common.exceptions import (NoSuchElementException, 
                                        ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        TimeoutException)
import time
KEY_PATH = "resources/KeyConfig.yaml"
CHAOJIYING_KIND = 9004

class TicketBot:
    def __init__(self):
        self._load_config()
        self.driver = self._init_driver()
        self.chaojiying = api.Chaojiying()
        self.nowaDate=""
        self.nowaPage=""

    def _load_config(self):
        with open(KEY_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.username = config["username"]
        self.password = config["password"]

    def _init_driver(self):
        options = webdriver.EdgeOptions()
        options.page_load_strategy = 'eager'
        options.add_argument('-ignore-certificate-errors')
        options.add_argument('-ignore-ssl-errors')
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        # options.add_argument("--headless")
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        return webdriver.Edge(options=options)

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3),
           retry=retry_if_exception_type((NoSuchElementException, TimeoutException)))
    def _find_element(self, by, value):
        return self.driver.find_element(by, value)

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3),
           retry=retry_if_exception_type((ElementClickInterceptedException, StaleElementReferenceException)))
    def _click_element(self, element):
        element.click()

    def login(self):
        try:
            print("正在登录中...")
            self.driver.get("https://cgyy.buaa.edu.cn/venue/login")
            
            # 登录按钮操作
            login_btn = self._find_element(By.CLASS_NAME, "loginFlagWrapItem")
            self._click_element(login_btn)
            
            # 切换iframe
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it("loginIframe"))
            
            # 输入凭证
            userbox = self._find_element(By.NAME, "username")
            userbox.send_keys(self.username)
            
            passbox = self._find_element(By.NAME, "password")
            passbox.send_keys(self.password)
            
            # 提交登录
            submit_btn = self._find_element(
                By.XPATH, "/html/body/div[2]/div/div[3]/div[2]/div[1]/div[7]/input")
            self._click_element(submit_btn)
            
            # 等待登录成功
            WebDriverWait(self.driver, 10).until(
                EC.url_to_be("https://cgyy.buaa.edu.cn/venue/home"))
            
            self.driver.get("https://cgyy.buaa.edu.cn/venue/venue-reservation/39")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("登录成功!正在查询场地...")
        except Exception as e:
            print(f"登录失败: {str(e)}")
            raise

    def get_nearest_option(self) -> list:
        access_list = []
        time.sleep(2)
        date_box = self._find_element(By.CLASS_NAME, "date_box")
        for date_div in date_box.find_elements(By.TAG_NAME, "div"):
            self.nowaDate=date_div
            if '\n' not in date_div.text:
                continue
                
            self._click_element(date_div)
            time.sleep(2)
            table = self._find_element(
                By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div/div[1]/div[2]/div[2]/div/div/div/div/table")
            page=0
            # 解析表格数据
            while True:
                try:
                    lastbutton=self.driver.find_element(By.XPATH,'//*[@id="scrollTable"]/table/thead/tr/td[6]/div/i')
                except:
                    self.nowaPage=page
                    break
                headers = [td.text for tr in table.find_element(By.TAG_NAME, "thead").find_elements(By.TAG_NAME, "tr") 
                        for td in tr.find_elements(By.TAG_NAME, "td")]
            
                for idx, tr in enumerate(table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")):
                    cells = tr.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        continue
                    
                    court_number = cells[0].text
                    for i, td in enumerate(cells[1:], start=1):
                        if td.text.startswith("￥"):
                            print(f"{page}-{len(access_list)+1}: 可预约场地 - 日期:{date_div.text.split('\n')[1]} "
                                f"时间段:{headers[i]} 场地:{court_number} 价格:{td.text}")
                            # 修改为基于表格行号的XPath定位
                            xpath = f"//tbody//tr[{idx+1}]/td[{i+1}]"
                            access_list.append([date_div, xpath,page])
                self._click_element(lastbutton)
                page+=1           
        return access_list
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3),
           retry=retry_if_exception_type((ElementClickInterceptedException, StaleElementReferenceException)))
    def buy_ticket(self, ticket):
        try:
            # 根据存储的信息重新定位元素
            date_div,xpath,page = ticket
            # 重新查找日期元素``
            if not date_div.text.startswith(self.nowaDate.text):
                self._click_element(date_div)
                self.nowaDate=date_div
                self.nowaPage=0
            # 等待并重新定位表格
            time.sleep(2)
            while page!=self.nowaPage:
               if page<self.nowaPage:
                   self._click_element(self.driver.find_element(By.XPATH,'//*[@id="scrollTable"]/table/thead/tr/td[2]/div/i'))
                   self.nowaPage-=1
               else:
                   self._click_element(self.driver.find_element(By.XPATH,'//*[@id="scrollTable"]/table/thead/tr/td[6]/div/i'))
                   self.nowaPage+=1
               time.sleep(1)
            # 定位目标单元格
            target_td = self._find_element(By.XPATH, xpath)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_td)
            self._click_element(target_td)
            
            # 选择同伴
            buddy_box = self._find_element(By.CLASS_NAME, "buddy-box")
            self._click_element(buddy_box.find_element(By.TAG_NAME, "div"))
            
            # 勾选协议
            checkbox = self._find_element(By.CLASS_NAME, "ivu-checkbox-input")
            self._click_element(checkbox)
            
            # 提交订单
            submit_btn = self._find_element(
                By.XPATH, "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[5]/div[2]/div[1]")
            self._click_element(submit_btn)
            
            # 处理验证
            code_element = self._find_element(
                By.XPATH, "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div")
            code_element.screenshot("code.png")
            
            # 识别验证码
            with open('code.png', 'rb') as f:
                res = self.chaojiying.PostPic(f.read(), CHAOJIYING_KIND)
            os.remove("code.png")
            
            # 点击验证码坐标
            code_width = code_element.size['width'] / 2
            code_height = code_element.size['height'] / 2
            points=api.get_points(res)
            for point in points:
                ActionChains(self.driver).move_to_element_with_offset(
                    code_element, point[0]-code_width, point[1]-code_height).click().perform()
                time.sleep(1)
            self._click_element(submit_btn)
            print(f"提交成功! 当前页面: {self.driver.current_url}")
        except Exception as e:
            print(f"购票失败: {str(e)}")
            raise

    def run(self):
        try:
            self.login()
            tickets = self.get_nearest_option()
            
            if not tickets:
                print("没有可预约的场地")
                return
                
                
            selection = int(input("请输入选票序号: "))
            if not 1 <= selection <= len(tickets):
                raise ValueError("无效的序号")
                
            self.buy_ticket(tickets[selection-1])
        except Exception as e:
            print(f"程序运行异常: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    bot = TicketBot()
    bot.run()


