import os
import random
from datetime import datetime

from flask import Flask, render_template, redirect, abort, request, send_file
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from data import db_session
from data.book import Book
from data.genres import Genre
from data.users import User
from forms.change_password import ChangePasswordForm
from forms.edit_book import EditBookForm
from forms.add_book import AddBookForm
from forms.login import LoginForm
from forms.register import RegisterForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    db_sess = db_session.create_session()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_page.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_page.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            nickname=form.login.data,
            age=form.age.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template('register_page.html', title='Регистрация', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter((User.email == form.email.data) | (User.nickname == form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login_page.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template("login_page.html", title="Авторизация", form=form)


@app.route("/change_avatar", methods=["GET", "POST"])
@login_required
def change_avatar():
    db_sess = db_session.create_session()
    if request.method == "POST":
        file = request.files['file']
        with open(f"static/images/avatars/{current_user.nickname}.png", "wb") as file_write:
            file_write.write(file.read())
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.user_avatar = f"{current_user.nickname}.png"
        db_sess.commit()
        return redirect("/change_avatar")
    else:
        return render_template("change_avatar_page.html", title="Смена аватара")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    db_sess = db_session.create_session()
    form = ChangePasswordForm()
    if request.method == "POST":
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect("/personal_account")
        else:
            return render_template("change_password_page.html", title="Смена пароля", form=form,
                                   message="Неправильный пароль")
    else:
        return render_template("change_password_page.html", title="Смена пароля", form=form)


@app.route("/", methods=["GET", "POST"])
def index():
    db_sess = db_session.create_session()
    if request.method == "POST":
        author = request.form['author-search']
        title = request.form['title-search']
        books = db_sess.query(Book).filter(Book.title.like(f"%{title.strip()}%")).filter(
            Book.book_author.like(f"%{author.strip()}%")).all()
        return render_template("main_page.html", title="Главная страница", books=books, books_count=len(books),
                               req=f"{title} {author}")
    else:
        books = db_sess.query(Book).all()
        return render_template("main_page.html", title="Главная страница", books=books, books_count=len(books))


@app.route("/personal_account")
@login_required
def personal_account():
    db_sess = db_session.create_session()
    user_books = db_sess.query(Book).filter(Book.user_id == current_user.id).all()
    return render_template("personal_account_page.html", books=user_books, books_count=len(user_books))


@app.route("/show_book/<int:book_id>", methods=["GET", "POST"])
def show_book(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    content_analysis = book.content_analysis
    l_u = book.updated_date
    image = book.image_link
    if not image or not os.path.exists(image):
        image = "static/images/skins/standard-image.jpg"
    return render_template("book_info_page.html",
                           title=book.title, image=image, author=book.book_author, genre=book.genre.title,
                           user_author=book.user.nickname, content_analysis=content_analysis, last_update=l_u,
                           book=book)


@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    form = EditBookForm()
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    if not book:
        abort(404, message="Такой книги не существует")
    if request.method == "POST":
        book.title = form.title.data
        book.book_author = form.book_author.data
        book.genre_id = form.genre.data
        book.updated_date = datetime.now()
        book.content_analysis = request.form['text']
        file_image = request.files['file']
        file_book = request.files['file_book']
        if file_image:
            image_link = f"static/images/skins/{book.title}-{random.randint(1, 100000)}.png"
            os.remove(book.image_link)
            with open(image_link, "wb") as file_write:
                file_write.write(file_image.read())
            book.image_link = image_link
        if file_book:
            file_link = f"static/files/{file_book.filename}"
            with open(file_link, "wb") as file_write:
                file_write.write(file_book.read())
            book.pdf_link = file_link
        db_sess.commit()
        return redirect(f"/show_book/{book_id}")
    else:
        image = book.image_link
        if not image or not os.path.exists(image):
            image = "static/images/skins/standard-image.jpg"
        form.genre.choices = [(i.id, i.title) for i in db_sess.query(Genre).all()]
        form.title.data = book.title
        form.book_author.data = book.book_author
        form.genre.data = book.genre_id
        return render_template("edit_book_page.html", form=form, book=book, image_link=image)


@app.route("/delete_book/<int:book_id>", methods=["GET", "POST"])
@login_required
def delete_book(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    if book:
        db_sess.delete(book)
        db_sess.commit()
    else:
        abort(404)
    return redirect(request.referrer)


@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    form = AddBookForm()
    db_sess = db_session.create_session()
    if request.method == "POST":
        book = Book()
        book.title = form.title.data
        book.book_author = form.book_author.data
        book.genre_id = form.genre.data
        book.created_date = datetime.now()
        book.updated_date = datetime.now()
        book.content_analysis = request.form['text']
        file_image = request.files['file']
        file_book = request.files['file_book']
        image_link = f"static/images/skins/{book.title}-{random.randint(1, 100000)}.png"
        file_link = f"static/files/{file_book.filename}"
        if file_image:
            with open(image_link, "wb") as file_write:
                file_write.write(file_image.read())
            book.image_link = image_link
        if file_book:
            with open(file_link, "wb") as file_write:
                file_write.write(file_book.read())
            book.pdf_link = file_link
        current_user.books.append(book)
        db_sess.merge(current_user)
        db_sess.commit()
        last_id = [int(*i) for i in db_sess.query(Book.id).all()]
        return redirect(f"/show_book/{last_id[-1]}")
    else:
        form.genre.choices = [(i.id, i.title) for i in db_sess.query(Genre).all()]
        return render_template("add_book_page.html", form=form)


@app.route("/download_file/<int:book_id>")
def download_file(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == book_id).first()
    return send_file(book.pdf_link, as_attachment=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/books.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=8080)
