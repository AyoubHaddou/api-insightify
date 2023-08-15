from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from dotenv import load_dotenv
import os 
from bs4 import BeautifulSoup  
load_dotenv()

class TrustpilotreviewsSpider(CrawlSpider):
    name = 'trustpilotreviews'
    tenant_url = os.getenv('TENANT_URL')
    allowed_domains = ['trustpilot.com']
    start_urls = [f'https://www.trustpilot.com/review/{tenant_url}']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='section[class="styles_reviewsContainer__3_GQw"]'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=rf'review/{tenant_url}'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=rf'review/{tenant_url}\?languages=all&page=\d+'), callback='parse_item', follow=True),
    )
    
    def parse_item(self, response):
        item = {}
        item['title'] = response.xpath('*//div[@class="styles_reviewContent__0Q2Tg"]/a/h2/text()').getall()
        item['review_rating'] = response.xpath('*//div[@class="styles_reviewHeader__iU9Px"]/div[@class="star-rating_starRating__4rrcf star-rating_medium__iN6Ty"]/img/@src').getall()
        comment_paragraphs = response.xpath('//div[@class="styles_reviewContent__0Q2Tg"]/p[1]')
        
        item['comment'] = []
        for p in comment_paragraphs:
            soup = BeautifulSoup(p.extract(), 'html.parser')  
            cleaned_text = soup.get_text(" ", strip=True)  # texte nettoyé avec des espaces entre les balises
            item['comment'].append(cleaned_text)

        item['date'] = response.xpath('*//div[@class="styles_reviewHeader__iU9Px"]/div[@class="typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_datesWrapper__RCEKH"]//time/@datetime').getall()
        return item