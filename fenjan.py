import mysql.connector
import json

# from dotenv import load_dotenv

from flask import Flask, render_template
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Customer:
    name: str
    email: str
    subscription_date: datetime
    expiration_date: str
    keywords: list

# @dataclass
# class CustomerDatabase:
    


app = Flask(__name__)


accounts = [
    {
        'User_Name': 'Vahid Kosari',
        'Email': 'vahid59m@yahoo.com',
        'Subscription_Date': '2023/02/20',
        'Expire_Date': '2023/12/20',
        'Keywords': '1-salam 2-aleyk 3-qorbanat 4-chera jade bastas? 5-hast dige',
        'status': 'active'
    },
    {
        'User_Name': 'Nahid Kosari',
        'Email': 'vahid59m@yahoo.com',
        'Subscription_Date': '2023/02/20',
        'Expire_Date': '2023/02/20',
        'Keywords': '11-salam 2-aleyk 3-qorbanat 4-chera jade bastas? 5-hast dige',
        'status': 'active'
    },
    {
        'User_Name': 'Hue Salari',
        'Email': 'mh-salari@yahoo.com',
        'Subscription_Date': '2023/02/20',
        'Expire_Date': '2023/02/20s',
        'Keywords': """'11-salam 2-aleyk 3-qorbanat 4-chera jade bastas? 5-hast dige
          3-qorbanat 4-chera jade bastas? 5-rah baraye residan hast vali dure 
          3-qorbanat 4-chera jade bastas? 5-rah baraye residan hast vali dure
          3-qorbanat 4-chera jade bastas? 5-rah baraye residan hast vali dure'""",
        'status': 'expired'
    },
    {
        'User_Name': 'VVahid Kosari',
        'Email': 'vahid59m@yahoo.com',
        'Subscription_Date': '2023/02/20',
        'Expire_Date': '2023/02/20',
        'Keywords': """'11-salam 2-aleyk 3-qorbanat 4-chera jade bastas? 5-hast dige
          3-qorbanat 4-chera jade bastas? 5-rah baraye residan hast vali dure 
          3-qorbanat 4-chera jade bastas? 5-rah baraye residan hast vali dure
          3-qorbanat 4-chera jade bastas? 5-rah baraye residan hast vali dure'""",
        'status': 'active'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', year=datetime.now().year)

@app.route("/admin")
def admin():
    return render_template('admin.html', title='Admin', accounts=accounts, year=datetime.now().year)

@app.route("/register")
def register():
    return render_template('register.html', title='Register', accounts=accounts)

@app.route("/edit_function")
def edit_function():
    return render_template('home.html', year=datetime.now().year)

# def delete_function():
#     return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)