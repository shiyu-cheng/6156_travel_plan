from flask import Flask, render_template, request, redirect, url_for
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

@app.route("/add", methods=["POST"])
def add():
    # add new travel plan 
    start = request.form.get("travel_start_time")
    end = request.form.get("travel_end_time")
    loc = request.form.get("travel_location")
    new_plan = TravelPlan(travel_start_time=start, travel_end_time=end, travel_location=loc, plan_completed=False)
    db.session.add(new_plan)
    db.session.commit()
    return redirect(url_for("main_page"))

@app.route("/update/<int:plan_id>")
def update(plan_id):
    # add new travel plan 
    target_plan = TravelPlan.query.filter_by(id=plan_id).first()
    target_plan.plan_completed = not target_plan.plan_completed
    db.session.commit()
    return redirect(url_for("main_page"))

@app.route("/delete/<int:plan_id>")
def delete(plan_id):
    # add new travel plan 
    target_plan = TravelPlan.query.filter_by(id=plan_id).first()
    db.session.delete(target_plan)
    db.session.commit()
    return redirect(url_for("main_page"))

if __name__ == "__main__":
    db.create_all()

    # new_travel_plan = TravelPlan(travel_start_time="2022/09/26", travel_end_time="2023/09/26", travel_location="Columbia University", plan_completed=False)
    # db.session.add(new_travel_plan)
    # db.session.commit()


    app.run(debug=True)