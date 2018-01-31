# Getting Started

There are a few basic pre-requisites to getting started with ElasticIntel.

1. A working aws account with at least one profile configured on your deployment machine(laptop, desktop, instance will all work)
2. [Terraform 10.4+](https://www.terraform.io/intro/getting-started/install.html)

### Configuration

Once the above requirements have been met, deployment steps should be quite simple.

1. Clone the repository(note, because of the python dependencies, the clone is at least moderately sized, it may take a minute)

2. Begin by copying the example config to `dev.conf` (this can actually be whatever you want it to be named, but for this
example we'll work with a "dev" environment


```commandline
cp example.conf.example dev.conf
```

2.a - (optional) configure your slack bot integration by following the guide [here](slack_bot_setup.md)

3. Fill in the values for the configuration as needed.
