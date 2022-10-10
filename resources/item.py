from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema


blp = Blueprint("Items", __name__, description="Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
      @jwt_required()
      @blp.response(200, ItemSchema)
      def get(self, item_id):
            item = ItemModel.query.get_or_404(item_id)
            return item

      @jwt_required()
      def delete(self, item_id):
            jwt = get_jwt()
            if not jwt.get("is_admin"):
                  abort(403, message="Admin privilege required")
            item = ItemModel.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return {"message", "Item deleted"}, 204

      @jwt_required()
      @blp.arguments(ItemUpdateSchema)
      @blp.response(200, ItemUpdateSchema)
      def put(self, item_id, item_data):
            item = ItemModel.query.get(item_id)
            if item:
                  item.price = item_data["price"]
                  item.name = item_data["name"]
            else:
                  item = ItemModel(id=item_id, **item_data)
            
            db.session.add(item)
            db.session.commit()

            return item, 200

@blp.route("/item")
class ItemList(MethodView):
      @jwt_required()
      @blp.response(200, ItemSchema(many=True))
      def get(self):
            return ItemModel.query.all()
      
      @jwt_required()
      @blp.arguments(ItemSchema)
      @blp.response(201, ItemSchema)
      def post(self, item_data, store_id):
            item = ItemModel(**item_data, store_id=store_id)
            
            try:
                  db.session.add(item)
                  db.session.commit()
            except SQLAlchemyError:
                  abort(400, message="An error occurred while adding the item.")
            return item, 201

