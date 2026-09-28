"""Route /api/journal (consultation réservée aux administrateurs)."""
from flask import Blueprint, jsonify

from ..db import get_db
from ..security import admin_requis
from ..services import journal

bp = Blueprint("journal", __name__)


@bp.get("/journal")
@admin_requis
def lister():
    return jsonify(journal.lister(get_db()))
