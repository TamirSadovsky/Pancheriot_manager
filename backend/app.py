from flask import Flask, jsonify, request
from flask_cors import CORS
from db import find_daily_appointments, update_driver_database, update_signature, find_daily_appointments_all
from gc_tools import save_signature_gc
from operator import itemgetter



app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print("Username:", username)
    print("Password:", password)

    # Procedure to check if the user deatils correct
    # The procedure returns the branch id of the user

    if username == "admin" and password == "1234":
        return jsonify({'success': True, 'branch_id': 0})
    else:
        return jsonify({'success': True, 'branch_id': 21})
    #else:
    #    return jsonify({'success': False}), 401


@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    branch_id = request.args.get('branch_id', type=int)
    appointment_date = request.args.get('appointment_date')  # Format: YYYY-MM-DD

    try:
        if branch_id == 0:
            appointments = find_daily_appointments_all(appointment_date)
        else:
            appointments = find_daily_appointments(branch_id, appointment_date)

        print("RESULT TYPE:", type(appointments))
        if isinstance(appointments, list):
            print("FIRST ROW:", appointments[0] if appointments else "No results")
        else:
            print("⚠️ Unexpected return:", appointments)

        appointments = sorted(appointments, key=itemgetter('AppointmentTime'))

        return jsonify(appointments)

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/driver-arrived', methods=['POST'])
def update_driver_arrival():
    # Prefer JSON body over query string for POST requests
    data = request.get_json()

    if not data or "AppointmentID" not in data:
        return jsonify({"success": False, "error": "Missing AppointmentID"}), 400

    appointment_id = data["AppointmentID"]
    print(f"🔄 Received AppointmentID: {appointment_id}")

    result = update_driver_database(appointment_id)

    if result["success"]:
        return jsonify({"success": True, "message": "Driver marked as arrived"}), 200
    else:
        return jsonify({"success": False, "error": result["error"]}), 500


@app.route('/api/set-signature', methods=['POST'])
def update_signature_sent():
    data = request.get_json()

    if not data or "AppointmentID" not in data or "Signeture" not in data:
        return jsonify({"success": False, "error": "Missing AppointmentID or Signature"}), 400

    appointment_id = data["AppointmentID"]
    signature = data["Signeture"]

    print(f"🔄 Received AppointmentID: {appointment_id}")
    print(f"🔄 Received Signature (base64 length): {len(signature)}")

    # Save image and get public URL
    url = save_signature_gc(appointment_id, signature)

    # Update the DB
    result = update_signature(appointment_id, url)

    if result["success"]:
        return jsonify({"success": True, "message": "Signature saved successfully", "url": url}), 200
    else:
        return jsonify({"success": False, "error": result["error"]}), 500


if __name__ == '__main__':
    app.run(debug=True)
