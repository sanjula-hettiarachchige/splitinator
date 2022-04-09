from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
# create the database interface
db = SQLAlchemy()

# a model of a user for the database
class User(db.Model, UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False)
    email = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20), unique=False)
    def __init__(self, name, email, password):  
        self.name=name
        self.email=email
        self.password=password

    def get_id(self):
        return self.id

# a model of a list for the database
# it refers to a user
class HouseHoldUser(db.Model):
    __tablename__='householdUser'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    household_id = db.Column(db.Integer) 

    def __init__(self, user_id, household_id):
        self.user_id = user_id
        self.household_id = household_id

# a model of a list for the database
# it refers to a user
class HouseHold(db.Model):
    __tablename__='household'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, name):
        self.name=name



# a model of a list item for the database
# it refers to a list
class Bill(db.Model):
    __tablename__='bill'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Text)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    category = db.Column(db.Text)
    payto = db.Column(db.Text)
    

    def __init__(self, name, date, description, category, payto):
        self.name=name
        self.date = date
        self.description=description
        self.category = category
        self.payto = payto

class BillItem(db.Model):
    __tablename__='billItem'
    id = db.Column(db.Integer, primary_key=True)
    date_paid = db.Column(db.Text)
    user_id = db.Column(db.Integer)
    bill_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    status = db.Column(db.Text)
    seen = db.Column(db.Text)
    
    

    def __init__(self, user_id, date_paid, bill_id, amount, status, seen):
        self.user_id = user_id
        self.date_paid = date_paid
        self.bill_id = bill_id
        self.amount = amount
        self.status = status
        self.seen = seen

# put some data into the tables
def dbinit():
    user_list = [
        User("Felicia","u@mail.com","helloworld"), 
        User("Petra","f@mail.com", "helloworld")
        ]
    db.session.add_all(user_list)
    db.session.commit()
    # # find the id of the user Felicia
    # felicia_id = User.query.filter_by(username="Felicia").first().id

    # all_lists = [
    #     List("Shopping",felicia_id,"Household"), 
    #     List("Chores",felicia_id, "Household")
    #     ]
    # db.session.add_all(all_lists)

    # # find the ids of the lists Chores and Shopping

    # chores_id = List.query.filter_by(name="Chores").first().id
    # shopping_id= List.query.filter_by(name="Shopping").first().id

    # all_items = [
    #     ListItem("Potatoes",shopping_id,1,"04/02/2022"), 
    #     ListItem("Shampoo", shopping_id,0,"04/02/2022"),
    #     ListItem("Wash up",chores_id,1,"04/02/2022"), 
    #     ListItem("Vacuum bedroom",chores_id,1, "04/02/2022")
    # ]
    # db.session.add_all(all_items)

    # # commit all the changes to the database file
    # db.session.commit()
