from flask_sqlalchemy import SQLAlchemy

# create a DB object from the SQLAlchemy class
DB = SQLAlchemy()

# one table for users and one for tweets

class User(DB.Model):
    # id column
    id = DB.Column(DB.BigInteger, primary_key=True, nullable=False)
    # username column
    username = DB.Column(DB.String, nullable=False)
    # most recent tweet id
    newest_tweet_id = DB.Column(DB.BigInteger)
    # backref in Tweet() class is as if we added a list of tweets
    # to the user class
    # tweets = []

    def __repr__(self):
        return f"User = {self.username}"

class Tweet(DB.Model):
    # id column
    id = DB.Column(DB.BigInteger, primary_key=True, nullable=False)
    # text column
    text = DB.Column(DB.Unicode(300))
    # let's store our word embeddings 'vectorization'
    # PickleType allows numpy.array to be stored in sqlalchemy database
    vect = DB.Column(DB.PickleType, nullable=False)
    # user_id column
    ## Is this 'user' referring to the next column over, which then
    ## pulls the User class's id attribute?
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    # user column creates a two-way link between user object and a tweet
    ## Why do we call the backref input "tweets"? What is that doing?
    ## And what is lazy=True?
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return f"Tweet = {self.text}"