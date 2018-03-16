from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from .. import base


class WatchlistSpider(base.BaseAuctionSpider):
    name = 'watchlist'

    def after_login(self):
        return Request('AuctionSiteURL1.com/account/main?tab=WatchList&perPage=200',
                       callback=self.parse_watchlist)

    def parse_watchlist(self, response):
        hxs = HtmlXPathSelector(response)

        base_url = get_base_url(response)

        item_urls = hxs.select('//tr[@class="auction"]//div[@class="tiny-thumbnail"]/a/@href').extract()

        for url in item_urls:
            yield Request(urljoin_rfc(base_url, url),
                          method='GET',
                          callback=self.parse_auction)

        #from scrapy.shell import inspect_response
        #inspect_response(response)

        next_page = hxs.select('//a[text()="Next Page >>"]/@href').extract()
        if next_page:
            yield Request(urljoin_rfc(base_url, next_page[0]),
                          method='GET',
                          callback=self.parse_watchlist)
