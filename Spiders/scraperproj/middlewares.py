from scrapy.downloadermiddlewares.cookies import CookiesMiddleware


class CustomCookiesMiddleware(CookiesMiddleware):
    def process_request(self, request, spider):
        if 'force_cookiejar' in request.meta:
            cookiejarkey = request.meta.get("cookiejar")
            self.jars[cookiejarkey] = request.meta['force_cookiejar']

        return super(CustomCookiesMiddleware, self).process_request(request, spider)

    def process_response(self, request, response, spider):
        result = super(CustomCookiesMiddleware, self).process_response(request, response, spider)

        cookiejarkey = request.meta.get("cookiejar")
        response.cookies = self.jars[cookiejarkey]

        return result
