from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.amenity import Amenity
from app.database import db

amenities = Blueprint("amenities", __name__)


@amenities.route("/amenities/new", methods=["GET", "POST"])
def new_amenity():
    if request.method == "POST":
        name = request.form["name"]
        if name:
            amenity = Amenity(name=name)
            db.session.add(amenity)
            db.session.commit()
            flash("Amenity added!")
            return redirect(url_for("amenities.new_amenity"))
    return render_template("new_amenity.html")
