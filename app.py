from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager

import os
import secrets

from db import db
import models

from resources.item import blp as item_blp
from resources.store import blp as store_blp
from resources.tag import blp as tag_blp
from resources.user import blp as user_blp
from blocklist import BLOCKLIST

def create_app(db_uri=None):
      app = Flask(__name__)

      app.config["PROPAGATE_EXCEPTIONS"] = True
      app.config["API_TITLE"] = "My API"
      app.config["API_VERSION"] = "v1"
      app.config["OPENAPI_VERSION"] = "3.0.3"
      app.config["OPENAPI_URL_PREFIX"] = "/"
      app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui/"
      app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
      app.config["SQLALCHEMY_DATABASE_URI"] = db_uri or os.getenv("DATABASE_URL", "sqlite:///data.db")
      app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
      db.init_app(app)

      api = Api(app)
      app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(16))
      jwt = JWTManager(app)

      @jwt.token_in_blocklist_loader
      def check_in_blocklist(jwt_header, jwt_payload):
            return jwt_payload["jti"] in BLOCKLIST

      @jwt.revoked_token_loader
      def revoked_token_callback(jwt_header, jwt_payload):
            return (
                  jsonify({
                        "description": "Token has been revoked", 
                        "error": "token_revoked"
                  }),
                  401,
            )

      @jwt.additional_claims_loader
      def add_claims_to_access_token(identity):
            if identity == 1:
                  return {"is_admin": True}
            return {"is_admin": False}

      @jwt.additional_claims_loader
      def add_claims_to_jwt(identity):
            # look in the database and see if the user is an admin
            if identity == 1:
                  return {"is_admin": True}
            return {"is_admin": False}

      @jwt.expired_token_loader
      def expired_token_callback(jwt_header, jwt_payload):
            return (
                  jsonify({
                        "message": "The token has expired", 
                        "error": "token_expired"}), 
                  401
            )
            
      @jwt.invalid_token_loader
      def invalid_token_callback(error):
            return (
                  jsonify({
                              "message": "Signature verification failed", 
                              "error": "invalid_token"
                        }),
                  401,
            )
            
      @jwt.unauthorized_loader
      def missing_token_callback(error):
            return (
                  jsonify({
                              "description": "Request does not contain an access token", 
                              "error": "authorization_required" 
                        })
            )

      @app.before_first_request
      def create_tables():
            db.create_all()

      api.register_blueprint(item_blp)
      api.register_blueprint(store_blp)
      api.register_blueprint(tag_blp)
      api.register_blueprint(user_blp)

      return app