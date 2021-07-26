# BitcoinAbuse Crawler
A basic scrapper made in python with [scrapy framework](https://scrapy.org/) to -
* Scrape reports from bitcoinabuse.com.
* Push the output to ElasticSearch.

At the moment crawler only outputs to the ElasticSearch.
### Kubernetese Deployment
***Prerequisites***
1. ElasticSearch cluster

***Install BitcoinAbuse Crawler***

Install bitcoinabuse crawler with the release name ```bitcoinabuse-crawler```
```sh
helm install bitcoinabuse-crawler https://toshi-qcri.github.io/helm-charts-test/bitcoinabuse-crawler-0.0.0.tgz
```
### Output Format

Bitcoinabuse crawler outputs crawled reports to the elasticsearch in following format
```
{
"timestamp": "timestamp",
"type": "service",
"source": "bitcoinabuse",
"info": {
  "domain": "domain",
  "url": "crawled_url",
  "title": "title",
  "external_links: {
    "href_urls": {
        "web": "[www_urls]",
        "onion": "[onion_urls]"
    }
  },
  "tags": {
    "cryptocurrency": {
      "address": {
        "btc": "[btc_addrs]"
      }
    },
    "abuse": {
      "address": address,
      "report": {
        "timestamp": timestamp,
        "type": ransomware | blackmail scam | sextortion | darknet market | bitcoin tumbler | other,
        "abuser": abuser_data,
        "description": description
      }
    }
  },
  "raw_data": ""
}
```