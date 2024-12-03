from flask import (Flask, render_template, redirect, render_template, redirect, request, render_template_string)
from flask_login import (LoginManager, login_user, login_required, logout_user, current_user)
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.books import Book
from data.users import User
from data.authors import Author
from forms.search import SearchForm
from forms.user import UserSignInForm, UserSignUpForm

from datetime import datetime, timedelta
from tools import *

template_dir = "templates"
static_dir = "static"
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.json.sort_keys = False
app.config["SECRET_KEY"] = "dfaasdjkfajsdkfjaklsdhjklfasjhdk"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

app.book_index = {}
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
HOST = '127.0.0.1'
PORT = 8080


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"/search/{search_form.search.data}")
    sign_in_form = UserSignInForm()
    if sign_in_form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == sign_in_form.email.data).first()
        if user and user.check_password(sign_in_form.password.data):
            login_user(user, remember=sign_in_form.remember_me.data)
            return redirect('/')
        return render_template(
            "sign_in_user.html",
            title="Sign In",
            message="Incorrect email or password",
            sign_in_form=sign_in_form,
            search_form=search_form
        )
    return render_template(
        "sign_in_user.html",
        title="Sign In",
        sign_in_form=sign_in_form,
        search_form=search_form
    )


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"search/{search_form.search.data}")
    sign_up_form = UserSignUpForm()
    if sign_up_form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == sign_up_form.email.data).first() is not None:
            return render_template(
                "sign_up_user.html",
                title="Sign In",
                search_form=search_form,
                message="There is already an account with that email!",
                sign_up_form=sign_up_form
            )
        if db_sess.query(User).filter(User.nickname == sign_up_form.nickname.data).first() is not None:
            return render_template(
                "sign_up_user.html",
                title="Sign In",
                search_form=search_form,
                message="There is already an account with that nickname!",
                sign_up_form=sign_up_form
            )
        user = User(
            email=sign_up_form.email.data,
            nickname=sign_up_form.nickname.data,
            age=sign_up_form.age.data,
            description=sign_up_form.description.data,
        )
        user.set_password(sign_up_form.password.data),
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/')
    return render_template(
        "sign_up_user.html",
        title="Sign Up",
        search_form=search_form,
        sign_up_form=sign_up_form
    )


@app.route('/search/<string:search>', methods=["GET", "POST"])
def search(search: str):
    search_form = SearchForm()
    if search_form.validate_on_submit():
        print("Trying to search on search page")
        return redirect(f"http://{HOST}:{PORT}/search/{search_form.search.data}")

    ids = []
    search_token = tokenize(search)
    for article_id, article_token in app.book_index.items():
        num_matching_words = len(search_token & article_token)
        if num_matching_words > 0:
            ids.append((article_id, num_matching_words))
    ids.sort(key=lambda x: x[1], reverse=True)
    ids = [i[0] for i in ids]

    sess = db_session.create_session()
    articles = sess.query(Book).filter(Book.id.in_(ids)).all()
    return render_template("search_results.html", articles=articles, search_form=search_form)


@app.route('/library', methods=["GET", "POST"])
def library():
    return redirect('/')


@app.route('/')
def index():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(f"http://{HOST}:{PORT}/search/{search_form.search.data}")

    return render_template("base.html", title="Library", search_form=search_form)


def main() -> None:
    db_session.global_init("db/library.sqlite")
    sess = db_session.create_session()
    books = sess.query(Book).all()
    for book in books:
        app.book_index[book.id] = tokenize(book.title)
    app.run(host=HOST, port=PORT, debug=True, threaded=True)


if __name__ == "__main__":
    main()
