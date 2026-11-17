from flask import Flask
from member4 import member4

app = Flask(__name__)

app.secret_key = "mysecretkey"
app.config["DATABASE"] = "lostfound.db"

app.register_blueprint(member4)

@app.route("/")
def home():
    return """
    <h1>Lost and Found Management System</h1>
    <h2>Member 4 Module</h2>
    <p>Flask application is running successfully!</p>
    """

if __name__ == "__main__":
    app.run(debug=True)