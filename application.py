# import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask import request, redirect
from werkzeug import security
# create the Flask app
from flask import flash
from flask import Flask, render_template
from flask_login import LoginManager, login_user, current_user, logout_user
from sqlalchemy import text
from markupsafe import escape
from datetime import date
from flask import jsonify 
import json
application = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(application)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# select the database filename
application.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///todo.sqlite'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.secret_key = 'helloworld'
# set up a 'model' for the data you want to store
from db_schema import db, User, HouseHoldUser, HouseHold, Bill, BillItem, dbinit

# init the database so it can connect with our app
db.init_app(application)

# change this to False to avoid resetting the database every time this app is restarted
resetdb = False
if resetdb:
    with application.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()

#route to the index
@application.route('/',  methods=['POST', 'GET'])
def index():
    #If the user is logged in, open the dashboard
    if current_user.is_authenticated:
        return redirect('dashboard.html')
    else:
        #If the user is not logged in, open the login page
        return render_template('login.html')

#Method to add a user to the database
@application.route('/addUser', methods=['POST', 'GET'])
def addUser():
    #Checks if the user is logged in
    if current_user.is_authenticated:
        return "logged in already"
    #If a post request
    if request.method=="POST":
        #Fetches the field details
        userName = escape(request.form['name'])
        email = escape(request.form['email'])
        password = escape(request.form['password'])
        repassword = escape(request.form['repassword'])
        #If both passwords entered match
        if password==repassword:
            #Generate hash
            hashed = security.generate_password_hash(password)
            try:
                ##Attempts to add user
                db.session.add(User(userName,email, hashed))
                db.session.commit()
            except:
                #Fails if the same email is already used
                return jsonify({"message": "Email already registered, please enter a different email"})
            #Returns back to login page
            return jsonify({"redirect": "/"})
        else:
            #Message that passwords do not match
            return "Passwords do not match"
    #If get request
    if request.method=="GET":
        #Display the register form
        return render_template("register.html")

#Route for the register form
@application.route('/register.html', methods=['POST', 'GET'])
def register():
    #Renders the register page
    return render_template('register.html')


#Checks whether the login details are a match to a record in the database
@application.route('/loginCheck', methods=['POST'])
def loginCheck():
    #Retrieves the necessary details
    email=escape(request.form['email'])
    password=escape(request.form['password'])
    user = User.query.filter_by(email=email).first()
    #If user cannot be found with email
    if user is None:
        return jsonify({"login": "fail"})
    #Checks if the hash matches the entered password hash 
    if not security.check_password_hash(user.password, password):
        return jsonify({"login": "fail"})
    login_user(user) #Logs the user in
    return jsonify({"login": "pass"})



#Renders the search page to allow the user to search for bills
@application.route('/search.html',methods=['GET'])
def search():
    return render_template("search.html")

#Handles the search query by retrieving bills with the substring as the entered search term
@application.route('/searchQuery', methods=['POST'])
def searchQuery():
    #Retrieves the search term from the form 
    searchItem = escape(request.form['searchTerm'])
    #Retrieves all the bills containing the search term as a substring
    bills = Bill.query.filter(Bill.name.contains(searchItem)).all()
    searchBillList = []
    #Adds bills that are only related to the current user
    for bill in bills:
        try:
            searchBillList.append(BillItem.query.filter_by(bill_id=bill.id, user_id=current_user.id).one())
        except:
            pass
    billPayTo = []
    billList = []
    billAmount = []
    #Retrieves the information about each bill
    for bill in searchBillList:
        paytoid = Bill.query.filter_by(id=bill.bill_id).first().payto
        billAmount.append(BillItem.query.filter_by(bill_id=bill.bill_id).first().amount)
        billPayTo.append((User.query.filter_by(id=paytoid)).first().name)
        currentBill = Bill.query.filter_by(id=bill.bill_id).first()
        billList.append(currentBill)
    #Renders the search page again, this time with the data to enter into the form as resutls 
    return render_template("search.html",billPayTo = billPayTo, billAmount = billAmount, billList = billList)


