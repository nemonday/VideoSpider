import os
import time
from random import choice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.ui as ui

from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.settings import User_Agent_list

LOG_DIRECTORY = "./"

class Print(object):
    @staticmethod
    def info(message):
        out_message =  Print.timeStamp() + '  ' + 'INFO: ' +str(message)
        Print.write(out_message)
        print(out_message)

    @staticmethod
    def write(message):
        log_path = os.path.join(LOG_DIRECTORY, 'log.txt')
        with open(log_path,'a+') as f:
            f.write(message)
            f.write('\n')

    @staticmethod
    def timeStamp():
        local_time = time.localtime(time.time())
        return time.strftime("%Y_%m_%d-%H_%M_%S", local_time)


class GithubStart(object):
    def __init__(self):
        self.opt = webdriver.ChromeOptions()
        self.opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
        self.opt.add_argument('--disable-dev-shm-usage')
        self.opt.add_argument('--no-sandbox')
        # display = Display(visible=0, size=(800, 600))
        # display.start()

        # self.proxy = requests.get('http://http.tiqu.alicdns.com/getip3?num=1&type=1&pro=0&city=0&yys=0&port=1&time=2&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=')
        # self.opt.add_argument('--proxy-server=http://{}'.format(self.proxy.text))
        # self.prefs = {"profile.managed_default_content_settings.images": 2}
        # self.opt.add_experimental_option("prefs", self.prefs)
        # self.opt.add_argument('--headless')
        self.broser = webdriver.Chrome(options=self.opt)
        self.wait = WebDriverWait(self.broser, 20, 0.5)
        self.login_url = 'https://miku.tools/tools/toutiao_video_downloader'
        # 登陆获取链接的网站
        self.broser.get(self.login_url)

    def is_visible(self, locator, timeout=10):
        try:
            ui.WebDriverWait(self.broser, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except Exception as f:
            return False

    def run(self):
        try:
            urls = ['http://m.toutiaoimg.cn/i6686269240195940877/', 'https://www.365yg.com/a6696432875174101511']
            # 判断弹窗是否存在
            exists = self.is_visible('//*[@id="__layout"]/div/div[1]/div/div[2]/div[2]/button')
            # 如果弹窗存在， 就点击close
            if exists is True:
                self.broser.find_element_by_xpath('//*[@id="__layout"]/div/div[1]/div/div[2]/div[2]/button').click()
                url_box = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="http://www.365yg.com/a6660790867638373640"]')))
                for url in urls:
                    # 输入要解析的地址
                    url_box.send_keys(url)
                    # 点击解析
                    click_button = self.broser.find_element_by_css_selector('[class="nya-btn"]')
                    click_button.click()

                    # 判断是否获取成功
                    exists = self.is_visible('//*[@id="__layout"]/div/main/div[2]/section[2]/h2/span')
                    if exists is True:
                        url = self.broser.find_element_by_xpath(
                            '//*[@id="__layout"]/div/main/div[2]/section[2]/div/p/a').get_attribute('href')
                        # Iduoliao.upload(url, 'http://manhua1032-61-174-50-98.cdndm5.com/11/10684/828113/33_8951.jpg?cid=828113&key=8addd8bd728b431096199d304202e18c&uk=', 'xiguashipin2', '西瓜视频')
                        url_box.clear()
                self.broser.quit()

        except Exception as f:
            print(f)
            # self.broser.quit()


if __name__ == '__main__':
    # url = input('爬取的项目url：')
    projetclist = [
        'https://github.com/icindy/wxParse/stargazers'
    ]
    for project in projetclist:
        obj = GithubStart()
        obj.run()