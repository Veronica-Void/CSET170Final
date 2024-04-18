from flask import Flask, render_template, request, redirect, session, url_for   # imported flask
from sqlalchemy import create_engine, text
import hashlib

app = Flask(__name__)
c_str = "mysql://root:MySQL@localhost/BANK_APP"
engine = create_engine(c_str, echo=True)
connection = engine.connect()
app.secret_key = 'WOMP'

@app.route('/')
def hello():
    return render_template('index.html')

# ------------------------------------------------ Start of Register ------------------------------------------------------------

# this page just displays the html for registering
@app.route('/register', methods=['GET'])
def registerForm():
    return render_template('register.html')

# this function is used in registerUser() to hash the user input password
def hashpw(inputpw):
    return hashlib.sha3_256(inputpw.encode())
    


@app.route('/register', methods=['POST'])
# register function
def registerUser():
    # grabs all of the inputs from the form 
    password = request.form.get('PW')
    ssn = request.form.get('SSN')
        # hashes the password from the user input, hashed password is then put into the database for later use.
    hashedpw = hashpw(password).hexdigest()
    f_name = request.form.get('F_NAME')
    l_name = request.form.get('L_NAME')
    address = request.form.get('ADDRESS')
    phone = request.form.get('PHONE')
    username = request.form.get('USERNAME')
    # adds those inputs to the database using the insert into statement
    connection.execute(text(f'INSERT INTO CUSTOMER (SSN, TYPE, F_NAME, L_NAME, USERNAME, PW, ADDRESS, PHONE, STATUS) VALUES (\'{ssn}\', "User", \'{f_name}\', \'{l_name}\', \'{username}\', \'{hashedpw}\', \'{address}\', \'{phone}\', "Pending")'))
    connection.commit()
    return redirect(url_for('showlogin'))


# ------------------------------------------------ End of Register ------------------------------------------------------------



# ------------------------------------------------ Start of Login ------------------------------------------------------------




@app.route('/login', methods=['GET'])
# loging function
def showlogin():
    # takes out 'login error' value out from the session and adds it to the 'var' variable
    if 'loginError' in session:
        var = session.pop('loginError')
    else:
        # setting an empty variable because you can't pass a null
        var = ""
        # displays the login html
    return render_template('login.html', loginError=var)


# function below determines the user and redirects them to the pages that they should see
@app.route('/login', methods=['POST'])
# function that allows the user logging in to see specific pages
def allowEntry():
    # grabs all of the inputs from the  login form 
    userInputUsername = request.form.get('USERNAME') 
    userInputPassword = request.form.get('PW')
    userInputSSN = request.form.get('SSN')
    # hashes the password from the user input to be compared with the hashed pw that is already in the database.
    hashedUserInputPassword = hashpw(userInputPassword).hexdigest
    # a variable is set for the select statement. It grabs all of the information for a specific user that is already registered so that the info can be checked in the later if/else satements.
    checkUserExists = connection.execute(text(f'SELECT * FROM CUSTOMER WHERE USERNAME = \'{userInputUsername}\'')).all()
    print(checkUserExists)
    # checks if un and pw exists
    if len(checkUserExists) < 1: 
        session['loginError'] = 'USER DOES NOT EXIST, PLEASE REGISTER.'
        return redirect(url_for('showlogin'))
    # checking if user is admin, if so then go to admin page
    if userInputPassword == 'Admin01!':
        return redirect(url_for('showAdminHome'))
    if hashedUserInputPassword == checkUserExists[0][5]: 
        # check if account is approved, if not go back to login
        userStatus = checkUserExists[0][-1]
        if userStatus == 'Approved':
            return redirect(url_for('showAccount'))
        else:
            return redirect(url_for('showlogin'))
    else:
        print('no')
        return redirect(url_for('showlogin')) 
 



# ------------------------------------------------ End of Login ------------------------------------------------------------






# ------------------------------------------------ Start of Accounts ------------------------------------------------------------





@app.route('/account', methods=['GET'])
def showAccount():
    allAccounts = connection.execute(text(f'SELECT * FROM CUSTOMER NATURAL JOIN ACCOUNT WHERE TYPE = "User"')).all()
    print(allAccounts)
    connection.commit()
    return render_template('account.html', account=allAccounts)


@app.route("/userAccount/<SSN>", methods=['GET'])
def particularAcc(SSN):
    get_partAcc = connection.execute(text(f"SELECT * FROM CUSTOMER NATURAL JOIN ACCOUNT WHERE SSN = {SSN}")).all()
    print(get_partAcc)
    return render_template('userAccount.html', userAccount=get_partAcc)

