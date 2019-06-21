import hashlib
import json
import re
import sys

import requests
import schedule
from selenium import webdriver
from VideoSpider.API.iduoliao import Iduoliao
from VideoSpider.API.iduoliaotool import Print
from VideoSpider.settings import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.ui as ui


def xg_video():

    item = {}
    isotimeformat = '%Y-%m-%d'
    opt = webdriver.ChromeOptions()
    # 加入请求头
    opt.add_argument('user-agent="{}"'.format(choice(User_Agent_list)))
    opt.add_argument('--disable-dev-shm-usage')
    # 不加载图片
    opt.add_argument('--no-sandbox')
    # 添加代理
    # opt.add_argument("--proxy-server={}".format(proxies))

    # 无头模式
    # opt.add_argument('--headless')

    # display = Display(visible=0, size=(800, 600))
    # display.start()

    broser = webdriver.Chrome(options=opt)
    wait = WebDriverWait(broser, 20, 0.5)
    login_url = 'https://miku.tools/tools/toutiao_video_downloader'
    # 登陆获取链接的网站
    broser.get(login_url)
    # 判断弹窗是否存在
    try:
        ui.WebDriverWait(broser, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[1]/div/div[2]/div[2]/button')))
        broser.find_element_by_xpath('//*[@id="__layout"]/div/div[1]/div/div[2]/div[2]/button').click()

    except:
        pass

    url_box = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//input[@placeholder="http://www.365yg.com/a6660790867638373640"]')))

    # 获取代理
    proxy_url = 'http://http.tiqu.alicdns.com/getip3?num=1&type=2&pro=0&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
    proxy = requests.get(proxy_url)
    proxy = json.loads(proxy.text)['data'][0]
    https_proxies = {
        'https': 'https://{0}:{1}'.format(proxy['ip'], proxy['port'])
    }
    proxies = https_proxies['https']

    for video_url, video_type in xg_spider_dict.items():
        item['view_cnt_compare'] = video_type[1]
        item['cmt_cnt_compare'] = video_type[2]
        item['category'] = video_type[0]
        item['old_type'] = video_type[4]

        json_data = json.loads(requests.get(video_url, headers=video_type[3], proxies=https_proxies).text)
        video_info = json_data['data']
        try:
            for video in video_info[2:]:
                    video = json.loads(video['content'])
                    item['id'] = video['group_id']
                    url = video['display_url']
                    item['download_url'] = video['display_url']
                    item['like_cnt'] = video['video_like_count']
                    item['cmt_cnt'] = video['comment_count']
                    item['sha_cnt'] = video['share_count']
                    item['view_cnt'] = video['video_detail_info']['video_watch_count']
                    item['thumbnails'] = video['large_image_list'][0]['url']
                    item['title'] = video['title']
                    item['video_height'] = json.loads(video['video_play_info'])['video_list']['video_1']['vheight']
                    item['video_width'] = json.loads(video['video_play_info'])['video_list']['video_1']['vwidth']
                    item['spider_time'] = time.strftime(isotimeformat, time.localtime(time.time()))
                    item['from'] = '西瓜视频'
                    item['category'] = item['category']
                    rep = re.search(r'http://toutiao.com/group/(.*)/', url).group(1)
                    item['url'] = 'https://www.ixigua.com/i' + rep + '/'

                    md = hashlib.md5()  # 构造一个md5
                    md.update(str(item['url']).encode())
                    item['osskey'] = md.hexdigest()

                    if item['view_cnt'] >= item['view_cnt_compare'] or item['cmt_cnt'] >= item['cmt_cnt_compare']:
                        is_ture = Iduoliao.redis_check(item['osskey'])
                        if is_ture is True:
                            # 输入要解析的地址
                            url_box.send_keys(item['url'])
                            # 点击解析
                            click_button = broser.find_element_by_css_selector('[class="nya-btn"]')
                            click_button.click()

                            # 判断是否出现解析失败
                            try:
                                ui.WebDriverWait(broser, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div[1]/div/div[2]/div[2]/button')))
                                click_button = broser.find_element_by_css_selector('[class="vue-dialog-button"]')
                                click_button.click()
                                url_box.clear()
                            except:
                                pass

                            # 判断是否获取成功
                            try:
                                ui.WebDriverWait(broser, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__layout"]/div/main/div[3]/fieldset[2]/legend/span')))
                            except:
                                pass
                            url = broser.find_element_by_xpath(
                                '//*[@id="__layout"]/div/main/div[3]/fieldset[2]/div/p/a').get_attribute('href')

                            # 开始去水印上传
                            Iduoliao.upload(url, item['thumbnails'], item['osskey'], '西瓜视频', item['title'], item['old_type'])
                            url_box.clear()
            broser.quit()

        except Exception as f:
            Print.error(f)
            print('错误所在的行号：', f.__traceback__.tb_lineno)
            # 判断是否出现解析失败1
            try:
                ui.WebDriverWait(broser, 10).until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[2]/div[1]/div[2]')))
                click_button = broser.find_element_by_css_selector('[class="vue-dialog-button"]')
                click_button.click()
                url_box.clear()
            except:
                sys.exit()


schedule.every(10).minutes.do(xg_video)

while True:
    schedule.run_pending()