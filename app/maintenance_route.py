from flask import Flask, request, jsonify, Blueprint
from .database import get_db_connection

maintenance_route = Blueprint('maintenance', __name__)