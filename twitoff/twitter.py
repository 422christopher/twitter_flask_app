from os import getenv
import tweepy
from .models import DB, User, Tweet
import spacy

# Get API keys from .env file
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

# Connect to Twitter API
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)

def add_or_update_user(username):
    '''Takes a username and pulls that user's data
    and tweets from the API. If user already exists, 
    then we will just check to see if there are any new 
    tweets from that user we don't already have, and we will 
    add new tweets to the DB.'''

    # Atomicity. Try adding all of the account or nothing. Not parts of it.
    try:
        # get user information from Twitter
        twitter_user = TWITTER.get_user(screen_name=username)

        # check to see if this user is already in the DB
        # Is there a user with the same id already in DB? Compare ID's
        # If we don't already have user, then create new one
        # Python trick leveraging 'or' statements
        # the first part is checking if ID already exists then set it to db_user
        # the second part creates the user if the first part came out False
        db_user = (User.query.get(twitter_user.id)) or User(id=twitter_user.id, username=username)

        # Add user to the database
        # this will NOT re-add if the user is already in
        DB.session.add(db_user)

        # then get user's tweets (in a list)and then commit after
        tweets = twitter_user.timeline(count=200,
                                        exclude_replies=True,
                                        include_rts=False,
                                        tweet_mode='extended',
                                        since_id=db_user.newest_tweet_id)

        # update the newest_tweet_id if there have been new tweets
        # since the last time this user tweeted
        ## If we don't have this line, an error with be thrown when
        ## you try to update. WHY?
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # add the individual tweets
        for tweet in tweets:
            # vectorize the tweet text
            tweet_vector = vectorize_tweet(tweet.full_text)
            # limit the tweet text to 300 chars because models.py Tweet class
            # only allows 300 characters
            db_tweet = Tweet(id=tweet.id,
                            text=tweet.full_text[:300],
                            vect = tweet_vector,
                            user_id=db_user.id)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f"Error processing {username}: {e}")
        raise e

    else:
        # save changes to DB
        DB.session.commit()

# now we have the same tool we used in the flask shell
nlp = spacy.load('my_model/')

def vectorize_tweet(tweet_text):
    # give some text and return word embedding
    return nlp(tweet_text).vector