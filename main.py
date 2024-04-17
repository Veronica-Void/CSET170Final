from flask import Flask, render_template, request, redirect, session, url_for   # imported flask
from sqlalchemy import create_engine, text
# from werkzeug.security import check_password_hash, generate_password_hash #research werkzeug
import hashlib

c_str = "mysql://root:MySQL8090@localhost/bank_app"
engine = create_engine(c_str, echo=True)
connection = engine.connect()
app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')

# ------------------------------------------------ Start of Register ------------------------------------------------------------
@app.route('/register', methods=['GET'])
def registerForm():
    return render_template('register.html')


def hashpw(inputpw):
    return hashlib.sha3_256(inputpw.encode())
    


@app.route('/register', methods=['POST'])
def registerUser():
    password = request.form.get('PW')
    ssn = request.form.get('SSN')
    hashedpw = hashpw(password).hexdigest()
    f_name = request.form.get('F_NAME')
    l_name = request.form.get('L_NAME')
    address = request.form.get('ADDRESS')
    phone = request.form.get('PHONE')
    username = request.form.get('USERNAME')
    connection.execute(text(f'INSERT INTO CUSTOMER (SSN, TYPE, F_NAME, L_NAME, USERNAME, PW, ADDRESS, PHONE, STATUS) VALUES (\'{ssn}\', "User", \'{f_name}\', \'{l_name}\', \'{username}\', \'{hashedpw}\', \'{address}\', \'{phone}\', "Pending")'))
    connection.commit()
    return redirect(url_for('showlogin'))


# ------------------------------------------------ End of Register ------------------------------------------------------------



# ------------------------------------------------ Start of Login ------------------------------------------------------------




@app.route('/login', methods=['GET'])
def showlogin():
    return render_template('login.html')

# function below determines the user and redirects them to the pages that they should see
@app.route('/login', methods=['POST', 'GET'])
def allowEntry():
    userInputUsername = request.form.get('USERNAME') 
    userInputPassword = request.form.get('PW')
    hashedUserInputPassword = hashpw(userInputPassword).hexdigest
    checkUserExists = connection.execute(text(f'SELECT * FROM CUSTOMER WHERE USERNAME = \'{userInputUsername}\'')).all()
    # checks if un and pw exists
    if len(checkUserExists) < 1: 
        session['loginError'] = 'Doesnt exist'
        return redirect(url_for('showlogin'))
    elif hashedUserInputPassword == len(checkUserExists): 
        # check if account is admin or user
        userType = checkUserExists[1]
        if userType == 'Admin':
            return redirect(url_for('showAdminHome'))
        else:
            # check if account status (pending or approved)
            userStatus = checkUserExists[-1]
            if userStatus == 'Approved':
                return redirect(url_for('displayAccount'))
            else:
                return redirect(url_for('showlogin'))
    return redirect(url_for('hello'))



# ------------------------------------------------ End of Login ------------------------------------------------------------





# ------------------------------------------------ Start of Customer ------------------------------------------------------------

# --- Start of Admin --

# autogenerate acc number upon approval

@app.route('/admin')
def showAdminHome():
    return render_template('admin.html')
# ---- End of Admin ---







# ------------------------------------------------ End of Customer ------------------------------------------------------------




# ------------------------------------------------ Start of Accounts ------------------------------------------------------------

# user can check bank account number and all their personal info on accounts page
# 


@app.route('/account')
def displayAccount():
    return render_template('account.html')

# grab user from session, check if admin. if not, redirect to where they should be.


# banking functionality

    # def banking():
    #     cardNum= 
    #     amt= 
 




# ------------------------------------------------ End of Accounts ------------------------------------------------------------



if __name__ == '__main__':
    app.run(debug=True)