from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.exceptions import ClientError
import logging
from datetime import datetime

# user = 'root'
# password = 'dbuserdbuser'
# port = '3306'
# host = 'localhost'
# db_name = '6156_travel_plan'
user = 'admin'
password = 'dbuserdbuser'
port = '3306'
host = 'e61561.cc790x5jaujy.us-east-1.rds.amazonaws.com'
db_name = '6156_travel_plan'

AWS_REGION = 'us-east-1'

# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

sns_client = boto3.client('sns', region_name=AWS_REGION)

app = Flask(__name__)
print('mysql+pymysql://%s:%s@%s:%s/%s'%(user, password, host, port, db_name))
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s:%s/%s'%(user, password, host, port, db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.app_context().push()
# conn = None

class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    travel_start_time = db.Column(db.String(100))
    travel_end_time = db.Column(db.String(100))
    travel_location = db.Column(db.String(100))
    plan_completed = db.Column(db.Boolean)

def add_permission(topic_arn, policy_label, account_ids, action_names):
    """
    Adds a policy statement to a topic's access control policy.
    """
    try:

        response = sns_client.add_permission(TopicArn=topic_arn,
                                             Label=policy_label,
                                             AWSAccountId=account_ids,
                                             ActionName=action_names)

    except ClientError:
        logger.exception(f'Could not add access policy to the topic.')
        raise
    else:
        return response

def publish_to_topic(action, detail):
    topic_arn = 'arn:aws:sns:us-east-1:669138289295:travel_sns'
    policy_label = 'policy-y'
    account_ids = ['583295611253']
    action_names = ['Publish', 'GetTopicAttributes']
    add_permission(topic_arn, policy_label, account_ids, action_names)

    sns = boto3.resource("sns", region_name='us-east-1')
    topic = sns.Topic(arn=topic_arn)
    message = "{\"AlarmName\":\"6156_travel_plan\",\"NewStateValue\":\"%s\",\"NewStateReason\":\"%s\"}"%(action, detail)
    response = topic.publish(Message=message)

    message_id = response['MessageId']


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
    publish_to_topic("insertion", "%s: %s to %s" %(loc, start, end))
    return redirect(url_for("main_page"))

@app.route("/update/<int:plan_id>")
def update(plan_id):
    # add new travel plan 
    target_plan = TravelPlan.query.filter_by(id=plan_id).first()
    target_plan.plan_completed = not target_plan.plan_completed
    db.session.commit()
    publish_to_topic("update", " %s: %s to %s" % (target_plan.travel_location, target_plan.travel_start_time, target_plan.travel_end_time))
    return redirect(url_for("main_page"))

@app.route("/delete/<int:plan_id>")
def delete(plan_id):
    # add new travel plan 
    target_plan = TravelPlan.query.filter_by(id=plan_id).first()
    db.session.delete(target_plan)
    db.session.commit()
    return redirect(url_for("main_page"))

if __name__ == "__main__":
    #db.drop_all()
    db.create_all()

    # new_travel_plan = TravelPlan(travel_start_time="2022/09/26", travel_end_time="2023/09/26", travel_location="Columbia University", plan_completed=False)
    # db.session.add(new_travel_plan)
    # db.session.commit()

    app.run(debug=True)