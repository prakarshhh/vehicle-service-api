from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class VehicleService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(50), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    service_cost = db.Column(db.Float, nullable=False)
