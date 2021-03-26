import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import HOpeItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class HOpeSpider(scrapy.Spider):
	name = 'hope'
	start_urls = ['https://www.bankofhope.com/hope-stories']

	def parse(self, response):
		post_links = response.xpath('//div[@class="text-right p-3 pt-0"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//span[@class="d-inline"]/span[2]/span/text()').get()
		try:
			title = response.xpath('//div[@class="row inner-block"]/p/strong/text() | //span[contains(@class,"NormalTextRun")]//text()').get().strip()
		except AttributeError:
			title = ''.join(response.xpath('//div[@class="row inner-block"]//text()').getall())
		content = response.xpath('//div[@class="default-text"]//text()[not (ancestor::script or ancestor::div[@class="default-text"]/span[@style="font-size: 12px; color: #333333;"] or ancestor::div[@class="social-sharing section-spacing heading-spacing"] or ancestor::div[@class="modal fade"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=HOpeItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