#Page to view the household        
@application.route('/viewhh.html')
def viewhh():
    #Checks if the user is logged in
    if current_user.is_authenticated:
        houseHoldname = ""
        #Retrieves the household of the current user
        houseHold = HouseHoldUser.query.filter_by(user_id=current_user.id).first()
        #If user is not currently in a household 
        if houseHold is None:
            return render_template('viewhh.html', name=houseHoldname)
        else:
            #If user is in a household, retrieve information
            householdid = houseHold.household_id
            houseHoldname = HouseHold.query.filter_by(id=householdid).first().name
            houseMates = HouseHoldUser.query.filter_by(household_id=householdid).all()
            housemateDetails = []
            #Gets housemate details
            for housemate in houseMates:
                housemateDetails.append(User.query.filter_by(id=housemate.user_id).first())
            return render_template('viewhh.html', name=houseHoldname, houseMates=housemateDetails)
    return render_template('viewhh.html')

#Route for creating a household
@application.route('/createhh.html')
def createhh():
    return render_template('createhh.html')

#Route for adding a bill to the household
@application.route('/addbill.html', methods=['GET','POST'])
def addbill():    
    if request.method =='GET':
        if current_user.is_authenticated:
            #If user is logged in and get request
            houseHoldname = ""
            houseHold = HouseHoldUser.query.filter_by(user_id=current_user.id).first()
        #If there are no household members
        if houseHold is None:
            return render_template('viewhh.html', name=houseHoldname)
        else:
            #If household does exist, gets the corresponding details
            householdid = houseHold.household_id
            houseHoldname = HouseHold.query.filter_by(id=householdid).first().name
            houseMates = HouseHoldUser.query.filter_by(household_id=householdid).all()
            housemateDetails = []
            #Iterates over each housemate
            for housemate in houseMates:
                print(housemate.user_id)
                if housemate.user_id!=current_user.id:
                    housemateDetails.append(User.query.filter_by(id=housemate.user_id).first())
            #Renders the addbill template
            return render_template('addbill.html', householdId = houseHold.household_id, houseMates=housemateDetails)
    else:
        #If post request, retrieves the necessary details
        today = date.today()
        todayDate = today.strftime("%d/%m/%Y")
        name = escape(request.form['name'])
        description = escape(request.form['description'])
        category = escape(request.form['category'])
        householdId = escape(request.form['householdId'])

        housemateid = request.form.getlist('housemateid[]')
        amount = request.form.getlist('amount[]')
       
        #Adds the bill to Bill table
        billId = Bill(name, todayDate, description, category, current_user.id)
        db.session.add(billId)
        db.session.flush()
        db.session.refresh(billId)

        #Adds the billItems to the BillItem table
        for i in range(0,len(housemateid)):
            if float(amount[i])>0:
                print(housemateid[i])
                db.session.add(BillItem(housemateid[i], "", billId.id, float(amount[i]), "pending", "False"))
                db.session.commit()
    return redirect("dashboard.html")

#Route for adding a household 
@application.route('/addHh', methods=['POST'])
def addHh():
    #Gets the name of the household
    name=escape(request.form['name'])
    #Adds the name of the household and current user id to the Household table
    householdId = HouseHold(name)
    db.session.add(householdId)
    db.session.flush()
    db.session.refresh(householdId)
    db.session.add(HouseHoldUser(current_user.id, householdId.id))
    db.session.commit()
    return redirect('viewhh.html')

#Route for adding a user to a household
@application.route('/addUserHh', methods=['POST'])
def addUserHh():
    #Retrieves the email address of the user to be added
    email=escape(request.form['email'])
    currentHouseholdId = HouseHoldUser.query.filter_by(user_id=current_user.id).first().household_id
    #Checks if the user already exists in the database
    user = User.query.filter_by(email=email).first()
    #If not user is found
    if user is None:
        #Displays message informing that a user was not found 
        return jsonify({"Message": "User with this email does not exist", "Name":"wron"})
    else:
        #If a user does exist for the entered email
        #Retrieves the household id of the current user
        household = HouseHoldUser.query.filter_by(user_id=user.id).first()
        #If the user is not currently in a household
        if household is None:
            #Adds the current user to the household
            db.session.add(HouseHoldUser(user.id, currentHouseholdId))
            db.session.commit()
            return jsonify({"Message": "True", "Name":user.name})
        else: #If the user is currently in a household
            print(household.user_id)
            return jsonify({"Message": "User has already been added to a household", "Name":"wron"})



