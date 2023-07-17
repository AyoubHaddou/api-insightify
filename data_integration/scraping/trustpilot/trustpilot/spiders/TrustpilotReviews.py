from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from dotenv import load_dotenv
import os 
load_dotenv()

class TrustpilotreviewsSpider(CrawlSpider):
    name = 'trustpilotreviews'
    tenant_url = os.getenv('TENANT_URL')
    allowed_domains = ['trustpilot.com']
    start_urls = [f'https://www.trustpilot.com/review/{tenant_url}?languages=all']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='section[class="styles_reviewsContainer__3_GQw"]'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=rf'review/{tenant_url}\?languages=all&page=\d+'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = {}
        ratings = response.xpath('*//div[@class="star-rating_starRating__4rrcf star-rating_medium__iN6Ty"]/img/@src').getall()
        review_rating = ratings[1:]
        item['review_rating'] = review_rating
        item['title'] = response.xpath('*//div[@class="styles_reviewContent__0Q2Tg"]/a/h2/text()').extract()
        item['comment'] = response.xpath('*//div[@class="styles_reviewContent__0Q2Tg"]/p[1]/text()').extract()
        item['date'] = response.xpath('*//div[@class="typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_datesWrapper__RCEKH"]//time/@datetime').extract()
        return item

