import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Initialization
engine = sa.create_engine('sqlite:///output/data.sqlite', echo=False)
BaseModel = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))


# Models
class Event(BaseModel):
    __tablename__ = 'events'

    id = sa.Column(sa.Integer, primary_key=True)

    last_update = sa.Column(sa.DateTime)

    event_id = sa.Column(sa.BigInteger)

    description = sa.Column(sa.UnicodeText)

    bidding_opens = sa.Column(sa.DateTime)
    bidding_closes = sa.Column(sa.DateTime)

    award_date = sa.Column(sa.DateTime)

    preview_date = sa.Column(sa.Unicode(64))
    preview_time = sa.Column(sa.Unicode(64))

    bid_due_date = sa.Column(sa.Unicode(64))
    removal_date = sa.Column(sa.Unicode(64))
    removal_time = sa.Column(sa.Unicode(64))
    pay_in_full = sa.Column(sa.Unicode(128))

    contact_phone = sa.Column(sa.Unicode(64))
    contact_email = sa.Column(sa.Unicode(64))


class Auction(BaseModel):
    __tablename__ = 'auctions'

    id = sa.Column(sa.Integer, primary_key=True)

    last_update = sa.Column(sa.DateTime)

    internal_id = sa.Column(sa.BigInteger, index=True)
    event_id = sa.Column(sa.BigInteger)
    lot_id = sa.Column(sa.BigInteger)

    description = sa.Column(sa.UnicodeText())

    start_date = sa.Column(sa.DateTime)
    end_date = sa.Column(sa.DateTime)

    start_price = sa.Column(sa.Float(as_decimal=True))
    current_price = sa.Column(sa.Float(as_decimal=True))

    # Additional info
    buyers_premium = sa.Column(sa.Float(as_decimal=True))

    # Payment
    payment_info = sa.Column(sa.UnicodeText)

    # Contact
    address = sa.Column(sa.Unicode(256))
    city = sa.Column(sa.Unicode(64))
    state = sa.Column(sa.Unicode(8))
    zip = sa.Column(sa.Unicode(16))

    country = sa.Column(sa.Unicode(32))

    contact_phone = sa.Column(sa.Unicode(32))
    contact_fax = sa.Column(sa.Unicode(32))

    facility_manager = sa.Column(sa.Unicode(64))
    facility_email = sa.Column(sa.Unicode(64))

    # Shipping
    lot_weight = sa.Column(sa.Unicode(64))
    weight_uom = sa.Column(sa.Unicode(64))
    shipping_qty = sa.Column(sa.Unicode(64))
    approx_dim = sa.Column(sa.Unicode(64))

    # Preview
    preview_arrangements = sa.Column(sa.UnicodeText)
    loadout_procedures = sa.Column(sa.UnicodeText)
    security_procedures = sa.Column(sa.UnicodeText)

    # Calculated properties
    distance = sa.Column(sa.Float)
    shell_caliber = sa.Column(sa.UnicodeText())
    shell_weight = sa.Column(sa.Unicode(64))

    # URLs
    ask_question_url = sa.Column(sa.String(512))


class Zip(BaseModel):
    __tablename__ = 'zip_codes'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.Unicode(8))
    lat = sa.Column(sa.Float)
    lon = sa.Column(sa.Float)


class BidHistory(BaseModel):
    __tablename__ = 'bid_history'

    id = sa.Column(sa.Integer, primary_key=True)

    last_update = sa.Column(sa.DateTime)

    internal_id = sa.Column(sa.BigInteger, index=True)
    event_id = sa.Column(sa.BigInteger)
    lot_id = sa.Column(sa.BigInteger)

    number = sa.Column(sa.Integer)
    bidder = sa.Column(sa.Unicode(64))
    amount = sa.Column(sa.Float(as_decimal=True))
    status = sa.Column(sa.Unicode(64))
    date = sa.Column(sa.DateTime)
    bid_type = sa.Column(sa.Unicode(32))

    __table_args__ = (sa.Index('ix_bidhistory_quick_lookup', internal_id, amount), )


# Database object
class Database(object):
    def __init__(self, crawler):
        self.crawler = crawler
        crawler.db_session = Session()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


# Events
@sa.event.listens_for(Zip.__table__, 'after_create')
def _create_zip(target, conn, **kwargs):
    import csv

    with open('data/zip_code_database.csv', 'r') as fp:
        reader = csv.DictReader(fp)

        session = Session()

        for row in reader:
            session.add(Zip(code=row['zip'], lat=row['latitude'], lon=row['longitude']))

        session.commit()
        session.close()

# Create all
BaseModel.metadata.create_all(engine)
