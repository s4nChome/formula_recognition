from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# 数据库配置
HOSTNAME = "127.0.0.1"
PORT = "3306"
DATABASE = "formula_recognition"
USERNAME = "s4nchome"
PASSWORD = "12345678"
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
db = SQLAlchemy(app)

# 导入API
from router import *

if __name__ == '__main__':
    app.run(debug=True)
#host="0.0.0.0", port=5000,