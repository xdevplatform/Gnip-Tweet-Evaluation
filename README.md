# Overview

This repository contains a Python package and executable scripts that
perform audience and conversation analysis on sets of Tweets payloads,
Tweet IDs, or Twitter user IDs.

# Installation

This package can be pip-installed.

`$ pip install gnip_tweet_evaluation[plotting]` 

You can also install a local version from the cloned repository location.

`[REPOSITORY] $ pip install gnip_tweet_evaluation[plotting] -U`

In both cases, `plotting` installs the extra dependencies needed for time series plotting. 

# What It Does

The core analysis module defines analyses performed on a set of Tweet bodies
(conversation analysis) and on a set of Twitter user biographies (audience analysis).
These analyses include the calculation of top n-grams, top hashtags, and top
URLs, along with geographic and language summaries.
We augment audience analysis by extracting the user IDs and running them
through the Twitter Audience API. This product returns demographic aggregations
for gender, age, device, carrier, location, and interests. 
We also provide an interface for passing a
set of Tweet IDs to the Twitter Engagements API, which provide 
engagement data such as impressions, favorites, and replies.

# Interfaces and Examples

We do tweet evaluation with the `tweet_evaluator.py` script. You must have
credentials for the Audience API to get demographic model results. All results
can be returned to text files and to the screen. 

We pass user IDs directly to the Audience API with the 
`user_id_evaluator.py` script, and the results can be written to text files
or printed to the screen. 

We get Tweet engagement data with the `tweet_engagements.py` script, which
takes input Tweet IDs from `stdin` or from a text file.

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

