from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from .. import base


class AuctionFileSpider(base.BaseAuctionSpider):
    name = 'auctionfile'

    def after_login(self):
        events = file('auction_list.txt').readlines()

        for event_url in events:
            url = event_url.strip()

            if not url or url.startswith('#'):
                continue

            yield Request(url,
                          callback=self.parse_auction)
