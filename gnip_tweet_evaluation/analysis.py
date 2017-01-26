import sys
import logging
import uuid
import datetime
import collections
import copy
try:
    import ujson as json
except ImportError:
    import json
from collections import defaultdict

from simple_n_grams.simple_n_grams import SimpleNGrams

logger = logging.getLogger("analysis")

def analyze_tweets(tweet_generator,results): 
    """ 
    Entry point for Tweet input.  A sequence of Tweet dicts and a results object are
    required.
    """ 
        
    for tweet in tweet_generator:
        analyze_tweet(tweet,results)

    if "audience_api" in results: 
        user_ids = results["tweets_per_user"].keys()
        analyze_user_ids(user_ids,results)

def compare_results(results_analyzed, results_baseline):

    user_ids_analyzed = results_analyzed["tweets_per_user"].keys()
    user_ids_baseline = results_baseline["tweets_per_user"].keys()
    logger.info('{} users in analysis user group'.format(len(user_ids_analyzed)))
    logger.info('{} users in baseline user group'.format(len(user_ids_baseline))) 
  
    results_output = {}

    produce_relative_audience(results_output,
            results_analyzed,
            results_baseline
            )

    produce_relative_text(results_output,
            results_analyzed,
            results_baseline
            )

    return results_output    

def deserialize_tweets(line_generator):
    """ 
    Generator function to manage JSON deserialization
    """
    for line in line_generator:
        try:
            yield json.loads(line)
        except ValueError:
            continue

def analyze_user_ids(user_ids, results, groupings = None):
    """ 
    Call to Audience API happens here.  All we ask from the caller are user IDs, a
    results object, and (optionally) a grouping.
    """
    import gnip_insights_interface.audience_api as api

    # set up groupings
    if groupings is not None:
        use_groupings = groupings
    else:
        grouping_dict = {"groupings": {
            "gender": {"group_by": ["user.gender"]}
            , "location_country": {"group_by": ["user.location.country"]}
            , "location_country_region": {"group_by": ["user.location.country", "user.location.region"]}
            , "interest": {"group_by": ["user.interest"]}
            , "tv_genre": {"group_by": ["user.tv.genre"]}
            , "device_os": {"group_by": ["user.device.os"]}
            , "device_network": {"group_by": ["user.device.network"]}
            , "language": {"group_by": ["user.language"]}
        }}
        use_groupings = json.dumps(grouping_dict)

    results["audience_api"] = api.query_users(list(user_ids), use_groupings)


def produce_relative_audience(results_output, results_analyzed, results_baseline): 
    """
    When multiple absolute results are stored at the 'baseline' and 'analyze'
    keys, this function computes their relative results and places them at the
    base level.
    """
    
    data_analyzed = results_analyzed['audience_api']
    data_baseline = results_baseline['audience_api']
    data_compared = collections.defaultdict(dict)
    
    for group_name, grouping in data_analyzed.items():
        if 'errors' in grouping:
            logger.warning(str(grouping))
            continue
        if isinstance(grouping,str):
            logger.warning(str(grouping))
            continue

        for key_level_1,value_level_1 in grouping.items():
            if isinstance(value_level_1,str):
                analyzed_value = float(value_level_1)
                try:
                    baseline_value = float(data_baseline[group_name][key_level_1])
                    data_compared[group_name][key_level_1] = u"{0:.2f}".format(analyzed_value - baseline_value)
                except KeyError:
                    pass
            elif isinstance(value_level_1,dict):
                for key_level_2,value_level_2 in value_level_1.items():
                    analyzed_value = float(value_level_2 )
                    try:
                        baseline_value = float(data_baseline[group_name][key_level_1][key_level_2]) 
                        if key_level_1 not in data_compared[group_name]:
                            data_compared[group_name][key_level_1] = {} 
                        data_compared[group_name][key_level_1][key_level_2] = u"{0:.2f}".format(analyzed_value - baseline_value)
                    except KeyError:
                        pass
            else:
                sys.stderr.write("Found a value that is neither dict nor unicode str. [{}] Exiting.\n".format(type(value_level_1)))
                sys.exit(1)
    results_output['audience_api'] = data_compared
   
