# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class PlantphotoPipeline(object):
    def process_item(self, item, spider):
        with open('1.txt','a+') as f:
            f.write(item.name)
        return item
