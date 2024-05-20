# Scrapy settings for ics_v1 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ics_v1'

SPIDER_MODULES = ['ics_v1.spiders']
NEWSPIDER_MODULE = 'ics_v1.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
USER_AGENT = "ics_v1 (+http://www.yourdomain.com)"
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 30
# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

DEFAULT_REQUEST_HEADERS = {
    'authority': 'www.te.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # 'cookie': 'site_info=usa|en; country_info=usa; language_id=1; geo_info=usa; _gcl_au=1.1.1716822395.1691753305; TECewt5=071a634d-0fbe-4ef5-96b5-73774081fc0f; TECewt7=7165622e-5a86-4fe8-b62f-35da6b82acee; s_ecid=MCMID%7C32597957907158501452984182049878406413; aam_uuid=28647652233262713252564058957898760177; _rdt_uuid=1691753314602.02c0ba5d-cea9-4c13-87e6-5f5fd798adfb; _fbp=fb.1.1691753317484.1211673976; QSI_SI_5uIX2NZ1U3nltKB_intercept=true; _gid=GA1.2.1378982765.1691987600; TECmp1=Metric; cdn_geo_info=SG; ak_bmsc=63C522BF8F96668DCFE58392F01FF177~000000000000000000000000000000~YAAQHLQRYKrMpfuJAQAAhXW0/BR5H1DZV9f5g3S7FwyyuZRkTIPXyFMMvGXqkunNVUjawEOSTYblp1sR3ozTYwEPV22D+aB90Siyr1o/LJrKUAiuGmR00LVbXs+6HyD0orw9/yf0JtGcisLdXvODmnVYZO/jxyBUgiQqqN2xMwu6QRA/Y9TnrCNqfryO4FhltRpr0jUB5XtWWW+53PAEwlGES93NrH5jywrBJ+LlRgjDRr0W3P5XqKqnO5NZxPEYWiJ8gigqcASOTJC0qBZyJH6sQkZw1l5i++/Ei+HgVh8a/zglu2GIYKAJ2Af8+1zH0CIOXRSrHWYTdRcqDiHqWHzFzyv9l/fFZnMak2epzxy2I/XHCVuuiFuYHmzFe0I9ZVi0yA==; PIM-SESSION-ID=C7tXL6Ohp8HDHlOO; rxVisitor=1692161833516ABKAL6M225MGP0DQ7600EJ4GRKCIGKR5; akacd_PIM-prd_ah_rollout=3869614634~rv=97~id=862e5a231f0e7791e5bac0ba2389a219; dtCookie=v_4_srv_1_sn_4FKM0D97ILPGQQR4I5L0BOTIJK3S6FMN_perc_100000_ol_0_mul_1_app-3A619a1bcb124cd83e_1; SSO=guestusr@te.com; SMIDENTITY=UK378yvRN7WvUYeyAjGZx3Zyz309osFtTD0ggmwhWqbxG9xLUdLXuRy9PLPCzMf45RQHXpg3E0uSvVpUZ6sCfwAvs0Xm4KieRLz9Af80UDoLeIYE2dtgo9tjE/zDYVlCByp4kWSd96mtvj/XBr6tlSCH7qUS2N8IDogT2Vke09vUxsN6zq2stkGhbKMVq9YH6X13USfZ+WUN5F/quEkkn9nMHagWSwbyS8GZQrfQhu8Hdz/nZ09HQ8LAC9nuwr97/ko3gmdsuGtPvMGPif2/g1WZHjw+Ems2VjdOxSUUq4lq/41fsLS4xQB9EiaDfJeuSRNM3VzXIVd77xhcJuCUjSMKj0X0X8dGwbvQELGmFi1KE7eC7ajbK/SvO/RrdP8w/1wLATNBlxOTso1EbWYX/av1cjr22dgLOkoEnCM53eWYzJgkpGAapSlZdYTJMYaj89SgLULP+ghyEnujhGI0rilNVdB5NA4SDmX7Alt7oTgZXRgIp5jtv0yKqD3TROwClbKxajgLz7KMeR7i3fdNBP90WgTJpS/yBfKSb2LTB4m9GrGQvJ0Hx8D9WgDLFIOM; AMCVS_A638776A5245AFE50A490D44%40AdobeOrg=1; AMCV_A638776A5245AFE50A490D44%40AdobeOrg=-432600572%7CMCIDTS%7C19586%7CMCMID%7C32597957907158501452984182049878406413%7CMCAAMLH-1692766637%7C7%7CMCAAMB-1692766637%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1692169037s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.5.2; s_cc=true; AKA_A2=A; dtSa=-; RT="z=1&dm=te.com&si=ojwksf83ens&ss=llcd6zyk&sl=0&tt=0"; IR_gbd=te.com; IR_10771=1692162351316%7C2083231%7C1692162351316%7C%7C; IR_PI=53daa2e0-383a-11ee-8711-9fd0416cd8ce%7C1692248751316; _dtm_v1=1692162352117%2C1692108440991%2C1692108186622%2C209; _ga_7XPK4TC9TD=GS1.1.1692161838.14.1.1692162354.60.0.0; _ga=GA1.1.1511634918.1691753305; _dtm_v=1692162376527%2C1692161838623%2C1692108446958%2C11; rxvt=1692164238126|1692161833518; s_tp=4327; s_ppv=store%253Aview%2520all%2520te%2520store%2520products%2C36%2C34%2C1547; dtPC=1$162351058_479h-vIQLJPALHDHREHSHMHKIAKUMHSNTPKDUJ-0e0; bm_sv=C5CBD9ADB297FED581488589D4E0D828~YAAQHLQRYHKep/uJAQAARBS+/BTGalfFF2h1GfmUT7jAVKIt+YRh05s/OZVbHWKjbo//MNvofoRdANP6D+0SMDORsKZSEbHYS+9zNgfLhKLYRmMSibBdM5ajcPVK55J68xuBJnR/0MLEy5mvVmynpefQ+3peJiwJXCJClJ344jGpg+owfwIzVpnoaiBGL0P5VBiG2zfYW1k7kUpteaaD3dt6SW+yMmS6FNEMZ5NEoxUB4r3BdmOPVle/9tsc~1',
    # 'if-modified-since': 'Tue, 15 Aug 2023 15:16:46 GMT',
    # 'if-none-match': '"37fbf-602f7aae93446:dtagent10269230615181503p0/K"',
    # 'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    # 'sec-ch-ua-mobile': '?0',
    # 'sec-ch-ua-platform': '"Windows"',
    # 'sec-fetch-dest': 'document',
    # 'sec-fetch-mode': 'navigate',
    # 'sec-fetch-site': 'none',
    # 'sec-fetch-user': '?1',
    # 'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'ics_v1.middlewares.IcsV1SpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#     'ics_v1.middlewares.IcsV1DownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'ics_v1.pipelines.IcsV1Pipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings

###eadting

# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
RETRY_ENABLED = False
DOWNLOAD_MAXSIZE = 0
DOWNLOAD_TIMEOUT = 600

#edting
# RETRY_HTTP_CODE = [500, 502, 503, 504, 400, 408]
