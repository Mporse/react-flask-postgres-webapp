# Import modules.
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
# NB: For "app.config", normally you'd do "postgresql://username:password@localhost/databaseName", but my postgres user does not
#     have a password associated with it, so I can skip that in our case.
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres@localhost/babytracker"
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(100), nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())

    def __repr__(self):
        return f"Event: {self.description}"
    
    def __init__(self, description):
        self.description = description

def format_event(event):
    return {
        "description": event.description,
        "id": event.id,
        "created_at": event.created_at
    }


# Root path of web app.
@app.route("/", methods = ["GET"])
def hello():
    return "Hey!"

# Create event (a.k.a. add data to our table).
@app.route("/events", methods = ["POST"])
def create_event():
    description = request.json["description"]
    event = Event(description)
    db.session.add(event)
    db.session.commit()

    return format_event(event)

# Get all events (all the data in the table).
@app.route("/events", methods = ["GET"])
def get_events():
    events = Event.query.order_by(Event.id.asc()).all()
    event_list = [format_event(event) for event in events]

    return {"events": event_list}

# Get a single event (based on id).
@app.route("/events/<id>", methods = ["GET"])
def get_event(id):
    event = Event.query.filter_by(id = id).one()
    formatted_event = format_event(event)
    
    return {"event": formatted_event}

# Update an event.
@app.route("/events/<id>", methods = ["PUT"])
def update_event(id):
    event = Event.query.filter_by(id = id)
    description = request.json["description"]
    event.update({"description": description, "created_at": datetime.utcnow()})
    db.session.commit()

    return {"event": format_event(event.one())}

# Delete an event.
@app.route("/events/<id>", methods = ["DELETE"])
def delete_event(id):
    event = Event.query.filter_by(id = id).one()
    db.session.delete(event)
    db.session.commit()

    return f"Event (id: {id}) deleted!"


if __name__ == "__main__":
    app.run()
