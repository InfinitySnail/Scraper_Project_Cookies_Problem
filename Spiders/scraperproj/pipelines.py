import logging
import math
from datetime import datetime
from decimal import Decimal
from dateutil.parser import parse
from scrapy.exceptions import DropItem

from .database import Auction, Event, BidHistory, Zip


# Helpers
def _parse_date(date):
    if not date:
        logging.warning('Missing date.')
        return

    if 'Eastern Time' in date:
        #date = date.replace('Eastern Time', 'EST')
        date = date.replace('Eastern Time', '')

    try:
        return parse(date)
    except ValueError:
        logging.error('Failed to parse date: %s' % date)


def _parse_price(price):
    if not price:
        logging.warning('Missing price.')
        return None

    try:
        return Decimal(price.replace('$', '').replace(',', ''))
    except SyntaxError:
        logging.error('Invalid price %s' % price)

    return None


# Pipelines
class AuctionPipeline(object):
    def process_item(self, item, spider):
        if 'AuctionPipeline' not in getattr(spider, 'pipelines', tuple()):
            return item

        # Clean ids
        item['internal_id'] = long(item['internal_id'])
        item['event_id'] = long(item['event_id'])
        item['lot_id'] = long(item['lot_id'])

        # Clean dates
        item['start_date'] = _parse_date(item['start_date'])
        item['end_date'] = _parse_date(item['end_date'])

        # Clean prices
        item['start_price'] = _parse_price(item['start_price'])
        item['current_price'] = _parse_price(item['current_price'])

        # Premium
        item['buyers_premium'] = Decimal(item['buyers_premium'])

        # Urls
        item['ask_question_url'] = 'AuctionSiteURL1.com/auction/gl_qna?cmd=ask&auctionId=%s' % item['internal_id']

        # Figure out weight and caliber
        item = self._figure_caliber(item)

        return item

    def _figure_caliber(self, item):
        description = item['description'].lower()

        calibers = set()

        for name in ['5.56', '7.62']:
            if name in description:
                calibers.add(name)
                break

        for name in ['mm', 'cal', 'brass']:
            matches = self._find_numbers(description, name)
            if matches:
                for m in matches:
                    calibers.add(m)

        item['shell_caliber'] = ', '.join(calibers)

        weight = self._find_numbers(description, 'lbs')

        if weight:
            item['shell_weight'] = weight.pop()
        else:
            item['shell_weight'] = None

        return item

    def _find_numbers(self, description, name):
        idx = 0

        results = set()

        while idx != -1:
            idx = description.find(name, idx)

            if idx != -1:
                pos = idx - 1

                while pos > 0 and description[pos].isspace():
                    pos -= 1

                word_end = pos + 1

                while pos > 0 and (description[pos].isdigit() or description[pos] in (',', '.')):
                    pos -= 1

                if pos < word_end:
                    if not description[pos].isdigit():
                        pos += 1

                    word = description[pos:word_end].replace(',', '').strip()

                    if word and word != '.':
                        results.add(word)

                idx += len(name)

        return results


class AuctionDatabasePipeline(object):
    def process_item(self, item, spider):
        if 'AuctionPipeline' not in getattr(spider, 'pipelines', tuple()):
            return item

        if not item['internal_id']:
            raise DropItem('Invalid item')

        session = spider.crawler.db_session

        model = session.query(Auction).filter_by(internal_id=item['internal_id']).first()
        if not model:
            model = Auction()
            session.add(model)

        if model.zip != item['zip'] or not model.distance:
            from_zip = spider.crawler.settings.get('FROM_ZIP', '65804')
            item['distance'] = self._calculate_distance(session, from_zip, item['zip']) * 2

        for k, v in item.iteritems():
            setattr(model, k, v)

        model.last_update = datetime.now()

        try:
            session.commit()
        except:
            session.rollback()
            raise

        return item

    def _calculate_distance(self, session, from_zip, to_zip):
        from_code = session.query(Zip).filter_by(code=from_zip).first()

        to_code = session.query(Zip).filter_by(code=to_zip).first()
        if not to_code:
            if '-' in to_zip:
                parts = to_zip.split('-')
                to_code = session.query(Zip).filter_by(code=parts[0]).first()

        if not from_code or not to_code:
            return 0

        return self.calc_distance(from_code.lat, from_code.lon,
                                  to_code.lat, to_code.lon) * 0.62137

    def calc_distance(self, lat1, lon1, lat2, lon2):
        RADIUS = 6371.0

        lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (math.sin(dlat / 2) ** 2 +
             math.sin(dlon / 2) ** 2 *
             math.cos(lat1) * math.cos(lat2))
        c = 2 * math.asin(math.sqrt(a))
        d = RADIUS * c

        return d


# Events
class EventDatabasePipeline(object):
    def process_item(self, item, spider):
        if 'EventPipeline' not in getattr(spider, 'pipelines', tuple()):
            return item

        if not item['event_id']:
            raise DropItem('Invalid item')

        item['bidding_opens'] = _parse_date(item['bidding_opens'])
        item['bidding_closes'] = _parse_date(item['bidding_closes'])
        item['award_date'] = _parse_date(item['award_date'])

        session = spider.crawler.db_session

        model = session.query(Event).filter_by(event_id=item['event_id']).first()
        if not model:
            model = Event()
            session.add(model)

        for k, v in item.iteritems():
            setattr(model, k, v)

        model.last_update = datetime.now()

        try:
            session.commit()
        except:
            session.rollback()
            raise

        return item


# Bid history
class BidHistoryDatabasePipeline(object):
    def process_item(self, item, spider):
        if 'BidHistoryPipeline' not in getattr(spider, 'pipelines', tuple()):
            return item

        if not item['event_id']:
            raise DropItem('Invalid item')

        # Clear data
        item['internal_id'] = long(item['internal_id'])
        item['event_id'] = long(item['event_id'])
        item['lot_id'] = long(item['lot_id'])

        item['amount'] = _parse_price(item['amount'])
        item['number'] = int(item['number'].replace('.', ''))

        date = item['date'].replace(u'\xa0/', u'/').replace(u'\xa0', ' ').replace('/ ', '/')
        date = date[:date.rfind(' ')]

        try:
            item['date'] = datetime.strptime(date, '%m/%d/%Y %I:%M %p')
        except ValueError:
            item['date'] = _parse_date(date)

        # Save in DB
        session = spider.crawler.db_session

        model = (session.query(BidHistory)
                 .filter_by(internal_id=item['internal_id'])
                 .filter_by(amount=item['amount'])
                 .first())

        if not model:
            model = BidHistory()
            session.add(model)

        for k, v in item.iteritems():
            setattr(model, k, v)

        model.last_update = datetime.now()

        try:
            session.commit()
        except:
            session.rollback()
            raise

        return item
