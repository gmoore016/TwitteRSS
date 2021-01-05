import atoma
import requests
import argparse
import datetime

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

    for post in new_posts:
        tweet(post)


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
        # Convert string timestamp to Unix time
        timestamp_string = entry.updated
        published_time = calculate_unix_time(timestamp_string)

        # If the entry is new, add it to list to publish
        if published_time > threshold:
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
    now = datetime.datetime.now()

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

def tweet(post):
    print(post)


main()
