from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, EmailField, validators
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.local import LocalProxy
from functools import wraps
import os

#db = LocalProxy(get_db)

def create_app(test_config = None):
    #__name__ là tên của module Python hiện tại. Ứng dụng cần biết nơi
    #mà nó được xác định nằm ở đâu để thiết lập một số path, và __name__
    #là một cách thuận tiện để nói với nó
    #instance_relative_config=True cho app biết rằng config file
    #và các thành phần liên quan nằm trong Folder [instance] được
    #đặt phía ngoài folder [flaskr] để chứa app này
    app = Flask(__name__, instance_relative_config=True)
    
    #Thiết lập mặc định mà app sẽ dùng
    app.config.from_mapping(
        SECRET_KEY = 'dev'
        DATABASE = os.path.join(app.instance_path,'flaskr.sqlite')
    )
    
    if test_config = None:
        #Load app config, nếu có, khi không testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #Load app config từ test_config khi testing
        app.config.from_mapping(test_config)

    #Đảm bảo rằng folder instance đã được tạo        
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    #Index
    @app.route('/')
    def index():
        return render_template('home.html')

    #About
    @app.route('/about')
    def about():
        return render_template('about.html')

    #Login
    #from . import auth
    #app.register_blueprint(auth.bp)

    #Register Form Class
    class RegisterForm(Form):
        name = StringField('Name',[
            validators.Length(min=1, max= 50),
            validators.DataRequired("Hãy nhập tên của bạn!")
        ])

        username = StringField('Username',[
            validators.Length(min=4,max=25),
            validators.DataRequired("Hãy nhập Username!")
        ])

        email = EmailField('Email',[
            validators.Length(min=6,max=50),
            validators.Required("Hãy nhập email của bạn!"),
            validators.Email()
        ])

        password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords do not match'),
            validators.Email()
        ])
        confirm = PasswordField('Confirm Password')

    #User Register
    @app.route('/register', method=['GET','POST'])
    def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            name = form.name.data
            username = form.username.data
            email = form.email.data
            password = form.password.data

        create cursor
        cur = LocalProxy(get_db)    
        error = None

        if not username:
            error = 'Username là trường bắt buộc'
        elif not email:
            error = 'Email là trường bắt buộc'
        elif not name:
            error = 'Tên là trường bắt buộc'
        elif not password:
            error = 'Mật khẩu là trường bắt buộc'
        elif "SELECT username, email FROM users WHERE username = ?",[username]).fetchone() is not None:
            error = 'Tên tài khoản {} đã tồn tại. Hãy chọn tên khác!'.format(username)
        elif "SELECT username, email FROM users WHERE email = ?",[email]).fetchone() is not None:
            error = 'Email này {} đã được sử dụng. Hãy nhập email khác!'.format(email)




    return app
