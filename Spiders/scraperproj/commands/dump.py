from scrapy.command import ScrapyCommand


class Command(ScrapyCommand):
    def syntax(self):
        return ""

    def short_desc(self):
        return "Dump database as CSV file"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)

    def run(self, args, opts):
        from .. import dump
        dump.dump_auctions('output/auctions.csv')
        dump.dump_events('output/events.csv')
        dump.dump_bidhistory('output/bidhistory.csv')
