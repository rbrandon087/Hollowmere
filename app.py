from flask import Flask
import os
from flask import url_for
from dotenv import load_dotenv 
load_dotenv()
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

oauth = OAuth(app)
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@app.route('/')
def home():
    return "Welcome to Hollowmere!"

@app.route('/login')
def login():
    redirect_uri = url_for("auth", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route("/callback")
def auth():
    token = oauth.google.authorize_access_token()
    user = token["userinfo"]
    return f"Hello, {user['name']}! Your email is {user['email']}."

if __name__ == '__main__':
    app.run(debug=True)