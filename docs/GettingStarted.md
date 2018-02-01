# Getting Started

There are a few basic pre-requisites to getting started with ElasticIntel.

1. A working aws account with at least one profile configured on your deployment machine(laptop, desktop, instance will all work)
2. [Terraform 10.4+](https://www.terraform.io/intro/getting-started/install.html)
3. Python3+

### Configuration

Once the above requirements have been met, deployment steps should be quite simple.

1. Clone the repository(note, because of the python dependencies, the clone is at least moderately sized, it may take a minute)

2. Begin by copying the example config to `dev.conf` (this can actually be whatever you want it to be named, but for this
example we'll work with a "dev" environment


    ```commandline
    cp example.conf.example dev.conf
   ```

3. (optional) configure your slack bot integration by following the guide [here](slack_bot_setup.md)


4. Fill in the values for the configuration as needed.

    ```json
      "prefix": "",
      "aws_profile": "",
      "region": "us-east-1",
      "s3_bucket_name": "",
      "backend_bucket_name": "",
      "lambda_bot_name": "intelbot",
      "lambda_bot_token": "",
      "lambda_bot_verification_token": "",
      "elasticsearch_domain_name": "elastic-intel",
      "user_ip_address": ""
    }
    ```

    `prefix` - this is a unique designator which will be prepended to your resource names,
    allowing identification.  Good values are things like **dev**, **testing**, etc.

    `aws_profile` - The name of the aws profile you wish to use.  This can be a custom named profile,
    or the `default` profile you created when configuring the aws cli.

    `s3_bucket_name` - This is the name of the bucket where your feeds, configs and
    feed data will be stored.   Remember, **S3 buckets  must be globally unique**

    `backend_bucket_name` - This is the name of the bucket that will be used to hold terraform
    states. Again, remember **S3 buckets  must be globally unique**

    `lambda_bot_name` - The name of the slackbot as it will appear in your slack channel

    `lambda_bot_token` - The token provided to you by your slack admin for your bot

    `lambda_bot_verification_token` - The verification token for your bot integration

    `elasticsearch_domain_name` - The name for your elasticsearch service domain.   Unless you plan
    on running more than one instance of ElasticIntel __in the same aws account__, leave this with the default value

    `user_ip_address` - The ip address or cidr block to allow access to to elasticsearch
    service from.  This is simplest method of accessing the AWS ES service.  A more advanced
    setup is documented [here](link)

5. Install the python requirements
    ```
    pip3 install -r requirements.txt
    ```

6. Once the config is filled out, its time to deploy!  Deployment is very simpl, but does take some time.
Expect to let the installation run for 30 minutes or more.  This is largely due to the fact
that the ElasticSearch Service from AWS takes about 20 minutes to provision resources.
Fortunately, there should be zero user interaction required during this time, so take
the opportunity to go make some coffee, chase a puppy, or whatever else floats your boat.




