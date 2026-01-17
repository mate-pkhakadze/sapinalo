from models import Tank
from flask import Blueprint, render_template, redirect, url_for, abort, request, flash
from flask_login import login_required, current_user
from extensions import db, app
from forms import TankForm
from os import path
from slugify import slugify
import os
from werkzeug.utils import secure_filename


tanks = Blueprint("tanks", __name__, url_prefix="/tanks")

@tanks.route("/")
def list_tanks():
    q = request.args.get("q", "")
    tier = request.args.get("tier")
    role = request.args.get("role")

    query = Tank.query

    if q:
        query = query.filter(Tank.name.ilike(f"%{q}%"))

    if tier:
        query = query.filter_by(tier=tier)

    if role:
        query = query.filter_by(role=role)

    tanks = query.all()
    return render_template("tanks/list.html", tanks=tanks)

@tanks.route("/add", methods=["GET", "POST"])
@login_required
def add_tank():
    if not current_user.is_admin:
        abort(403)

    form = TankForm()

    if form.validate_on_submit():
        tank = Tank(
            name=form.name.data,
            slug=slugify(form.name.data),
            tier=form.tier.data,
            tank_class=form.tank_class.data,
            nation=form.nation.data,
            role=form.role.data,

            armor=form.armor.data,
            view_range=form.view_range.data,

            hit_points=form.hit_points.data,
            gun_caliber=form.gun_caliber.data,
            reload_time=form.reload_time.data,
            penetration=form.penetration.data,
            alpha_damage=form.alpha_damage.data,
            top_speed=form.top_speed.data,

            playstyle=form.playstyle.data,
        )

        if form.image.data:
            image = form.image.data
            filename = slugify(form.name.data) + "." + image.filename.rsplit(".", 1)[1]
            upload_path = path.join(
                app.root_path, "static", "uploads", "tanks", filename
            )
            image.save(upload_path)
            tank.image = filename

        db.session.add(tank)
        db.session.commit()

        return redirect(url_for("tanks.list_tanks"))

    return render_template("tanks/add.html", form=form)

@tanks.route("/<slug>")
def tank_detail(slug):
    tank = Tank.query.filter_by(slug=slug).first_or_404()
    return render_template("tanks/detail.html", tank=tank)

@tanks.route("/tank/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_tank(slug):
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for("tanks.list_tanks"))

    tank = Tank.query.filter_by(slug=slug).first_or_404()
    form = TankForm(obj=tank)

    if form.validate_on_submit():

        # --- temporarily remove image field ---
        image_data = form.image.data
        form.image.data = None

        # populate everything EXCEPT image
        form.populate_obj(tank)

        # restore image field
        form.image.data = image_data

        # --- handle image upload manually ---
        if image_data and hasattr(image_data, "filename"):
            ext = image_data.filename.rsplit(".", 1)[1].lower()
            filename = f"{tank.slug}.{ext}"

            upload_path = os.path.join(
                app.root_path, "static", "uploads", "tanks", filename
            )

            image_data.save(upload_path)
            tank.image = filename

        db.session.commit()
        flash("Tank updated successfully", "success")
        return redirect(url_for("tanks.tank_detail", slug=tank.slug))

    return render_template("tanks/edit_tank.html", form=form, tank=tank)

@tanks.route("/compare")
def compare():
    left_id = request.args.get("left", type=int)
    right_id = request.args.get("right", type=int)

    tanks = Tank.query.order_by(Tank.name).all()

    tank1 = Tank.query.get(left_id) if left_id else None
    tank2 = Tank.query.get(right_id) if right_id else None

    return render_template(
        "tanks/compare.html",
        tanks=tanks,
        tank1=tank1,
        tank2=tank2
    )

@tanks.route("/tank/<slug>/delete", methods=["POST"])
@login_required
def delete_tank(slug):
    if not current_user.is_admin:
        flash("Access denied", "danger")
        return redirect(url_for("tanks.list_tanks"))

    tank = Tank.query.filter_by(slug=slug).first_or_404()
    db.session.delete(tank)
    db.session.commit()

    flash("Tank deleted", "success")
    return redirect(url_for("tanks.list_tanks"))