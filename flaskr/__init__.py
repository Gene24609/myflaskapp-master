from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
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
    from . import auth
    app.register_blueprint(auth.bp)




    return app
