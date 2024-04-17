from flask import Flask, render_template, request, redirect, session, url_for  # imported flask
from sqlalchemy import create_engine, text

c_str = "mysql://root:MySQL@localhost/BANK_APP2"
engine = create_engine(c_str, echo=True)
connection = engine.connect()
app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')


# @app.route("/login")
# def login():
#     return render_template('login.html')


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
        text(f'SELECT * FROM CUSTOMER WHERE TYPE = "User" AND SSN = (:SSN) OR STATUS = (:STATUS)'), request.form)
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

# @app.route("/AdminAcc/<SSN>", methods=['GET'])
# def displayAcc(SSN):
#     getUserInfo = connection.execute(text(f"SELECT * FROM ACCOUNT WHERE SSN = {SSN}")).all()
#     print(getUserInfo)
#     return render_template('AdminAcc.html', AdminAcc=getUserInfo)




if __name__ == '__main__':
    app.run(debug=True)
