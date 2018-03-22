import couchdb
import scrapy
import sys
sys.path.append('..')
from scrapy.http import Request
from lxmlhtml import CustomLxmlLinkExtractor as LinkExtractor
import localsettings as settings

from items import RawResponseItem
from redis_spider import RedisSpider

class LinkSpider(RedisSpider):
    '''
    A spider that walks all links from the requested URL. This is
    the entrypoint for generic crawling.
    '''
    name = "link"
    def __init__(self, *args, **kwargs):
        super(LinkSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        self._logger.debug("crawled url {}".format(response.request.url))
        cur_depth = 0
        if 'curdepth' in response.meta:
            cur_depth = response.meta['curdepth']
        page = response.url.split("/")[-2]
        temp = response.url.split("//")[-1]
        filenam = '%s.html' % temp
        #storing the downloaded html document
        couch = couchdb.Server('http://localhost:5984')
        try:
            db = couch['crawler']
        except:
            db = couch.create('crawler')
        with open(filenam, 'wb') as f:
            f.write(response.url)
            f.write("\n")
            f.write(response.body)
        #print("response url ")
        #print(response.url)
        #print("response body")
        #print(response.body)
        #with open("temp.txt",'wb') as w:
        #    w.write(response.body)
        temp_doc = { 'name' : filenam }
        db.save(temp_doc)
        #writing which documents have already been stored
        with open("doc_updated.txt","a+")as x:
            x.write("%s saved \n" %filenam)
        #attaching the html files to the documents itself
        with open(filenam,"r+") as _file:
            name = filenam
            db.put_attachment(temp_doc,_file,filename = name,content_type='text/html')
        # capture raw response
        item = RawResponseItem()
        # populated from response.meta
        item['appid'] = response.meta['appid']
        item['crawlid'] = response.meta['crawlid']
        item['attrs'] = response.meta['attrs']

        # populated from raw HTTP response
        item["url"] = response.request.url
        item["response_url"] = response.url
        item["status_code"] = response.status
        item["status_msg"] = "OK"
        item["response_headers"] = self.reconstruct_headers(response)
        item["request_headers"] = response.request.headers
        item["body"] = response.body
        item["links"] = []

        # determine whether to continue spidering
        if cur_depth >= response.meta['maxdepth']:
            self._logger.debug("Not spidering links in '{}' because" \
                " cur_depth={} >= maxdepth={}".format(
                                                      response.url,
                                                      cur_depth,
                                                      response.meta['maxdepth']))
        else:
            # we are spidering -- yield Request for each discovered link
            link_extractor = LinkExtractor(
                            allow_domains=response.meta['allowed_domains'],
                            allow=response.meta['allow_regex'],
                            deny=response.meta['deny_regex'],
                            deny_extensions=response.meta['deny_extensions'])

            for link in link_extractor.extract_links(response):
                # link that was discovered
                the_url = link.url
                the_url = the_url.replace('\n', '')
                item["links"].append({"url": the_url, "text": link.text, })
                req = Request(the_url, callback=self.parse)

                req.meta['priority'] = response.meta['priority'] - 10
                req.meta['curdepth'] = response.meta['curdepth'] + 1

                if 'useragent' in response.meta and \
                        response.meta['useragent'] is not None:
                    req.headers['User-Agent'] = response.meta['useragent']

                self._logger.debug("Trying to follow link '{}'".format(req.url))
                yield req
                yield item
                                                           102,9         Bot

