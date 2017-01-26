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

This tool can be configured to perform a relative evaluation,
in which the results for an _analysis_ set of Tweets is shown relative to the
results for a _baseline_ set of Tweets. In the case of audience analysis,
the results for the _analysis_ user IDs are compared to those for the 
_baseline_ user IDs.This functionality is enabled by specifying a 
set of baseline Tweets with the `-b` option. The analysis Tweets are passes in as before.

If audience analysis is selected, a relative analysis returns 
difference in percentage for each category in the output taxonomy 
of the Audience API. If a category is below the reporting threshold 
for either set of users, it is not displayed in the relative analysis
output. Other elements of the audience analysis, such as geo locations,
are not implement for the relative analysis. If conversation analysis
is selected, a relative analysis returns the top over- and under-indexing
elements of the URLs and hashtags lists. No other elements of the 
conversation analysis output are implemented for relative analysis.

Relative results for top-n lists are defined as follows:

The count for item `k` in the analyzed Tweets is `a_k`,
and `b_k` in the baseline Tweets. The sum of `a_k` for all `k`
found in the analyzed Tweets is `A`, and similarly `B` for the
baseline Tweets. To produce relative results, the `a_k` are 
re-weighted: `a'_k = a_k * ((a_k / A) - (b_k / B)) / (b_k / B)`.
The top `a'_k` by absolute value are displayed. 