#Route for the addBill form
@application.route('/addbillform.html')
def addbillform():
    return render_template('addbillform.html')

#Method to update the status of bills to pending payment or delete
@application.route('/updateStatusToPp', methods=['POST'])
def updateStatusToPp():
    #If the pay button is clicked
    if request.form.get("pay"):
        #Adds the date paid and changes the status to pending approval
        today = date.today()
        todayDate = today.strftime("%d/%m/%Y")
        billId = escape(request.form['billId1'])
        billItem = db.session.query(BillItem).filter(BillItem.id==billId).one()
        billItem.status = "pending approval"
        billItem.date_paid = todayDate
        db.session.commit()
    elif request.form.get("delete"):
        #If the delete button is clicked
        billId = escape(request.form['billId1'])
        #Removes the corresponding bill from the database
        BillItem.query.filter(BillItem.id==billId).delete()
        db.session.commit()
        return redirect('managebillreceive.html')
    return redirect('managebillpay.html')

#Method to change the status to pending approval
@application.route('/updatePp', methods=['POST'])
def updatePp():
    today = date.today()
    todayDate = today.strftime("%d/%m/%Y")
    billId = escape(request.form['id'])
    billItem = db.session.query(BillItem).filter(BillItem.id==billId).one()
    billItem.status = "pending approval"
    billItem.date_paid = todayDate
    db.session.commit()
    return "added"
    return redirect('managebillpay.html')

#Method to update status to paid or reject
@application.route('/updateStatusToP', methods=['POST'])
def updateStatusToP():
    #If the disapprove button is clicked
    if request.form.get("disapprove"):
        billId = escape(request.form['billId1'])
        billItem = db.session.query(BillItem).filter(BillItem.id==billId).one()
        billItem.status = "pending"
        db.session.commit()
        #If the approve button is clicked
    elif request.form.get("approve"):
        billId = escape(request.form['billId1'])
        billItem = db.session.query(BillItem).filter(BillItem.id==billId).one()
        billItem.status = "completed"
        db.session.commit()
    return redirect('managebillreceive.html')

