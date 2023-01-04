from sklearn.linear_model import LogisticRegression
import numpy as np
from .models import User
from .twitter import vectorize_tweet

def predict_user(user0_username, user1_username, hypo_tweet_text):
    #1 grab the users from database first
    user0 = User.query.filter(User.username==user0_username).one()
    user1 = User.query.filter(User.username==user1_username).one()

    #2 get word embeddings
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    #3 vertically stack the two 2D np arrays to make X matrix
    X_train = np.vstack([user0_vects, user1_vects])
     
    #4 concatenate our 0's and 1's for each tweet and make y matrix
    zeros = np.zeros(user0_vects.shape[0])
    ones = np.ones(user1_vects.shape[0])

    y_train = np.concatenate([zeros, ones])

    #5 instantiate and fit the logistic regression
    log_reg = LogisticRegression().fit(X_train, y_train)

    #6 verctorize the tweet text
    #  make sure that it's help in a 2D numpy array
    hypo_tweet_text = vectorize_tweet(hypo_tweet_text).reshape(1,-1)

    return log_reg.predict(hypo_tweet_text)[0]