def produce_relative_text(results_output,results_analyzed,results_baseline):
    """
    Return data representing the analyzed data renomalized by the baseline data
    """

    # results to renormalize
    keys = ['hashtags','urls']
    for key in keys:
        try:
            analyzed = results_analyzed[key] 
        except KeyError:
            continue
        baseline = results_baseline[key]

        # get normalization factors
        B = sum(baseline.values())
        A = sum(analyzed.values())

        compared = defaultdict(int)
        for a_item,a_value in analyzed.items():
            if a_item not in baseline:
                factor = 1
            else:
                a_frac = a_value / A 
                b_frac = baseline[a_item] / B
                factor = (a_frac - b_frac)/a_frac
            compared[a_item] = analyzed[a_item] * factor
        results_output[key] = compared
    

def setup_analysis(do_conversation = False, do_audience = False, identifier = None, input_results = None):
    """
    Created placeholders for quantities of interest in results structure;
    return results data structure.

    If an identifier is specified, place the measurement accumulators at a
    particular key.

    """
    
    def weight_and_screennames():
        return {"weight": 0, "screennames": set([])}

    results = {
            "tweet_count": 0,
            "non-tweet_lines": 0,
            "tweets_per_user": defaultdict(int),
            #"user_id_to_screenname": 
    }
    if do_conversation:
        results['do_conversation'] = True
        results["body_term_count"] = SimpleNGrams(
                char_lower_cutoff=3
                ,n_grams=2
                ,tokenizer="twitter"
                )
        results["hashtags"] = defaultdict(int)
        results["urls"] = defaultdict(int)
        results["number_of_links"] = 0
        results["utc_timeline"] = defaultdict(int)
        results["local_timeline"] = defaultdict(int)
        results["at_mentions"] = defaultdict(weight_and_screennames)
        results["in_reply_to"] = defaultdict(int)
        results["RT_of_user"] = defaultdict(weight_and_screennames)
        results["quote_of_user"] = defaultdict(weight_and_screennames)
    else:
        results['do_conversation'] = True

    if do_audience:
        results['do_audience'] = True
        results["bio_term_count"] = SimpleNGrams(
                char_lower_cutoff=3
                ,n_grams=1
                ,tokenizer="twitter"
                )
        results["profile_locations_regions"] = defaultdict(int)
        results["audience_api"] = ""
    else:
        results['do_audience'] = False

    # in the future we could add custom fields by adding kwarg = func where func is agg/extractor and kwarg is field name
   
    return results

