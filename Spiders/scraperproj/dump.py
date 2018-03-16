import csv

from .database import Session, Auction, Event, BidHistory


def _header(rules):
    result = []

    for name, _ in rules:
        result.append(name)

    return result


def _rules(item, rules):
    result = []

    for name, field in rules:
        if callable(field):
            result.append(field(item))
        else:
            result.append(getattr(item, field))

    return result


def dump_auctions(file_name):
    fields = [
        ('Event', 'event_id'),
        ('Lot', 'lot_id'),
        ('Link', lambda item: "AuctionSiteURL1.com/auction/view?auctionId=%s" % item.internal_id),
        ('Description', 'description'),
        ('Premium', 'buyers_premium'),
        ('Pounds', 'shell_weight'),
        ('Contents', 'shell_caliber'),
        ('Open Date', lambda item: item.start_date.strftime('%m/%d/%Y')),
        ('Open Time', lambda item: item.start_date.strftime('%H:%M')),
        ('Close Date', lambda item: item.end_date.strftime('%m/%d/%Y')),
        ('Close Time', lambda item: item.end_date.strftime('%H:%M')),
        ('Zip Code', 'zip'),
        ('City', 'city'),
        ('State', 'state'),
        ('Distance', 'distance')
    ]

    with open(file_name, 'wb') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_ALL)

        writer.writerow(_header(fields))

        session = Session()

        for item in session.query(Auction).order_by(Auction.event_id, Auction.lot_id):
            writer.writerow(_rules(item, fields))


def dump_events(file_name):
    fields = [
        ('Event', 'event_id'),
        ('Description', 'description'),
        ('Bidding Open', 'bidding_opens'),
        ('Bidding Closes', 'bidding_closes'),
        ('Award Date', 'award_date'),
        ('Preview Date', 'preview_date'),
        ('Preview Time', 'preview_time'),
        ('Bid Due', 'bid_due_date'),
        ('Removal Date', 'removal_date'),
        ('Removal Time', 'removal_time'),
        ('Pay in Full', 'pay_in_full'),
        ('Contact phone', 'contact_phone'),
        ('Contact email', 'contact_email'),
    ]

    with open(file_name, 'wb') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_ALL)

        writer.writerow(_header(fields))

        session = Session()

        for item in session.query(Event).order_by(Event.event_id):
            writer.writerow(_rules(item, fields))


def dump_bidhistory(file_name):
    fields = [
        ('Event', 'event_id'),
        ('Lot ID', 'lot_id'),
        ('Bid', 'number'),
        ('Bidder', 'bidder'),
        ('Amount', 'amount'),
        ('Status', 'status'),
        ('Bid Date', 'date'),
        ('Type', 'bid_type'),
    ]

    with open(file_name, 'wb') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_ALL)

        writer.writerow(_header(fields))

        session = Session()

        for item in session.query(BidHistory).order_by(BidHistory.event_id, BidHistory.lot_id, BidHistory.date.desc()):
            writer.writerow(_rules(item, fields))
