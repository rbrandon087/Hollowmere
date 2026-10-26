from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Hollowmere!"

@app.route('/login')
def login():
    return "Login page coming soon."

if __name__ == '__main__':
    app.run(debug=True)