def analyze_tweet(tweet, results):
    """
    Add relevant data from a tweet to 'results'
    """

    ######################################
    # fields that are relevant for user-level and tweet-level analysis
    # count the number of valid Tweets here
    # if it doesn't have at least a body and an actor, it's not a tweet
    try: 
        body = tweet["body"]
        userid = tweet["actor"]["id"][:15]
        results["tweet_count"] += 1
    except (ValueError, KeyError):
        if "non-tweet_lines" in results:
            results["non-tweet_lines"] += 1
        return

    # count the number of tweets from each user
    if "tweets_per_user" in results:
        results["tweets_per_user"][tweet["actor"]["id"][15:]] += 1
    
    #######################################
    # fields that are relevant for the tweet-level analysis
    # ------------------> term counts
    # Tweet body term count
    if "body_term_count" in results:
        results["body_term_count"].add(tweet["body"])

    # count the occurences of different hashtags
    if "hashtags" in results:
        if "hashtags" in tweet["twitter_entities"]:
            for h in tweet["twitter_entities"]["hashtags"]:
                results["hashtags"][h["text"].lower()] += 1
    
    try:
        # count the occurences of different top-level domains
        if ("urls" in results) and ("urls" in tweet["gnip"]):
            for url in tweet["gnip"]["urls"]:
                try:
                    results["urls"][url["expanded_url"].split("/")[2]] += 1
                except (KeyError,IndexError,AttributeError):
                    pass
        # and the number of links total
        if ("number_of_links" in results) and ("urls" in tweet["gnip"]):
            results["number_of_links"] += len(tweet["gnip"]["urls"])
    except KeyError:
        pass
    
    # -----------> timelines
    # make a timeline of UTC day of Tweets posted
    if "utc_timeline" in results:
        date = tweet["postedTime"][0:10]
        results["utc_timeline"][date] += 1

    # make a timeline in normalized local time (poster's time) of all of the Tweets
    if "local_timeline" in results:
        utcOffset = tweet["actor"]["utcOffset"]
        if utcOffset is not None:
            posted = tweet["postedTime"]
            hour_and_minute = (datetime.datetime.strptime(posted[0:16], "%Y-%m-%dT%H:%M") + 
                    datetime.timedelta(seconds = int(utcOffset))).time().strftime("%H:%M")
            results["local_timeline"][hour_and_minute] += 1
    
    # ------------> mention results
    # which users are @mentioned in the Tweet
    if "at_mentions" in results:
        for u in tweet["twitter_entities"]["user_mentions"]:
            # update the mentions with weight + 1 and 
            # list all of the screennames (in case a name changes)
            if u["id_str"] is not None:
                results["at_mentions"][u["id_str"]]["weight"] += 1 
                results["at_mentions"][u["id_str"]]["screennames"].update([u["screen_name"].lower()])
    
    # count the number of times each user gets replies
    if ("in_reply_to" in results) and ("inReplyTo" in tweet):
        results["in_reply_to"][tweet["inReplyTo"]["link"].split("/")[3].lower()] += 1

    # --------------> RTs and quote Tweet
    # count share actions (RTs and quote-Tweets)
    # don't count self-quotes or self-RTs, because that's allowed now
    if (("quote_of_user" in results) or ("RT_of_user" in results)) and (tweet["verb"] == "share"):
        # if it's a quote tweet
        if ("quote_of_user" in results) and ("twitter_quoted_status" in tweet["object"]):
            quoted_id = tweet["object"]["twitter_quoted_status"]["actor"]["id"][15:]
            quoted_name = tweet["object"]["twitter_quoted_status"]["actor"]["preferredUsername"]
            if quoted_id != tweet["actor"]["id"]:
                results["quote_of_user"][quoted_id]["weight"] += 1       
                results["quote_of_user"][quoted_id]["screennames"].update([quoted_name])
        # if it's a RT
        elif ("RT_of_user" in results):
            rt_of_name = tweet["object"]["actor"]["preferredUsername"].lower()
            rt_of_id = tweet["object"]["actor"]["id"][15:]
            if rt_of_id != tweet["actor"]["id"]:
                results["RT_of_user"][rt_of_id]["weight"] += 1 
                results["RT_of_user"][rt_of_id]["screennames"].update([rt_of_name])

    ############################################
    # actor-property qualities
    # ------------> bio terms
    if "bio_term_count" in results:
        if tweet["actor"]["id"][:15] not in results["tweets_per_user"]:
            try:
                if tweet["actor"]["summary"] is not None:
                    results["bio_term_count"].add(tweet["actor"]["summary"])
            except KeyError:
                pass
    
    # ---------> profile locations
    if "profile_locations_regions" in results:
        # if possible, get the user's address
        try:
            address = tweet["gnip"]["profileLocations"][0]["address"]
            country_key = address.get("country", "no country available")
            region_key = address.get("region", "no region available")
        except KeyError:
            country_key = "no country available"
            region_key = "no region available"
        results["profile_locations_regions"][country_key + " , " + region_key] += 1
    
