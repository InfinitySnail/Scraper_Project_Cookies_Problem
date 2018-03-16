from __future__ import absolute_import

import pickle
import logging
from urllib.parse import urlparse, parse_qs
from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.spiders import Spider
from scrapy.exceptions import CloseSpider
from scraperproj.items import AuctionItem

COOKIE_NAME = 'output/cookies.bin'


# Spiders
class LoginMixin(object):
    allowed_domains = ['AuctionSiteURL1.com', 'AuctionSiteURL2.com']

    def start_requests(self):
        yield self.begin_auth()

    def begin_auth(self):
        try:
            with open(COOKIE_NAME, 'rb') as fp:
                cookies = pickle.load(fp)
                return Request('AuctionSiteURL1.com/account/main',
                               meta=dict(force_cookiejar=cookies),
                               callback=self.check_home)
        except Exception as ex:
            logging.error('error %s' % ex)
            return self.login()

    def check_home(self, response):
        if response.url != 'AuctionSiteURL1.com/account/main':
            return self.login()

        return self.after_login()

    def login(self):
        formdata = {
            'callback_url': 'AuctionSiteURL1.com/login?page=/account/main',
            'page': '/account/main',
            'app_key': '2',
            'j_username': self.settings.get('USER_LOGIN'),
            'j_password': self.settings.get('USER_PASSWORD'),
            'submitLogin': 'Login'
        }

        return FormRequest('AuctionSiteURL2.com/unifieduser/j_spring_security_check',
                           method='POST',
                           formdata=formdata,
                           dont_filter=True,
                           callback=self.check_login)

    def check_login(self, response):
        if response.url != 'AuctionSiteURL1.com/account/main':
            raise CloseSpider('Login failed')

        with open(COOKIE_NAME, 'wb') as fp:
            pickle.dump(response.cookies, fp)

        return self.after_login()

    def after_login(self):
        pass

    def _clean_field(self, field):
        return field.strip().replace('\t\t', '').replace('\n\n', '').replace('  ', '').replace('\n\t\n\t', '\n')


class BaseAuctionSpider(LoginMixin, Spider):
    pipelines = ['AuctionPipeline']

    def parse_auction(self, response):
        hxs = HtmlXPathSelector(response)

        item = AuctionItem()

        # Get internal id
        url = urlparse(response.url)
        qs = parse_qs(url.query)

        if 'auctionId' in qs:
            item['internal_id'] = qs['auctionId'][0]
        elif 'id' in qs:
            item['internal_id'] = qs['id'][0]

        # Front page
        item['event_id'], item['lot_id'] = hxs.select('//div[@class="event-details"]//span/text()').extract()
        item['description'] = ''.join(hxs.select('//div[@id="auction_lotDetails"]/text()').extract()).strip()

        item['start_date'] = self._grab_info(hxs, 'Open Time:')
        item['end_date'] = self._grab_info(hxs, 'Close Time:')

        item['start_price'] = self._grab_info(hxs, 'Opening Bid:')
        item['current_price'] = self._grab_info(hxs, 'Current Bid:')

        # Premium
        val = hxs.re('A (\d+)% Buyer\'s Premium applies to this lot.')
        if val:
            item['buyers_premium'] = val[0]
        else:
            item['buyers_premium'] = '0'

        # Contact
        self._parse_address(hxs, item)
        item['country'] = self._grab_tab_field(hxs, 'auction_contact', 'Country of Origin:')

        item['contact_phone'] = self._grab_tab_field(hxs, 'auction_contact', 'Contact Phone:')
        item['contact_fax'] = self._grab_tab_field(hxs, 'auction_contact', 'Contact Fax:')

        item['facility_manager'] = self._grab_tab_field(hxs, 'auction_contact', 'Facility Manager:')
        item['facility_email'] = self._grab_tab_field(hxs, 'auction_contact', 'Facility EMail:')

        # Payment
        item['payment_info'] = self._clean_field(''.join(hxs.select('//div[@id="auction_payment"]//text()').extract()))

        # Shipping
        item['lot_weight'] = self._grab_tab_field(hxs, 'auction_shippingInfo', 'Approximate Lot Weight:')
        item['weight_uom'] = self._grab_tab_field(hxs, 'auction_shippingInfo', 'Weight UOM:')
        item['shipping_qty'] = self._grab_tab_field(hxs, 'auction_shippingInfo', 'Shipping QTY:')
        item['approx_dim'] = self._grab_tab_field(hxs, 'auction_shippingInfo', 'Approximate Dim. or Lot Cube:')

        # Preview dimensions
        item['preview_arrangements'] = self._grab_tab_field(hxs, 'auction_preview', 'Preview Arrangements:')
        item['loadout_procedures'] = self._grab_tab_field(hxs, 'auction_preview', 'Loadout Procedures:')
        item['security_procedures'] = self._grab_tab_field(hxs, 'auction_preview', 'Secuity Procedures:')

        return item

    def _parse_address(self, hxs, item):
        lines = [l.strip() for l in self._grab_tab_field_list(hxs, 'auction_contact', 'Item Location:') if l.strip()]

        if len(lines) > 2:
            item['address'] = '%s, %s' % (lines[0], lines[1])
        else:
            item['address'] = lines[0]

        city, part = lines[-1].split(',')
        item['city'] = city.strip()

        state, zip = part.strip().split(' ')
        item['state'] = state
        item['zip'] = zip

    def _grab_info(self, hxs, name):
        data = hxs.select('//td/h4[text()="%s"]/../../td[2]/text()' % name).extract()

        if data:
            return data[0].strip()

        return None

    def _grab_tab_field_list(self, hxs, tabid, name):
        return hxs.select('//div[@id="%s"]//td[text()="%s"]/../td[2]//text()' % (tabid, name)).extract()

    def _grab_tab_field(self, hxs, tabid, name):
        data = self._grab_tab_field_list(hxs, tabid, name)
        return ''.join(data).strip()
