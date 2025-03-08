from flask import Blueprint

plant_bp = Blueprint('plant', __name__)

from . import routes
