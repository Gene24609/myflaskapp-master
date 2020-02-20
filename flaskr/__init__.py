#from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from wtforms import Form, StringField, TextAreaField, PasswordField, validators
#from werkzeug.security import check_password_hash, generate_password_hash
#from functools import wraps
#import os
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import sqlite3
import os

#nạp module db_connector
from . import db_connector
from flaskr.db_connector import get_db
#from flaskr.db_connector import close_db

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
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path,'flaskr.sqlite')
    )
    
    if test_config is None:
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
    #@is_logged_in
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

        email = StringField('Email',[
            validators.Length(min=6,max=50),
            validators.Required("Hãy nhập email của bạn!"),
            validators.Email("Email nhập không chính xác!")
        ])

        password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Password giữa hai lần nhập không khớp! Hãy nhập lại!'),
        ])
        confirm = PasswordField('Confirm Password')

    #User Register
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            name = form.name.data
            email = form.email.data
            username = form.username.data
            password = form.password.data

            #create cursor
            cur = get_db()  
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif not email:
                error = 'Email is required'
            elif not name:
                error = 'Display name is required'
            elif cur.execute("SELECT * FROM users WHERE username = ?",[username]).fetchone() is not None:
                error = 'Username {} đã được sử dụng!'.format(username)
            elif cur.execute("SELECT * FROM users WHERE email = ?", [email]).fetchone() is not None:
                error = 'Email {} đã được sử dụng!'.format(email)

            if error is None:
                cur.execute(
                    'INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)',
                    (name, email, username, generate_password_hash(password))
                    )
            # Commit to DB
            cur.commit()
            # Close connection
            cur.close()
            if error is None:
                flash('Bạn đã đăng ký thành công và có thể đăng nhập', 'success')
                return redirect(url_for('login'))
            else:
                flash(error, 'danger')
        
        return render_template('register.html', form=form)

    # User login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
        # Get Form Fields
            username = request.form['username']
            password_candidate = request.form['password']

        # Create cursor
            cur = get_db()
        # Get user by username
            result = cur.execute("SELECT username, password FROM users WHERE username = ?", [username]).fetchone()
            if result is None:
                error = 'Tài khoản hoặc mật khẩu không chính xác!'
                return render_template('login.html', error=error)
            else:
                # Get stored hash
                data = result
                password = data['password']

            # Compare Passwords
                if check_password_hash(password, password_candidate):
                # Passed
                    session['logged_in'] = True
                    session['username'] = username

                    flash('Xin chào ['+ username + ']. Bạn đã đăng nhập thành công!', 'success')
                    #return redirect(url_for('dashboard'))
                    return redirect(url_for('index'))
                else:
                    error = 'Tài khoản hoặc mật khẩu không chính xác!'
                    return render_template('login.html', error=error)
            # Close connection
            cur.commit()
            cur.close()
        return render_template('login.html')

# Check if user logged in
    def is_logged_in(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                flash('Hãy đăng nhập để xem nội dung này!', 'danger')
                return redirect(url_for('login'))
        return wrap

    # Logout
    @app.route('/logout')
    @is_logged_in
    def logout():
        session.clear()
        flash('Đăng xuất thành công!', 'success')
        return redirect(url_for('login'))

    # Articles
    @app.route('/articles')
    def articles():
        cur = get_db()
        res = cur.execute("SELECT * FROM articles WHERE publish = ? ",['Publish'])
        articles = res.fetchall()
        cur.commit()
        cur.close()

        if res is None:
            msg = 'Không có bài viêt!!!'
            return render_template('articles.html', msg=msg)
        else:
            return render_template('articles.html', articles = articles)

    # Single Article
    @app.route('/article/<string:id>/')
    def article(id):
        # Create cursor
        cur = get_db()
        # Get article
        res = cur.execute("SELECT * FROM articles WHERE id = ?", [id])
        article = res.fetchone()
        cur.commit()
        cur.close()
        return render_template('article.html', article=article)
    
    # Dashboard
    @app.route('/dashboard')
    @is_logged_in
    def dashboard():
        cur = get_db()
        res = cur.execute("SELECT * from articles WHERE author = ?", [session['username']])
        articles = res.fetchall()
        cur.commit
        cur.close
        if res is None:
            msg = 'Bạn chưa tạo bài viết nào! Hãy bắt đầu viết một bài viết đi nào :)'
            return render_template('dashboard.html', msg = msg)
        else:
            return render_template('dashboard.html', articles = articles)
# Article Form Class
    class ArticleForm(Form):
        title = StringField('Tiêu đề', [validators.Length(min=1, max=200)])
        body = TextAreaField('Nội dung', [validators.Length(min=1)])

# Add Article
    @app.route('/add_article', methods=['GET', 'POST'])
    @is_logged_in
    def add_article():
        form = ArticleForm(request.form)
        if request.method == 'POST' and form.validate():
            title = form.title.data
            body = form.body.data

        # Create Cursor
            cur = get_db()

        # Execute
            cur.execute("INSERT INTO articles(title, body, author) VALUES(?, ?, ?)",(title, body, session['username']))

        # Commit to DB
            cur.commit()

        #Close connection
            cur.close()

            flash('Article Created', 'success')

            return redirect(url_for('dashboard'))

        return render_template('add_article.html', form=form)


# Edit Article
    @app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
    @is_logged_in
    def edit_article(id):
    # Create cursor
        cur = get_db()
    # Get article by id
        result = cur.execute("SELECT * FROM articles WHERE id = ?", [id])
        article = result.fetchone()
        cur.commit()
        #cur.close()
        db_connector.close_db()
    # Get form
        form = ArticleForm(request.form)

    # Populate article form fields
        form.title.data = article['title']
        form.body.data = article['body']

        if request.method == 'POST' and form.validate():
            title = request.form['title']
            body = request.form['body']

        # Create Cursor
            cur = get_db()
            cur.execute(
                'UPDATE articles SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            #app.logger.info(title)
         # Execute
            cur.commit()
        #Close connection
            cur.close()
            flash('Article Updated', 'success')
            return redirect(url_for('dashboard'))

        return render_template('edit_article.html', form=form)

# Delete Article
    @app.route('/delete_article/<string:id>', methods=['POST'])
    @is_logged_in
    def delete_article(id):
    # Create cursor
        cur = get_db()

    # Execute
        cur.execute("DELETE FROM articles WHERE id = ?", [id])

    # Commit to DB
        cur.commit()

    #Close connection
        cur.close()

        flash('Article Deleted', 'success')

        return redirect(url_for('dashboard'))
# PP Article
    @app.route('/pp_article/<string:id>', methods=['POST'])
    @is_logged_in
    def pp_article(id):
    # Create cursor
        cur = get_db()
    
    # Execute
        if request.method == 'POST':
            if request.form['hide_button'] == 'Publish':
                cur.execute( 'UPDATE articles SET publish = ? WHERE id = ?',('Pending', id))
                flash('Article '+ id +' is changed to "Pending"', 'success')
            elif request.form['hide_button'] == 'Pending':
                cur.execute( 'UPDATE articles SET publish = ? WHERE id = ?',('Publish', id))
                flash('Article '+ id +' is changed to "Publish"', 'success')
                
    # Commit to DB
        cur.commit()

    #Close connection
        cur.close()

        

        return redirect(url_for('dashboard'))








    return app
