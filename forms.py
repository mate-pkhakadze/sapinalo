from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, optional, Optional
from flask_wtf.file import FileAllowed, FileField

class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=50)]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")]
    )

    profile_image = FileField(
        "Profile Picture",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")]
    )

    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")

class TankForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    tier = IntegerField("Tier", validators=[DataRequired()])

    tank_class = SelectField(
        "Class",
        choices=[
            ("heavy", "Heavy"),
            ("medium", "Medium"),
            ("light", "Light"),
            ("td", "Tank Destroyer"),
            ("spg", "SPG"),
        ],
        validators=[DataRequired()],
    )

    nation = StringField("Nation", validators=[Optional()])
    role = StringField("Role", validators=[Optional()])

    # === BASE STATS (USER ENTERS THESE) ===
    hit_points = IntegerField("Hit Points", validators=[Optional()])
    armor = IntegerField("Armor", validators=[Optional()])
    top_speed = IntegerField("Top Speed (km/h)", validators=[Optional()])

    alpha_damage = IntegerField("Alpha Damage", validators=[Optional()])
    penetration = IntegerField("Penetration (mm)", validators=[Optional()])
    reload_time = FloatField("Reload Time (s)", validators=[Optional()])
    gun_caliber = FloatField("Gun Caliber (mm)", validators=[Optional()])

    view_range = IntegerField("View Range (m)", validators=[Optional()])

    playstyle = TextAreaField(
        "How to play this tank",
        validators=[DataRequired()]
    )

    image = FileField("Tank image", validators=[Optional()])

    submit = SubmitField("Add Tank")