from models import Tank
from flask import Blueprint, render_template, redirect, url_for, abort, request
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

@tanks.route("/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_tank(slug):
    if not current_user.is_admin:
        abort(403)

    tank = Tank.query.filter_by(slug=slug).first_or_404()
    form = TankForm(obj=tank)  # 👈 pre-fill form

    if form.validate_on_submit():
        form.populate_obj(tank)

        # image update (optional)
        if form.image.data:
            # delete old image
            if tank.image:
                old_path = path.join(
                    app.root_path, "static", "uploads", "tanks", tank.image
                )
                if path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(form.image.data.filename)
            upload_path = path.join(
                app.root_path, "static", "uploads", "tanks", filename
            )
            form.image.data.save(upload_path)
            tank.image = filename

        tank.calculate_ratings()  # 🔥 IMPORTANT
        db.session.commit()

        return redirect(url_for("tanks.tank_detail", slug=tank.slug))

    return render_template("tanks/edit.html", form=form, tank=tank)

@tanks.route("/compare")
def compare_tanks():
    left_slug = request.args.get("left")
    right_slug = request.args.get("right")

    if not left_slug or not right_slug:
        abort(400)

    left = Tank.query.filter_by(slug=left_slug).first_or_404()
    right = Tank.query.filter_by(slug=right_slug).first_or_404()

    return render_template(
        "tanks/compare.html",
        left=left,
        right=right,
    )

@tanks.route("/<slug>/delete", methods=["POST"])
@login_required
def delete_tank(slug):
    if not current_user.is_admin:
        abort(403)

    tank = Tank.query.filter_by(slug=slug).first_or_404()

    # delete image file
    if tank.image:
        image_path = path.join(
            app.root_path, "static", "uploads", "tanks", tank.image
        )
        if path.exists(image_path):
            os.remove(image_path)

    db.session.delete(tank)
    db.session.commit()

    return redirect(url_for("tanks.list_tanks"))
