from flask import Flask, request, jsonify
from models import db, VehicleService
from datetime import datetime

app = Flask(__name__)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vehicle_service.db"
db.init_app(app)

# Initialize the database
with app.app_context():
    db.create_all()


@app.route("/service_count", methods=["GET"])
def get_service_count():
    services = (
        db.session.query(VehicleService.vehicle_id, db.func.count(VehicleService.id))
        .group_by(VehicleService.vehicle_id)
        .all()
    )

    service_count = {vehicle_id: count for vehicle_id, count in services}

    return jsonify(service_count), 200


@app.route("/service_count/<string:vehicle_id>", methods=["GET"])
def get_service_count_by_vehicle(vehicle_id):
    service_count = (
        db.session.query(db.func.count(VehicleService.id))
        .filter(VehicleService.vehicle_id == vehicle_id)
        .scalar()
    )

    if service_count is None:
        return jsonify({"error": "Vehicle not found"}), 404

    return jsonify({vehicle_id: service_count}), 200


@app.route("/service", methods=["POST"])
def add_service():
    data = request.get_json()

    # Debug: Print the incoming data
    print(data)  # Add this line

    # Check if data is valid
    if not data or not isinstance(data, list):
        return jsonify({"error": "Invalid input data"}), 400

    for entry in data:
        if (
            "vehicle_id" not in entry
            or "service_date" not in entry
            or "description" not in entry
            or "service_cost" not in entry
        ):
            return jsonify({"error": "Invalid input data"}), 400

        try:
            # Create a new VehicleService object
            new_service = VehicleService(
                vehicle_id=entry["vehicle_id"],
                service_date=datetime.strptime(
                    entry["service_date"], "%Y-%m-%d"
                ).date(),
                description=entry["description"],
                service_cost=entry["service_cost"],
            )

            # Add the new service to the session
            db.session.add(new_service)

        except Exception as e:
            print(e)  # Print any exceptions
            return jsonify({"error": "An error occurred while adding the service"}), 500

    # Commit all new services to the database at once
    db.session.commit()

    return jsonify({"message": "Services added successfully"}), 201


@app.route("/service", methods=["GET"])
def get_services():
    services = VehicleService.query.all()
    output = []
    for service in services:
        service_data = {
            "id": service.id,
            "vehicle_id": service.vehicle_id,
            "service_date": str(service.service_date),
            "description": service.description,
            "service_cost": service.service_cost,
        }
        output.append(service_data)
    return jsonify({"services": output}), 200


@app.route("/service/<vehicle_id>", methods=["GET"])
def get_vehicle_service(vehicle_id):
    services = VehicleService.query.filter_by(vehicle_id=vehicle_id).all()
    if not services:
        return jsonify({"message": "No service records found!"}), 404

    output = []
    for service in services:
        service_data = {
            "id": service.id,
            "service_date": str(service.service_date),
            "description": service.description,
            "service_cost": service.service_cost,
        }
        output.append(service_data)
    return jsonify({"services": output}), 200


@app.route("/services/<string:vehicle_id>", methods=["GET"])
def get_services_by_vehicle(vehicle_id):
    services = VehicleService.query.filter_by(vehicle_id=vehicle_id).all()

    if services:
        result = [
            {
                "service_date": service.service_date.strftime("%Y-%m-%d"),
                "description": service.description,
                "service_cost": service.service_cost,
            }
            for service in services
        ]
        return (
            jsonify(
                {
                    "vehicle_id": vehicle_id,
                    "service_count": len(services),
                    "services": result,
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "No services found for this vehicle"}), 404


if __name__ == "__main__":
    app.run(debug=True)
