# ElasticIntel

[![Build Status](https://travis-ci.org/securityclippy/elasticintel.svg?branch=master)](https://travis-ci.org/securityclippy/elasticintel)

Serverless, low cost, threat intel aggregation for enterprise or personal use, backed by ElasticSearch.  


### About

An alternative to expensive threat intel aggregation platforms which ingest the same data feeds you could get for free.

ElasticIntel is designed to provide a central, scalable and easily queryable repository for
threat intelligence of all types.

Utilizes amazon services to allow for minimal support needs while maintaining scalability and 
resilience and performance.  (aws lambda, elasticsearch, s3, sns)

### Getting started

See the [Getting started docs](docs/GettingStarted.md)

#### Disclaimer.

**Currently documentation for this project is lacking due to time constraints.  This is actively
being fixed and should be much more verbose in a few days.  Please check back
soon if you're not ready to jump in blind :)**


#### Features
* Serverless - No maintenance required
* Scalable (all services scale via AWS)
* High performance API - API can be used to run extremely high volume queries
* Flexible - Feeds can be added via simple json feed configuration
* Extensible - written in python and extended by new modules
* Cost-effective - Pay only for the backend services - don't worry about API limits
* Automated Deployment - platform can be deployed from a single command
* Works "out of the box" - comes pre-configured with 30+ opensource intel feeds


### Why ElasticIntel

ElasticIntel is the answer to a frustration which arose when evaluating various paid threat intel products and feeds.
After reviewing the data from several of these services, I found that 90% of the data they were returning was data
from publicly (and freely) available sources, simply aggregated into one place.

Even more frustrating, was the fact that nearly all of them wanted to charge insane amounts for API access to this ame data,
which was limited by volume and made it nearly impossible to query the data in any significant volume without
paying even more.

### Enrichment

* Whois enrichment
* < more to come >


## Architecture

1. Feed Scheduler lambda - The feed scheduler lambda runs once an hour, just like a cron job.  It downloads
the configurations for all feeds, checks their scheduled download times and puts a download job
into an sns queue a feed needs to be downloaded

2. Ingest Feed Lambda - The ingest lambda is triggered by messages arriving to an sns topic.  When a message arrives,
the ingest lamda reads the message, parses out the information about the intel feed and downloads the feed itself.  Once
downloaded, the ingest lambda stores a copy of the feed in s3 and then parses out the data in the feed.  Once
the data is parsed, the ingest lambda puts the data into the intel index in elasticsearch for easy querying.

* intel objects define in set of values (json)
* intel feed objects define the feed itself (url, type(xml, csv, json), schedule)
* intel feeds may be easily added simply by defining a new feed configuration in the feeds
directory.
* for API-based intel feeds, modules may be easily added in the form of python scripts and
imported into the main feed manager
###  feed ingestion is done via a series of lambdas
* Feed scheduler:
  * the scheduler lambda runs once an hours, reads the various config files and determines if 
any feeds need to be pulled in
  * If a feed is determined to need refreshing, the scheduler lambda launches a new lambda
to pull down that feed

### Feed ingestion

feeds are ingested through the ingestfeed lambda function.
this function is passed a event containing a feed dictionary, as well as the ES index where the indicators
from the feed will be stored.

This function then reads the feed dictionary, downloads the appropriate data from the feed url, saves that data to
an s3 bucket as a timestamped file, parses that
data into intel objects and finally indexes the feed data in teh specified ES index


### Elasticsearch

It is important to note that intel is not unique.  Each feed is queried daily and some intel
may appear in a feed across multiple days.  This is by designed, to allow a history view of indicators.

However, this may not be your default expected behavior when querying against the data, so it is
important to realize that the number of times an indicator shows up may not be indicative 
of a high threat score.

##### setup




## Requirements note

if pip3 fails on crypto install, make sure libssl-dev is installed (sudo apt install libssl-dev)


## Issues

* Elasticsearch, while extremely powerful in its query language, has a very high barrier to entry.  For actively slicing and dicing 
data, piping or copying data to splunk may yield more maleable data.

* Queries are best written in the developer tools section of kibana

## Recommended Reading:
Aws elasticsearch service: http://docs.aws.amazon.com/elasticsearch-service/latest
    
#### understanding elasticsearch upgrades
aws elasticsearch service takes a large amount of hassle out of running your own elasticsearch cluster
however, it is important to note that because of this abstraction, the variables that
need to be managed by the end user are still important decisions
* Dedicate master 
  * Dedicated master's are used to control all the operational chores of running
  and elasticsearch cluster.  They do not hold data, but manage indices, shards, etc.  The project ships with  
  some relatively sane defaults and should be plenty to get you off the ground
  and collecting intel.  However, as usage and data size grow, it is important to make sure the dedicate master size and count of 
  dedicated masters also gets increased.  This is a manual process and must be managed by changing variables in
  the terraform scripts.  Further reading: http://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-managedomains.html
  
* Upgrading or modifying the elasticsearch service domain.
  * when modifying or changing an elasticsearch domain, a new custer is spun up, data is copied over and 
  then the old cluster is shut down.  in doing this, you will incur charges for running both clusters
  for an hour.  After the data is copied over, the old cluster is shut down
  and you are charged only for the newly running cluster.  
  
 * Multi-zone awareness
   * Default ships with this disabled.  For production it is recommend this be turned on true.
     * note:  enableding multi-zone awareness requires an even number of instances and master nodes.


 * Migrating/Upgrading  to a new version: see http://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-version-migration.html

 * Sizing ElasticSearch Domains:  https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/sizing-domains.html


