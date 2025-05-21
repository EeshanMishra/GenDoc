from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import ldap3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@dbserver/timeoffdb'
db = SQLAlchemy(app)

# LDAP connection setup (details omitted)
ldap_server = 'ldap://corporate.ldap.server'

class TimeOffRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Pending')

@app.route('/request_leave', methods=['POST'])
def request_leave():
    data = request.json
    # Validate and create leave request (simplified)
    new_request = TimeOffRequest(**data)
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Request submitted'}), 201

if __name__ == '__main__':
    app.run()
