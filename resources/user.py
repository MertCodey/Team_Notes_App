from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from schemas import UserRegisterSchema, UserSchema
from models.users import UserModel
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
)
from db import db
from models.users import UserModel
from blocklist import BLOCKLIST  

blp = Blueprint("Users", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Register a new user"""
        if UserModel.query.filter(
            or_(UserModel.email == user_data['email'], UserModel.username == user_data['username'])
        ).first():
            abort(400, message="Username or email already exists.")
        user = UserModel(**user_data)
        user.password = sha256.hash(user.password)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Username or email already exists.")
        return user, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)  
    def post(self, user_data):
        user = UserModel.query.filter_by(username=user_data["username"]).first()
        if not user or not sha256.verify(user_data["password"], user.password):
            abort(401, message="Invalid credentials.")

        access_token = create_access_token(identity=str(user.id), fresh=True)
        refresh_token = create_refresh_token(identity=str(user.id))
        return {"access_token": access_token, "refresh_token": refresh_token}, 200

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

@blp.route("/refresh")
class UserRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_access_token}, 200