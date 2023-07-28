import atexit
import time

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_cors import CORS, cross_origin
from recommendation import (ContentBaseRecommendation, ItemBasedRecommendation,
                            UserBasedRecommendation)
from wrapper import AppWrapper

SUPPORT_RECOMMENDATIONS_CLASS = [ContentBaseRecommendation, UserBasedRecommendation, ItemBasedRecommendation]

flask_app = Flask(__name__)

app = AppWrapper(flask_app)
cors = CORS(app.app)

app.init_recommendations(SUPPORT_RECOMMENDATIONS_CLASS)

def home():
    return "Welcome to Book Recommendation service"

app.add_endpoint('/', 'home', home, methods=['GET'])
app.add_endpoint('/api/recommendation/<id>/<type>', 'book-item-rec', app.recommend, methods=['GET'])
app.add_endpoint('/api/samples', 'rec-samples', app.get_samples, methods=['GET'])
app.add_endpoint('/api/popular', 'popular-books', app.get_popular_books, methods=['GET'])



def init_cron_job(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=app.update_rec_models, trigger="cron", hour=12 )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

# init_cron_job(app)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)
