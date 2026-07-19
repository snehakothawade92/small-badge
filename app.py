from flask import Flask
from config import Config, mongo
from routes.auth import auth
from routes.badge import badge

app = Flask(__name__)

app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['MONGO_URI'] = Config.MONGO_URI

mongo.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(badge)

@app.route('/')
def home():
    return 'SmallBadge Running'

if __name__ == '__main__':
    app.run(debug=True)