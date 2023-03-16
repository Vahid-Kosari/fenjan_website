from flask import Flask, render_template, url_for
from datetime import datetime



app = Flask(__name__)


acounts = [
    {
        'User Name': 'Vahid Kosari',
        'Email': 'vahid59m@yahoo.com',
        'Expire Date': '2023/02/20',
        'Keywords': '1-salam 2-aleyk 3-qorbanat 4-chera jade bastas? 5-hast dige'
    },
    {
        'User Name': 'Hue Salari',
        'Email': 'mh-salari@yahoo.com',
        'Expire Date': '2023/02/20s',
        'Keywords': '1-Hello 2-aleyk 3-qorbanat 4-chera jade bastas? 5-rah baraye residan hast vali dure'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', year=datetime.now().year)

@app.route("/admin")
def admin():
    return render_template('base.html', title='Admin', posts=acounts)

@app.route("/register")
def register():
    return render_template('register.html', title='Register', posts=acounts)

if __name__ == '__main__':
    app.run(debug=True)