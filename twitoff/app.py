from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .twitter import add_or_update_user
from .predict import predict_user

def create_app():

    app = Flask(__name__)

    # If DB exists, it connects, but it not, then it creates an 'environment' of the DB.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # creates the database
    DB.init_app(app)

    # the '/' means home page
    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route('/reset')
    def reset():
        # Drop all database tables
        DB.drop_all()

        # Recreate tables according to schemas in models.py
        DB.create_all()
        return render_template('base.html', title='Reset Database')



    @app.route('/update')
    def update():
        # get list of all the Class Objects, which have attributes we can call
        users = User.query.all()

        for username in [user.username for user in users]:
            add_or_update_user(username)

        return render_template('base.html', title='Updated Database')

    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):
        username = username or request.values['user_name']

        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f"User {username} has been successfully added."

            tweets = User.query.filter(User.username==username).one().tweets
        
        except Exception as e:
            message = f"Error adding {username}: {e}"
            tweets = []

        return render_template('user.html', title=username, tweets=tweets, message=message)

    @app.route('/compare', methods=['POST'])
    def compare():

        user0, user1 = sorted([request.values['user0'], request.values['user1']])
        hypo_tweet_text = request.values['tweet_text']

        if user0 == user1:
            message = "Cannot compare the same user"
        else:
            prediction = predict_user(user0, user1, hypo_tweet_text)

            # Get into this if statement only when user 1 is predicted
            # because 1 is user 1 in the y_train data
            if prediction:
                message = f'"{hypo_tweet_text}" is more likely to be said by {user1} than by {user0}'
            # this else block if prediction is 0
            else:
                message = f'"{hypo_tweet_text}" is more likely to be said by {user0} than by {user1}'

        return render_template('prediction.html', title="Prediction", message=message)

    return app
