from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

app.app_context().push()


class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    travel_start_time = db.Column(db.String(100))
    travel_end_time = db.Column(db.String(100))
    travel_location = db.Column(db.String(100))
    plan_completed = db.Column(db.Boolean)


@app.route('/')
def main_page():
    # we want to show all travel plan on main page 
    plan_list = TravelPlan.query.all()
    print(plan_list)
    return render_template('main_page.html', plan_list=plan_list)


if __name__ == "__main__":
    db.create_all()

    new_travel_plan = TravelPlan(travel_start_time="2022/09/26", travel_end_time="2023/09/26", travel_location="Columbia University", plan_completed=False)
    db.session.add(new_travel_plan)
    db.session.commit()


    app.run(debug=True)