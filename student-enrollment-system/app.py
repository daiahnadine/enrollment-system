from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enrollment.db'
db = SQLAlchemy(app)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    dob = db.Column(db.Date, nullable=False)
    program = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enrollment', methods=['GET', 'POST'])
def enrollment():
    if request.method == 'POST':
        full_name = request.form['full-name']
        email = request.form['email']
        dob_str = request.form['dob']
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        program = request.form['program']
        address = request.form['address']

       
        existing_enrollment = Enrollment.query.filter_by(email=email).first()

        if existing_enrollment:
            message = "Information is already existing!"
            return render_template('enrollment.html', message=message)

        try:
            new_enrollment = Enrollment(full_name=full_name, email=email, dob=dob, program=program, address=address)
            db.session.add(new_enrollment)
            db.session.commit()
            logging.info("Enrollment data saved successfully.")
            message = "Enrollment Successful."
            return render_template('enrollment.html', message=message)
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"Error saving enrollment data: {str(e)}")
            message = "Enrollment unsuccessful. Please try again."
            return render_template('enrollment.html', message=message)
        except OperationalError as e:
            db.session.rollback()
            logging.error(f"Database operation failed due to operational error: {str(e)}")
            message = "Enrollment unsuccessful. Please try again."
            return render_template('enrollment.html', message=message)

    return render_template('enrollment.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