#Route for the dashboard
@application.route('/dashboard.html', methods=['GET'])
def dashboard():
    #If the user is logged in
    if current_user.is_authenticated:
        #Gets details about bills that need to be paid by current user
        #Gets details about total outstanding oending bills
        outstandingTotal = 0
        billOutstandingItems = BillItem.query.filter_by(user_id=current_user.id, status="pending").all()
        for bill in billOutstandingItems:
            outstandingTotal+=bill.amount
        
        #Gets details about total pending approval bills
        waitingTotal = 0
        billWaitingItems = BillItem.query.filter_by(user_id=current_user.id, status="pending approval").all()
        for bill in billWaitingItems:
            waitingTotal+=bill.amount
        
        #Gets details of all completed bills
        completedTotal = 0
        billCompletedItems = BillItem.query.filter_by(user_id=current_user.id, status="completed").all()
        for bill in billCompletedItems:
            completedTotal+=bill.amount

        #Gets details about bills that need to be paid to the current user
        #Gets details about pending bills
        poutstandingTotal = 0
        pbillOutstandingList = []
        billId = Bill.query.filter_by(payto=current_user.id)
        poutstandingTotal = 0
        for bill in billId:
            billItem = BillItem.query.filter_by(bill_id=bill.id, status="pending").all()
            for billitem in billItem:
                pbillOutstandingList.append(billitem)
                poutstandingTotal += billitem.amount

        #Gets details about pending approval bills
        pwaitingTotal = 0
        pbillWaitingList = []
        billId = Bill.query.filter_by(payto=current_user.id)
        for bill in billId:
            billItem = BillItem.query.filter_by(bill_id=bill.id, status="pending approval").all()
            for billitem in billItem:
                pbillWaitingList.append(billitem)
                pwaitingTotal += billitem.amount

        #Gets details about completed bills 
        pcompletedTotal = 0
        pbillCompletedList = []
        billId = Bill.query.filter_by(payto=current_user.id)
        for bill in billId:
            billItem = BillItem.query.filter_by(bill_id=bill.id, status="completed").all()
            for billitem in billItem:
                pbillCompletedList.append(billitem)
                pcompletedTotal += billitem.amount
        
        #Gets details about newly added bills to flash notify the user
        newBills = 0
        print(current_user.id)
        billNew = BillItem.query.filter_by(user_id=current_user.id).all()
        for bill in billNew:
            print(bill.seen)
            if bill.seen=="False":
                bill.seen = "True"
                db.session.commit()
                newBills+=1
        try:
            #Retrieves information for the pie chart displays
            houseHoldid = (HouseHoldUser.query.filter_by(user_id=current_user.id).first()).household_id
            houseMates = (HouseHoldUser.query.filter_by(household_id=houseHoldid).all())
            billBreakdown = [["Groceries",0],["Utilities",0],["Rent",0],["Going out",0],["Takeaways",0], ["Other",0]]
            #Forms a 2D array of household expenses by category
            for houseMate in houseMates:
                currentUserId = houseMate.user_id
                currentBills = (Bill.query.filter_by(payto=currentUserId).all())
                for currentBill in currentBills:
                    currentCategory = currentBill.category
                    currentBillId = currentBill.id
                    currentBillItems = (BillItem.query.filter_by(bill_id=currentBillId).all())
                    index = 0
                    if currentCategory=="grocery":
                        index=0
                    elif currentCategory=="utilities":
                        index=1
                    elif currentCategory=="rent":
                        index=2
                    elif currentCategory=="goingout":
                        index=3
                    elif currentCategory=="takeaway":
                        index=4
                    elif currentCategory=="other":
                        index=5
                    for currentBillItem in currentBillItems:
                        billBreakdown[index][1] = billBreakdown[index][1] + currentBillItem.amount
            billBreakdownUser = []
            householdTotal = 0
            #forms a 2D array of household expenses by each household member
            for houseMate in houseMates:
                currentUserId = houseMate.user_id
                currentUserName = (User.query.filter_by(id=currentUserId).one()).name
                allBillsUser = (BillItem.query.filter_by(user_id=currentUserId).all())
                total = 0
                for bill in allBillsUser:
                    total+=bill.amount
                    householdTotal +=bill.amount
                billBreakdownUser.append([currentUserName,total])

        except:
            #If there was an error, means that the household did not exist, so returns an error page
            return render_template('dashboarde.html')
    if householdTotal==0:
        return render_template('dashboarde.html')
    userName = (User.query.filter_by(id=current_user.id).one()).name
    print("newbills")
    print(newBills)
    return render_template('dashboard.html',name=userName, billBreakdownUser= billBreakdownUser, billBreakdown=billBreakdown, pbillCompleted=len(pbillCompletedList),pbillCompletedTotal=pcompletedTotal,pbillWaitingTotal=pwaitingTotal, pbillWaiting=len(pbillWaitingList), pbillOutstandingTotal=poutstandingTotal, pbillOutstanding=len(pbillOutstandingList),billCompleted = len(billCompletedItems), billCompletedTotal = completedTotal, billWaiting = len(billWaitingItems), billWaitingTotal=waitingTotal, billOutstanding=len(billOutstandingItems), billOutstandingTotal = outstandingTotal, newBills=newBills) 

