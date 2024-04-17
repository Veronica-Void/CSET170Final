from flask import Flask, render_template, request, redirect, session, url_for   # imported flask
from sqlalchemy import create_engine, text
# from werkzeug.security import check_password_hash, generate_password_hash #research werkzeug
import hashlib

app = Flask(__name__)
c_str = "mysql://root:MySQL8090@localhost/bank_app"
engine = create_engine(c_str, echo=True)
connection = engine.connect()
app.secret_key = 'WOMP'


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
    # takes out 'login error' value from the session and adds it to the 'var' variable
    if 'loginError' in session:
        var = session.pop('loginError')
    else:
        # setting an empty variable because you can't pass a null
        var = ""
    return render_template('login.html', loginError=var)

# function below determines the user and redirects them to the pages that they should see
@app.route('/login', methods=['POST'])
def allowEntry():
    userInputUsername = request.form.get('USERNAME') 
    userInputPassword = request.form.get('PW')
    hashedUserInputPassword = hashpw(userInputPassword).hexdigest
    checkUserExists = connection.execute(text(f'SELECT * FROM CUSTOMER WHERE USERNAME = \'{userInputUsername}\'')).all()
    print(checkUserExists)
    # checks if un and pw exists
    if len(checkUserExists) < 1: 
        session['loginError'] = 'Doesnt exist'
        return redirect(url_for('showlogin'))
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
        return redirect(url_for('showlogin'))
 



# ------------------------------------------------ End of Login ------------------------------------------------------------




# ------------------------------------------------ Start of Accounts ------------------------------------------------------------





























# ------------------------------------------------ End of Accounts ------------------------------------------------------------

# ------------------------------------------------ Start of Admin ------------------------------------------------------------







































# ------------------------------------------------ End of Admin ------------------------------------------------------------




if __name__ == '__main__':
    app.run(debug=True)