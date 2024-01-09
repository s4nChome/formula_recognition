from app import db,app

class ModelName(db.Model):
    __tablename__ = 'model'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)

class Success(db.Model):
    __tablename__ = 'success'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, nullable=False)
    model = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    result = db.Column(db.Text)

class Error(db.Model):
    __tablename__ = 'error'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, nullable=False)
    model = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.String(255), nullable=False)

class Correction(db.Model):
    __tablename__ = 'correction'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, nullable=False)
    model = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    wrong_result = db.Column(db.Text)
    right_result = db.Column(db.Text)


# with app.app_context():
#     db.create_all()