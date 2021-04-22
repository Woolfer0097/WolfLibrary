from . import db_session
from .users import User
from flask import jsonify
from flask_restful import Resource, abort, reqparse


parser = reqparse.RequestParser()
parser.add_argument('nickname', required=True)
parser.add_argument('age', required=True, type=int)
parser.add_argument('email', required=True)
parser.add_argument('user_avatar', required=True)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify(
            {
                'users':
                    [item.to_dict(only=('nickname', 'age', 'email', 'user_avatar'))
                     for item in user]
            }
        )

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify(
            {
                'users':
                    [item.to_dict(only=('nickname', 'age', 'email', 'user_avatar'))
                     for item in users]
            }
        )

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            nickname=args['nickname'],
            age=args['age'],
            email=['email'],
            user_avatar=['user_avatar']
        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
