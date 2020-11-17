# -*- coding: utf-8 -*-
import codecs
import json
import os
import random
import re
from urllib import parse

import chardet
import requests
import scrapy
from bs4 import BeautifulSoup
from lxml import etree

USER_AGENT_LIST=[
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]


def save_file(dir_path, zh_name, en_name,b):
    dir_files = os.listdir(dir_path)  # 得到该文件夹下所有的文件
    for file in dir_files:
        file_path = os.path.join(dir_path, file)  # 路径拼接成绝对路径
        file_name=zh_name+en_name
        if os.path.isdir(file_path) and file!=file_name:  # 如果目录，就递归子目录
            save_file(file_path,zh_name,en_name,b)
        elif os.path.isdir(file_path) and file==file_name:
            i=1
            p=os.path.join(file_path, '{}.jpeg'.format(i))
            while os.path.exists(p):
                i+=1
                p = os.path.join(file_path, '{}.jpeg'.format(i))
            with open(p,'wb') as f:
                f.write(b)


class GetImgSpider(scrapy.Spider):
    name = 'get_img'
    allowed_domains = ['http://ppbc.iplant.cn']
    start_urls = ['http://ppbc.iplant.cn/ashx/getphotopage.ashx']

    def start_requests(self):
        for i in range(1,30):
            yield scrapy.FormRequest(
                url=self.start_urls[0]+'?page={}&n=2&group=class'.format(i),
                callback=self.class_parse,
                dont_filter=True
            )
        # yield scrapy.FormRequest(
        #         url='http://ppbc.iplant.cn/tu/5044908',
        #         callback=self.name_parse,
        #         dont_filter=True
        #     )

    def class_parse(self, response):
        html_data=response.body.decode('utf-8')
        html=etree.HTML(html_data)
        class_id=html.xpath('//*[@class="spphotoimg"]/@classid')
        class_zh_name=html.xpath('//*[@class="mp10"]/div[1]/a/text()')
        class_en_name=html.xpath('//*[@class="mp10"]/div[2]/a/text()')
        fam_urls=html.xpath('//*[@class="spphotoimg"]/@href')
        for cid in class_id:
            for i in range(1,20):
                yield scrapy.FormRequest(
                    url=self.start_urls[0] +'?n={}&group=fam&cid={}&p=&m='.format(i,cid),
                    callback=self.fam_parse,
                    dont_filter=True
                )

    def fam_parse(self, response):
        html_data = response.body.decode('utf-8')
        html = etree.HTML(html_data)
        fam_id = html.xpath('//*[@class="spphotoimg"]/@classid')
        fam_zh_name = html.xpath('//*[@class="mp10"]/div[1]/a/text()')
        fam_en_name = html.xpath('//*[@class="mp10"]/div[2]/a/text()')
        fam_urls = html.xpath('//*[@class="spphotoimg"]/@href')
        for fid in fam_id:
            for i in range(1,20):
                yield scrapy.FormRequest(
                    url=self.start_urls[0] +'?n={}&group=gen&cid={}&p=&m='.format(i,fid),
                    callback=self.gen_parse,
                    dont_filter=True
                )

    def gen_parse(self, response):
        html_data = response.body.decode('utf-8')
        html = etree.HTML(html_data)
        gen_id = html.xpath('//*[@class="spphotoimg"]/@classid')
        print(gen_id)
        gen_zh_name = html.xpath('//*[@class="mp10"]/div[1]/a/text()')
        gen_en_name = html.xpath('//*[@class="mp10"]/div[2]/a/text()')
        gen_urls = html.xpath('//*[@class="spphotoimg"]/@href')
        for gid in gen_id:
            for i in range(1, 20):
                yield scrapy.FormRequest(
                    url=self.start_urls[0] + '?n={}&group=sp&cid={}&p=&m='.format(i, gid),
                    callback=self.sp_parse,
                    dont_filter=True
                )
    def sp_parse(self, response):
        html_data = parse.unquote(response.body.decode('utf-8'))
        html = etree.HTML(html_data)
        sp_id = html.xpath('//*[@class="img"]/@cno')
        sp_name = html.xpath('//*[@class="namew fl"]/a/text()')
        img_id = html.xpath('//*[@class="img"]/@pid')
        for sid in sp_id:
            yield scrapy.FormRequest(
                url='http://ppbc.iplant.cn/ashx/getotherinfo.ashx?spid={}&t=photosys'.format(sid),
                callback=self.path_parse,
                dont_filter=True
            )
        # for img in img_id:
        #     yield scrapy.FormRequest(
        #         url='http://ppbc.iplant.cn/tu/{}'.format(img),
        #         callback=self.name_parse,
        #         dont_filter=True
        #     )

    def path_parse(self, response):
        html_data = response.body.decode('utf-8')
        bs = BeautifulSoup(html_data, "html")
        path_list=bs.get_text().replace(' ','').split('>>')
        # 判断结果
        path='中国植物图鉴'
        for p in path_list:
            path+='/{}'.format(p)
        if not os.path.exists(path):
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)
        # item = PlantphotoItem()
        # item.name = bs.get_text()
        # yield item

    def name_parse(self, response):
        html_data = parse.unquote(response.body.decode('utf-8'))
        html = etree.HTML(html_data)
        name = html.xpath('//*[@id="img72"]/img/@alt')[0].replace(' ','')
        src=html.xpath('//*[@id="img72"]/img/@src')[0]
        sid=src.split('/')[-1].split('.')[0]
        headers = {
            'Referer': 'http://ppbc.iplant.cn/tu/{}'.format(sid),
            'User-Agent':'{}'.format(random.choice(USER_AGENT_LIST))
        }
        en_name = re.sub('[\u4E00-\u9FA5]', "", name)
        zh_name = re.sub("[A-Za-z0-9\!\%\[\]\,\。\ ]", "", name)
        req = requests.get('http://img1.iplant.cn/image2/b/{}.jpg'.format(sid),headers=headers)#发送请求
        dir_path = 'H:\Image_get\PlantPhoto\中国植物图鉴'
        save_file(dir_path,zh_name,en_name,req.content)

