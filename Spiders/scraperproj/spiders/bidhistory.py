from __future__ import absolute_import
from urllib.parse import urlparse, parse_qs
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spiders import Spider
from scraperproj.items import BidHistoryItem
from scrapy.utils.url import urljoin_rfc
from scrapy.utils.response import get_base_url

from .. import base, database


class BidHistorySpider(base.LoginMixin, Spider):
    pipelines = ['BidHistoryPipeline']

    name = 'bidhistory'
    allowed_domains = ['AuctionSiteURL1', 'AuctionSiteURL2', 'localhost']

    def after_login(self):
        return Request('BidHistory URL',
                       callback=self.parse_history_list)

    def parse_history_list(self, response):
        hxs = HtmlXPathSelector(response)

        base_url = get_base_url(response)

        events = hxs.select('//tr/td[1][@class="titleSectionBackground1"]//a/@href').extract()

        for url in events:
            yield Request(urljoin_rfc(base_url, url),
                          method='GET',
                          callback=self.parse_event)

    def parse_event(self, response):
        hxs = HtmlXPathSelector(response)

        base_url = get_base_url(response)

        parsed = urlparse(response.url)
        qs = parse_qs(parsed.query)
        event_id = qs['eventId'][0]

        auctions = hxs.select('//tr/td[1]/a/font/b')

        for item in auctions:
            parsed = urlparse(item.select('../../@href').extract()[0])
            qs = parse_qs(parsed.query)
            auction_id = qs['auctionId'][0]

            # Fetch data
            yield Request(urljoin_rfc(base_url, '/auction/bidhistory?cmd=historyCurrent&auctionId=%s' % auction_id),
                          method='GET',
                          callback=self.parse_auction,
                          meta={
                            'auction_id': auction_id,
                            'event_id': event_id,
                            'lot_id': item.select('text()').extract()[0]
                          })

    def parse_auction(self, response):
        hxs = HtmlXPathSelector(response)

        base_url = get_base_url(response)

        rows = hxs.select('//tr/td[1][@align="center"]/font[@size="2"]/../..')
        for row in rows:
            item = BidHistoryItem()
            item['internal_id'] = response.meta['auction_id']
            item['event_id'] = response.meta['event_id']
            item['lot_id'] = response.meta['lot_id']

            item['number'] = self._get(row, 'td[1]//text()')
            item['bidder'] = self._get(row, 'td[2]//text()')
            item['amount'] = self._get(row, 'td[3]//text()')
            item['status'] = self._get(row, 'td[4]//text()')
            item['date'] = self._get(row, 'td[5]//text()')
            item['bid_type'] = self._get(row, 'td[6]//text()')
            yield item

        next_page = hxs.select('//a[text()="Next > >"]/@href').extract()
        if next_page:
            yield Request(urljoin_rfc(base_url, next_page[0]),
                          method='GET',
                          callback=self.parse_auction,
                          meta=response.meta)

    def _get(self, xhs, select):
        return ''.join(xhs.select(select).extract()).strip()
