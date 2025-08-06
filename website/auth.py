from flask import Blueprint,render_template,request,flash,redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, login_required, current_user


auth= Blueprint('auth',__name__)

#login page
@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email')
        password1=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password1):
                flash('Logged in successfully', category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='failed')
                return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist', category='failed')
            return redirect(url_for('auth.login'))
    return render_template("login.html",user=current_user)

#logout page
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#Signup page
@auth.route('/sign-up', methods=['GET','POST'])
def signup():
    if request.method =='POST':
        email=request.form.get("email")
        firstName=request.form.get("firstName")
        password1=request.form.get("password1")
        password2=request.form.get("password2")
        user=User.query.filter_by(email=email).first()
        if user:
            flash('Account already exists.', category='failed')
        elif len(email) < 5:
            flash("Email must be of length atleast 4.",category="failed")
        elif len(firstName) < 4:
            flash("First name must be of length atleast 3.",category="failed")
        elif password1 != password2:
            flash("The passwords do not match.",category="failed")
        elif len(password1) < 8:
            flash("The password must be of length atleast 7.",category="failed")
        else:
            new_user=User(email=email,firstName=firstName,password=generate_password_hash(password1,method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash("Successfully created account.",category="success")
           # login_user(user,remember=True)
            return redirect(url_for('views.home'))



    return render_template("signup.html",user=current_user)

#
