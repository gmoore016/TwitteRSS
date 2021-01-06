import atoma
import requests
import argparse
import datetime
import tweepy
import os

# Maximum allowable length of a tweet
LENGTH_LIMIT = 280


def main():
    arg_parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    arg_parser.add_argument(
        '-s', "--source", action="store", required=True, help="The source feed to tweet"
    )

    arg_parser.add_argument(
        '-f', "--frequency", action="store", default="d", choices=['m', 'h', 'd', 'w'], help="The timeframe to check for posts. Can be 'm', 'h', 'd', or 'w' for minute, hour, day, and week respectively."
    )

    args = arg_parser.parse_args()

    new_posts = get_new_posts(**vars(args))

    consumer_key = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']

    access_token = os.environ['ACCESS_TOKEN']
    access_secret = os.environ['ACCESS_SECRET']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth)

    for post in new_posts:
        tweet_text = construct_tweet(post)
        api.update_status(tweet_text)


def get_new_posts(source, frequency):
    # Pull feed from web
    response = requests.get(source)
    feed = atoma.parse_atom_bytes(response.content)

    # Calculate standard for "new" posts
    threshold = get_threshold_time(frequency)

    # Array to store new posts
    new_posts = []

    # Interate through entries starting from newest
    for entry in feed.entries[0:4]:

        # If the entry is new, add it to list to publish
        if entry.updated.replace(tzinfo=None) > threshold:
            new_posts.append(entry)

        # Otherwise, we've reached the end of the new entries
        # and are done
        else:
            break

    # Return all posts published after threshold
    return new_posts


def get_threshold_time(frequency):
    """Function to calculate threshold time. Articles published
    after threshold time are "new" and should be processed. """
    # Pulls current time to determine "newness"
    now = datetime.datetime.now().replace(tzinfo=None)

    # Determines time frequency
    if frequency == 'm':
        delta = 1
    elif frequency == 'h':
        delta = 60
    elif frequency == 'd':
        delta = 24 * 60
    elif frequency == 'w':
        delta = 24 * 60 * 7
    else:
        raise Exception

    # If posts occurred after this time, they're new
    threshold = now - datetime.timedelta(minutes=delta)
    return threshold


def construct_tweet(post):
    """Given a post object, this extracts the appropriate title and link to construct a tweet"""
    # Extracts the post title
    post_title = post.title.value

    # In the event no link is found, use an empty string
    article_link = ""

    # Check each link to see if the link title matches the post title
    for link in post.links:
        if link.title == post_title:
            article_link = link.href

    # If the link is more than 280 characters on its own...
    if len(article_link) > LENGTH_LIMIT:
        # Attempt to tweet title and truncation note
        suffix = "; too large for tweet"
        text = post_title + suffix

        # If that's too large, shorten the title and add truncation note
        if len(text) > LENGTH_LIMIT:
            text = post_title[0:LENGTH_LIMIT - 4] + "..." + suffix

    # If the link fits but the title does not, truncate the title
    elif len(post_title) + len(" ") + len(article_link) > LENGTH_LIMIT:
        acceptable_len = LENGTH_LIMIT - len(article_link) - len("... ")
        text = post_title[0:acceptable_len] + "...\n" + article_link

    # If both title and link fit, add as many tags as possible
    else:
        post_content = post_title

        # Start with first tag
        i = 0

        # While we're still less than the length limit, add more hashtags
        while len(post_content) + len('\n') + len(article_link) <= LENGTH_LIMIT:
            # The text is the most recent acceptable version of the post
            text = post_content + '\n' + article_link

            # Try to lengthen the content
            post_content = post_content + ' ' + hashtagify(post.categories[i].term)

            # Move to the next hashtag on the next iteration
            i += 1

    # Return the composed tweet
    return(text)


for post in get_new_posts("http://marketdesigner.blogspot.com/feeds/posts/default", 'd'):
    print(construct_tweet(post))
