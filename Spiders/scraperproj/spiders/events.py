from __future__ import absolute_import

from urllib.parse import urlparse, parse_qs

from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spiders import Spider
from scraperproj.items import EventItem

from .. import base, database


class EventsSpider(base.LoginMixin, Spider):
    pipelines = ['EventPipeline']

    name = 'events'

    def after_login(self):
        session = self.crawler.db_session

        # Find missed events
        subq = (session.query(database.Event.event_id)
                .subquery())

        query = (session.query(database.Auction.event_id)
                 .filter(~database.Auction.event_id.in_(subq)))

        for event in query:
            url = 'AuctionSiteURL1.com/auction/search?cmd=event_tab&event_id=%s' % event.event_id

            return Request(url,
                           callback=self.parse_event)

    def parse_event(self, response):
        hxs = HtmlXPathSelector(response)

        item = EventItem()

        url = urlparse(response.url)
        qs = parse_qs(url.query)

        item['event_id'] = qs['event_id'][0]

        item['description'] = self._clean_field(self._grab_field(hxs, 'Description :'))
        item['bidding_opens'] = self._grab_field(hxs, 'Bidding Opens :')
        item['bidding_closes'] = self._grab_field(hxs, 'Bid Close Date :')

        item['award_date'] = self._grab_field(hxs, 'Award Date :')

        item['preview_date'] = self._grab_field(hxs, 'Preview Date :')
        item['preview_time'] = self._grab_field(hxs, 'Preview Time :')

        item['bid_due_date'] = self._grab_field(hxs, 'Bid Due Date :')

        item['removal_date'] = self._grab_field(hxs, 'Removal Date :')
        item['removal_time'] = self._grab_field(hxs, 'Removal Time :')

        item['pay_in_full'] = self._grab_field(hxs, 'Pay In Full :')

        contact = hxs.select('//td[text()="Contact :"]/../td[2]')
        if contact:
            item['contact_phone'] = ''.join(contact.select('p/text()').extract())
            item['contact_email'] = ''.join(contact.select('a/text()').extract())

        return item

    def _grab_field(self, hxs, name):
        return ''.join(hxs.select('//td[text()="%s"]/../td[2]//text()' % (name)).extract())
