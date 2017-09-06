#!/usr/bin/env python

import argparse
import logging
try:
    import ujson as json 
except ImportError:
    import json
import sys
import datetime
import os
import importlib

from gnip_tweet_evaluation import analysis,output

"""
Perform audience and/or conversation analysis on a set of Tweets.
"""

logger = logging.getLogger('analysis') 
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--identifier",dest="unique_identifier", default='0',type=str,
            help="a unique name to identify the conversation/audience; default is '%(default)s'")
    parser.add_argument("-c","--do-conversation-analysis",dest="do_conversation_analysis",action="store_true",default=False,
            help="do conversation analysis on Tweets")
    parser.add_argument("-a","--do-audience-analysis",dest="do_audience_analysis",action="store_true",default=False,
            help="do audience analysis on users") 
    parser.add_argument("-i","--input-file-name",dest="input_file_name",default=None,
            help="file containing Tweet data; take input from stdin if not present") 
    parser.add_argument('-o','--output-dir',dest='output_directory',default=os.environ['HOME'] + '/tweet_evaluation/',
            help='directory for output files; default is %(default)s')
    parser.add_argument('-b','--baseline-input-file',dest='baseline_input_name',default=None,
            help='Tweets against which to run a relative analysis')
    args = parser.parse_args()

    # get the time right now, to use in output naming
    time_now = datetime.datetime.now()
    output_directory = '{0}/{1:04d}/{2:02d}/{3:02d}/'.format(args.output_directory.rstrip('/')
            ,time_now.year
            ,time_now.month
            ,time_now.day
            )
    # get the empty results object, which defines the measurements to be run
    results = analysis.setup_analysis(do_conversation = args.do_conversation_analysis, do_audience = args.do_audience_analysis) 

    baseline_results = None
    if args.baseline_input_name is not None:
        baseline_results = analysis.setup_analysis(do_conversation = args.do_conversation_analysis, do_audience = args.do_audience_analysis)

    # manage input sources, file opening, and deserialization
    if args.input_file_name is not None:
        tweet_generator = analysis.deserialize_tweets(open(args.input_file_name))
    else:
        tweet_generator = analysis.deserialize_tweets(sys.stdin)

    # run analysis
    analysis.analyze_tweets(tweet_generator, results)

    # run baseline analysis, if requests
    if baseline_results is not None:
        baseline_tweet_generator = analysis.deserialize_tweets(open(args.baseline_input_name)) 
        analysis.analyze_tweets(baseline_tweet_generator, baseline_results)
        results = analysis.compare_results(results,baseline_results)
    
    # dump the output
    output.dump_results(results, output_directory, args.unique_identifier)
