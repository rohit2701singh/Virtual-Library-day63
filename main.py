from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books-library.db"     # "sqlite:///<name of database>.db"

db = SQLAlchemy()
db.init_app(app)

# -----------table creation in database-----------


class Books(db.Model):
    # table name will generate by converting the CamelCase class name to snake_case. e.g. BookName --> book_name
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    book_author: Mapped[str] = mapped_column(String(120), nullable=False)
    rating: Mapped[float] = mapped_column(Float(3), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    # --------read from database-----------
    result = db.session.execute(db.select(Books).order_by(Books.id))
    all_books = result.scalars()

    return render_template("index.html", books_collection=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        book_name = request.form.get("book")
        author = request.form.get("writer")
        rate = request.form.get("star")

        # -------adding record in database.

        new_book_review = Books(book_title=book_name, book_author=author, rating=rate)
        db.session.add(new_book_review)
        db.session.commit()
        # return redirect(url_for("home"))

    return render_template('add.html')


@app.route('/edit', methods=["GET", "POST"])
def edit_record():

    if request.method == "POST":
        record_id = request.form.get("id")  # from edit-rating.html <input hidden....>
        new_rating = request.form.get("rate")

        # --------update database rating-----------
        book_to_update = db.session.execute(db.select(Books).where(Books.id == record_id)).scalar()
        book_to_update.rating = new_rating
        db.session.commit()

        return redirect(url_for('home'))

    record_id = request.args.get("book_id")
    record_book = db.session.execute(db.select(Books).where(Books.id == record_id)).scalar()
    return render_template("edit-rating.html", book_detail=record_book)


@app.route('/delete/<book_id>')
def delete_record(book_id):

    # --------delete from database-----------
    book_to_update = db.session.execute(db.select(Books).where(Books.id == book_id)).scalar()
    db.session.delete(book_to_update)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

