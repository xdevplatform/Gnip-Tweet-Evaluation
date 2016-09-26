# Overview

This repository contains a Python package and an executable script that
performs audience and conversation analysis on sets of Tweet payloads.
The audience analysis optionally includes data from Twitter's
Audience API.

# Installation

This package can be installed from the cloned repository location.

`[REPOSITORY] $ pip install -e .[plotting,insights]`

The optional `plotting` specification installs the extra dependencies 
needed for time series plotting,
and the `insights` specification installs the 
[Gnip-Insights-Interface](https://github.com/jeffakolb/Gnip-Insights-Interface) 
package. To authenticate to the Gnip Insights products, you must have 
a credentials file called `.twitter_api_creds` in your home directory, 
which is formatted as described in the 
[README](https://github.com/jeffakolb/Gnip-Insights-Interface/README.md) 
for Gnip-Insights-Interface.

# What It Does

The core analysis module defines analyses to be performed on a set of Tweet bodies
(conversation analysis) and on a set of Twitter user biographies (audience analysis).
These analyses include the calculation of top n-grams, top hashtags, and top
URLs, along with geographic and language summaries.
We optionally augment the audience analysis by extracting the user IDs and running them
through the [Twitter Audience API](http://support.gnip.com/apis/audience_api/). 
This product returns aggregate info for demographic variables such as
gender, age, device, carrier, location, and interests. 

# Interfaces and Examples

We do command-line Tweet evaluation with the `tweet_evaluator.py` script. 
You must have credentials for the Audience API to get demographic model results.
Otherwise, you can use the `--no-insights` option to stick to Tweet payload data
All results can be returned to text files and to the screen. 
From the repository directory,
you can run the following example analysis on dummy Tweet data:

```bash
$ cat example/dummy_tweets.json | tweet_evaluator.py -a -c --no-insights
```

See the script's help menu for a full list of options and output specifications.

The analysis code is packaged into two modules in the `gnip_tweet_evaluation`
directory: `analysis.py` and `output.py`. The analysis module defines a setup 
function, which configures all the analyses to be run. It also provides the 
ability to produce *relative* results (see next section). The output module
handles data aggregation, display, and writing to files. 

# Relative Audience Evaluation

The Audience API interface can be configured to perform a relative evaluation,
in which the results for an _analysis_ set of user IDs is shown relative to the
results for a _baseline_ set of user IDs. This in enabled 
with the `-s` option to `user_id_evaluator.py`. This _splitting configuration_
specifies that you a doing a _relative_ Tweet evaluation. The splitting config file
defines these two sets of Tweets by defining two functions and mapping them in a dictionary.

The example in `examples/my_splitting_config.py` demonstrates the pattern:
```python
def analyzed_function(tweet):
    """ dummy filtering function """
    try:
        if len(tweet['actor']['preferredUsername']) > 7:
            return True
        else:
            return False
    except KeyError:
        return False

def baseline_function(tweet):
    return not analyzed_function(tweet)

splitting_config = {
    'analyzed':analyzed_function,
    'baseline':baseline_function
}
```

The function mapped to the _analyzed_ key selects Tweets in the analysis group,
and the function mapped to the _baseline_ key selects the baseline group of Tweets.
The result returned by the Audience API gives the difference (in percentage) between
the analysis and baseline groups, for categories in which both groups return results. 