#Route to manage bills that need to be paid by the user
@application.route('/managebillpay.html')
def managebill():
    if request.method =='GET':
        if current_user.is_authenticated:
            #Retrieves the bills that are pending
            houseHoldname = ""
            billListItems = BillItem.query.filter_by(user_id=current_user.id, status="pending").all()
            billPayTo = []
            billList = []
            billAmount = []

            for bill in billListItems:
                paytoid = Bill.query.filter_by(id=bill.bill_id).first().payto
                billPayTo.append((User.query.filter_by(id=paytoid)).first().name)
                currentBill = Bill.query.filter_by(id=bill.bill_id).first()
                billList.append(currentBill)
            
            #Retrieves bills that are pending approval
            billPendingApproval = BillItem.query.filter_by(user_id=current_user.id,status="pending approval").all()
            billPendingApprovalList = []
            billPendingBillData = []
            billPendingUserList = []
            print(billPendingApproval)
            
            for bill in billPendingApproval:
                
                billItem = BillItem.query.filter_by(bill_id=bill.bill_id, status="pending approval").first()
                print(billItem)
                if billItem != None:
                    billData = Bill.query.filter_by(id=billItem.bill_id).first()
                    billPendingBillData.append(billData)
                    billPendingUser = User.query.filter_by(id=billData.payto).first().name
                    billPendingApprovalList.append(billItem)
                    billPendingUserList.append(billPendingUser)

            #Retrieves the bills that have been completed
            billCompleted = BillItem.query.filter_by(user_id=current_user.id,status="completed").all()
            billCompletedBillList = []
            billCompletedBillData = []
            billCompletedUserList = []
            
            for bill in billCompleted:
                
                billItem = bill
                if billItem != None:
                    billData = Bill.query.filter_by(id=billItem.bill_id).first()
                    billCompletedBillData.append(billData)
                    billCompletedUser = User.query.filter_by(id=billData.payto).first().name
                    billCompletedBillList.append(billItem)
                    billCompletedUserList.append(billCompletedUser)
            
            return render_template('managebillpay.html', billCompletedUser = billCompletedUserList ,billCompletedData=billCompletedBillData  ,billCompletedList=billCompletedBillList, billPendingData = billPendingBillData, billPendingUser = billPendingUserList, billPending = billPendingApprovalList, billListItems = billListItems, billList = billList, billPayTo=billPayTo)
         
#Route to manage bills that need to be paid to the user
@application.route('/managebillreceive.html')
def managebillpay():
    if request.method =='GET':
        if current_user.is_authenticated:
            #Retrieves bills that are pending
            houseHoldname = ""
            billPending = Bill.query.filter_by(payto = current_user.id).all()
            billPendingList = []
            billPendingListItem = []
            billPendingNameList = []
            for bill in billPending:
                billItem = BillItem.query.filter_by(bill_id=bill.id).all()
                for billitem in billItem:
                    if billitem.status=="pending":
                        billPendingList.append(bill)
                        billPendingListItem.append(billitem)
                        billPendingUser = User.query.filter_by(id=billitem.user_id).first().name
                        billPendingNameList.append(billPendingUser)
            #Retrieves bills that are pending approval
            billPendingApproval = Bill.query.filter_by(payto = current_user.id).all()
            billPendingApprovalList = []
            billPendingApprovalListItem = []
            billPendingApprovalUser = []
            for bill in billPending:
                billItem = BillItem.query.filter_by(bill_id=bill.id).all()
                for billitem in billItem:
                    if billitem.status=="pending approval":
                        billPendingApprovalList.append(bill)
                        billPendingApprovalListItem.append(billitem)
                        billPendingUser = User.query.filter_by(id=billitem.user_id).first().name
                        billPendingApprovalUser.append(billPendingUser)
            #Retrieves bills that are completed
            billCompleted = Bill.query.filter_by(payto = current_user.id).all()
            billCompletedList = []
            billCompletedListItem = []
            billCompletedUser = []
            for bill in billPending:
                billItem = BillItem.query.filter_by(bill_id=bill.id).all()
                for billitem in billItem:
                    if billitem.status=="completed":
                        billCompletedList.append(bill)
                        billCompletedListItem.append(billitem)
                        billPendingUser = User.query.filter_by(id=billitem.user_id).first().name
                        billCompletedUser.append(billPendingUser)
                
            return render_template('managebillreceive.html',billCompletedUser=billCompletedUser, billCompletedListItem=billCompletedListItem, billCompletedList=billCompletedList, billPendingApprovalUser=billPendingApprovalUser, billPendingApprovalListItem=billPendingApprovalListItem, billPendingApprovalList=billPendingApprovalList, billPendingListItem=billPendingListItem, billPendingList=billPendingList, billPendingNameList=billPendingNameList )

#Route for logging out of the website
@application.route('/logout')
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    application.run()