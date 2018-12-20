# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from NewCGSpider.items import NewcgspiderItem

class NewcgSpider(scrapy.Spider):
    name = 'newcg'
    allowed_domains = ['newcger.com/']
    # start_urls = ['http://newcger.com/aemoban//']
    start_urls = ['https://www.newcger.com/aemoban/']
    def parse(self, response):
        list_urls_xpath = '//ul[@id="list_soft"]/li/div[@class="thumb"]/a/@href | //ul[@id="list_soft"]/li/div[@class="thumb"]/a/img/@src'
        list_urls = response.xpath(list_urls_xpath).extract()
        for n in range(1,13):
            url = list_urls[(n-1)*2]
            post_img = list_urls[2*n-1]
            url = parse.urljoin(response.url,url)
            post_img = parse.urljoin(response.url, post_img)


            yield Request(url=url, meta={'post_image_url':post_img}, callback=self.parse_detail,dont_filter=True)

        next_url = response.xpath('//div[@class="joggerA"]/a[last()]/@href').extract()[0]
        if next_url:
            next = parse.urljoin(response.url, next_url)
            print(next)
            yield Request(url=next, callback=self.parse,dont_filter=True)

    @staticmethod
    def parse_detail(response):
        Newcg_item = NewcgspiderItem()
        img_xpath = '//p[@style="text-align: center;"]/img/@src'
        tital_xpath = '//div[@class="ramp2 "]/h2/text()'
        time_xpath = '//time/text()'
        detail_img = parse.urljoin(response.url,response.xpath(img_xpath).extract()[0])
        post_img = response.meta.get('post_image_url','')
        Newcg_item['img'] = [detail_img]
        Newcg_item['tital'] = response.xpath(tital_xpath).extract()[0]
        Newcg_item['time'] = response.xpath(time_xpath).extract()[0].strip().replace('发表时间：', '')


        yield Newcg_item