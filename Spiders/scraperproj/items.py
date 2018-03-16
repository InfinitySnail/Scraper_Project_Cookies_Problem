from scrapy.item import Item, Field


class EventItem(Item):
    event_id = Field()

    description = Field()

    bidding_opens = Field()
    bidding_closes = Field()

    award_date = Field()

    preview_date = Field()
    preview_time = Field()

    bid_due_date = Field()
    removal_date = Field()
    removal_time = Field()
    pay_in_full = Field()

    contact_phone = Field()
    contact_email = Field()


class AuctionItem(Item):
    # General information
    internal_id = Field()
    event_id = Field()
    lot_id = Field()

    description = Field()

    start_date = Field()
    end_date = Field()

    start_price = Field()
    current_price = Field()

    # Additional info
    buyers_premium = Field()

    # Payment
    payment_info = Field()

    # Contact
    address = Field()
    city = Field()
    state = Field()
    zip = Field()

    country = Field()

    contact_phone = Field()
    contact_fax = Field()

    facility_manager = Field()
    facility_email = Field()

    # Shipping
    lot_weight = Field()
    weight_uom = Field()
    shipping_qty = Field()
    approx_dim = Field()

    # Preview
    preview_arrangements = Field()
    loadout_procedures = Field()
    security_procedures = Field()

    # Calculated properties
    distance = Field()
    shell_caliber = Field()
    shell_weight = Field()

    # Links
    ask_question_url = Field()


class BidHistoryItem(Item):
    internal_id = Field()
    event_id = Field()
    lot_id = Field()

    number = Field()
    bidder = Field()
    amount = Field()
    status = Field()
    date = Field()
    bid_type = Field()
