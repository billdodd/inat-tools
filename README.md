# inat-tools

## Introduction
This repository contains a set of python scripts to help
extract observation data from [iNaturalist](https://www.inaturalist.org)
to perform analysis or visualization.

The tools currently target
[Herps of Texas](https://www.inaturalist.org/projects/herps-of-texas)
project observations. And the observations are further filtered to only
retrieve "research" grade observations of Order _Anura_ (frogs and toads)
from Central Texas. But they can be readily forked and modified to target
other sets of observations.

Before you use these tools, please have a look at the description of
available iNaturalist APIs and datasets as described here:

[https://www.inaturalist.org/pages/developers](https://www.inaturalist.org/pages/developers)

Be sure to pay attention to the described rate limits.

For these tools, I chose to use the Node-js-based API that is mentioned
in the above document and described in detail here:

[http://api.inaturalist.org/v1/docs/](http://api.inaturalist.org/v1/docs/)

## Commands


### inat_observations

Command syntax:

```
usage: inat_observations.py [-h] [-v]

Query observations from iNaturalist

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  enable debug logging to STDERR
```

Sample output:

```
$ python3 inat_observations.py
...
12142872,"2018-05-02","Travis","Blanchard's Cricket Frog","2","27"
5480218,"2017-03-25","Williamson","Rio Grande Leopard Frog","1","19"
...
```

The above sample only shows two lines of CSV output. The actual output
was 2300+ lines long. The six fields in the CSV output are, respectively:

1. observation id
2. date observed
3. Texas county
4. species common name
5. call intensity
6. air temperature (degrees C)


### inat\_id\_search

Command syntax:

```
usage: inat_id_search.py [-h] (-l | -p | -t | -u) [-v] name

Lookup IDs on iNaturalist

positional arguments:
  name            the name of the iNaturalist resource to lookup

optional arguments:
  -h, --help      show this help message and exit
  -l, --location  search for a location (place) ID
  -p, --project   search for a project ID
  -t, --taxon     search for a taxon ID
  -u, --user      search for a user ID
  -v, --verbose   enable debug logging to STDERR
```

Sample output:

```
$ python3 inat_id_search.py --project 'Herps of Tex'
id=411, name="Herps of Texas"
```








  