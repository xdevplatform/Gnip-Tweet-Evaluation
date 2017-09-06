# Overview

This repository contains a Python package and an executable script that
performs audience and conversation analysis on sets of Tweet payloads.

# Installation

This package can be installed from the cloned repository location.

`[REPOSITORY] $ pip install -e .[plotting]`

The optional `plotting` specification installs the extra dependencies needed
for time series plotting.
 
# What It Does

The core analysis module defines analyses to be performed on a set of Tweet bodies
(conversation analysis) and on a set of Twitter user biographies (audience analysis).
These analyses include the calculation of top n-grams, top hashtags, and top
URLs, along with geographic and language summaries.

# Interfaces and Examples

We do command-line Tweet evaluation with the `tweet_evaluator.py` script.  All
results can be returned to text files and to the screen.  From the repository
directory, you can run the following example analysis on dummy Tweet data:

```bash
$ cat example/dummy_tweets.json | tweet_evaluator.py -a -c
```

See the script's help menu for a full list of options and output specifications.

The analysis code is packaged into two modules in the `gnip_tweet_evaluation`
directory: `analysis.py` and `output.py`. The analysis module defines a setup 
function, which configures all the analyses to be run. It also provides the 
ability to produce *relative* results (see next section). The output module
handles data aggregation, display, and writing to files. 

# Relative Evaluation

This tool can be configured to perform a relative evaluation, in which the
results for an _analysis_ set of Tweets is shown relative to the results for a
_baseline_ set of Tweets. This functionality is enabled by specifying a set of
baseline Tweets with the `-b` option. The analysis Tweets are passed in as
before.

If conversation analysis is selected, a relative analysis returns the top over-
and under-indexing elements of the URLs and hashtags lists. No other elements
of the conversation analysis output are implemented for relative analysis.

Relative results for top-n lists are defined as follows:

The count for item `k` in the analyzed Tweets is `a_k`,
and `b_k` in the baseline Tweets. The sum of `a_k` for all `k`
found in the analyzed Tweets is `A`, and similarly `B` for the
baseline Tweets. To produce relative results, the `a_k` are 
re-weighted: `a'_k = a_k * ((a_k / A) - (b_k / B)) / (b_k / B)`.
The top `a'_k` by absolute value are displayed. 