@app.route("/userAccountAdd/<ACC_NUM>", methods=['POST', 'GET'])
def addingtoAccount(ACC_NUM):
    accountAdd = connection.execute(text(f"SELECT * FROM CUSTOMER NATURAL JOIN ACCOUNT WHERE ACC_NUM = {ACC_NUM}")).all()
    if request.method == "POST":
        addingToBalance = connection.execute(text(f"UPDATE ACCOUNT SET BALANCE = BALANCE + (:ADDING) WHERE ACC_NUM = {ACC_NUM}"), request.form)
        accountAdd = connection.execute(text(f"SELECT * FROM CUSTOMER NATURAL JOIN ACCOUNT WHERE ACC_NUM = {ACC_NUM}")).all()
        print(addingToBalance)
        return render_template('userAccountAdd.html', userAccountAdd=accountAdd, balance=accountAdd[0][10])
    print(accountAdd)
    return render_template('userAccountAdd.html', userAccountAdd=accountAdd, balance=accountAdd[0][10])


@app.route("/transfer/<ACC_NUM>", methods=['POST', 'GET'])
def subtractFromAccount(ACC_NUM):
    accountTransfer = connection.execute(text(f"SELECT * FROM CUSTOMER NATURAL JOIN ACCOUNT WHERE ACC_NUM = {ACC_NUM}")).all()
    if request.method == "POST":
        subtract = request.form.get('SUBTRACT')
        if int(subtract) > accountTransfer[0][10]:
            raise ValueError("Insufficient funds!")
        else:
            subtractToBalance = connection.execute(text(f"UPDATE ACCOUNT SET BALANCE = BALANCE - (:SUBTRACT) WHERE ACC_NUM = {ACC_NUM}"), request.form)
            addingToOtherAcc = connection.execute(text(f"UPDATE ACCOUNT SET BALANCE = BALANCE + (:SUBTRACT) WHERE ACC_NUM = (:toACC)"), request.form)
            accountTransfer = connection.execute(text(f"SELECT * FROM CUSTOMER NATURAL JOIN ACCOUNT WHERE ACC_NUM = {ACC_NUM}")).all()
            print(subtractToBalance)
            print(addingToOtherAcc)
            print(accountTransfer)
        return render_template('transfer.html', transfer=accountTransfer, balance=accountTransfer[0][10])
    return render_template('transfer.html', transfer=accountTransfer, balance=accountTransfer[0][10])


# ------------------------------------------------ End of Accounts ------------------------------------------------------------


# ------------------------------------------------ Start of Admin ------------------------------------------------------------

@app.route('/admin', methods=['GET'])
def showAdminHome():
    allUsers = connection.execute(text(f'SELECT * FROM CUSTOMER WHERE TYPE = "User"')).all()
    print(allUsers)
    connection.commit()
    return render_template('admin.html', admin=allUsers)


@app.route('/admin', methods=['GET'])
def displayUsers():
    return render_template('admin.html')


@app.route('/admin', methods=['POST'])
def sUsers():  # table
    searchUsers = connection.execute(
        text(f'SELECT * FROM CUSTOMER WHERE TYPE = "User", SSN = (:SSN) OR STATUS = (:STATUS)'), request.form)
    connection.commit()
    return render_template('admin.html', admin=searchUsers)


@app.route("/AdminAcc/<SSN>", methods=['GET'])
def particularUSER(SSN):
    get_partUser = connection.execute(text(f"SELECT * FROM CUSTOMER WHERE SSN = {SSN} ")).all()
    getUserInfo = connection.execute(text(f"SELECT * FROM ACCOUNT WHERE SSN = {SSN}")).all()
    print(get_partUser)
    print(getUserInfo)
    if getUserInfo == 0:  # if SSN is not in account, skip to the next route
        return render_template('AdminAcc.html', AdminAcc=get_partUser)
    else:  # if it is in account print the account info for customer
        return render_template('AdminAcc.html', userInfo=getUserInfo, AdminAcc=get_partUser)


@app.route('/AdminAcc/<SSN>', methods=['POST', 'GET'])  # HOW TO HANDLE DUPLICATES????? only allow one submission of form!
def update_account(SSN):
    updateStatus = connection.execute(text(f"UPDATE CUSTOMER SET STATUS = (:STATUS) WHERE SSN = {SSN}"), request.form)
    makeAccount = connection.execute(text(f"INSERT INTO ACCOUNT (SSN) SELECT {SSN} FROM CUSTOMER WHERE SSN = {SSN}"))
    print(updateStatus)
    print(makeAccount)
    # print(getUserInfo)
    connection.commit()
    return redirect(f'/AdminAcc/{SSN}')

#------------------------------------------------------- Admin END-------------------------------------------------------------



if __name__ == '__main__':
    app.run(debug=True)
