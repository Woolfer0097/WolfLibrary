from . import db_session
from .book import Book
from flask import jsonify
from flask_restful import Resource, abort, reqparse


parser = reqparse.RequestParser()
parser.add_argument('genre_id', required=True, type=int)
parser.add_argument('user_author', required=True, type=int)
parser.add_argument('book_author', required=True)
parser.add_argument('book_size', required=True)


def abort_if_user_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Book).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")


class BooksResource(Resource):
    def get(self, book_id):
        abort_if_user_not_found(book_id)
        session = db_session.create_session()
        book = session.query(Book).get(book_id)
        return jsonify(
            {
                'books':
                    [item.to_dict(only=('genre_id', 'user_author', 'book_author', 'book_size'))
                     for item in book]
            }
        )

    def delete(self, book_id):
        abort_if_user_not_found(book_id)
        session = db_session.create_session()
        book = session.query(Book).get(book_id)
        session.delete(book)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, book_id):
        abort_if_user_not_found(book_id)
        args = parser.parse_args()
        session = db_session.create_session()
        book = session.query(Book).get(book_id)
        book.genre_id = args["genre_id"]
        book.user_author = args["user_author"]
        book.book_author = args["book_author"]
        book.book_size = args["book_size"]
        session.commit()
        return jsonify({'success': 'OK'})


class BooksListResource(Resource):
    def get(self):
        session = db_session.create_session()
        books = session.query(Book).all()
        return jsonify(
            {
                'books':
                    [item.to_dict(only=('genre_id', 'user_author', 'book_author', 'book_size'))
                     for item in books]
            }
        )

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        book = Book(
            genre_id=args["genre_id"],
            user_author=args["user_author"],
            book_author=args["book_author"],
            book_size=args["book_size"]
        )
        session.add(book)
        session.commit()
        return jsonify({'success': 'OK'})
