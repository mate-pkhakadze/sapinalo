from datetime import datetime
from flask_login import UserMixin
from extensions import db
from slugify import slugify     


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    profile_image = db.Column(
        db.String(200),
        default="uploads/pfps/default.png"
    )

    is_admin = db.Column(db.Boolean, default=False)

    posts = db.relationship("Post", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="author", lazy=True)



class Tank(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Basic
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    tier = db.Column(db.Integer, nullable=False)
    tank_class = db.Column(db.String(20), nullable=False)
    nation = db.Column(db.String(50))
    role = db.Column(db.String(100))

    # Core stats (0–100 scale)
    firepower = db.Column(db.Integer)
    armor = db.Column(db.Integer)
    mobility = db.Column(db.Integer)
    view_range = db.Column(db.Integer)

    # Advanced stats (actual WoT-style)
    hit_points = db.Column(db.Integer)
    gun_caliber = db.Column(db.Float)     
    reload_time = db.Column(db.Float)    
    penetration = db.Column(db.Integer)    
    alpha_damage = db.Column(db.Integer)   
    top_speed = db.Column(db.Integer)       

    # Guide
    playstyle = db.Column(db.Text)

    # Media
    image = db.Column(db.String(200))

    posts = db.relationship("Post", backref="tank", lazy=True)

    @property
    def firepower_rating(self):
        if not all([self.alpha_damage, self.penetration, self.reload_time]):
            return 0

        dpm = (60 / self.reload_time) * self.alpha_damage

        score = (
            (dpm / 3000) * 40 +        
            (self.penetration / 260) * 40 +  
            (self.gun_caliber / 130) * 20    
        )

        return max(0, min(100, int(score)))

    @property
    def armor_rating(self):
        if not all([self.armor, self.hit_points]):
            return 0

        score = (
            (self.armor / 300) * 70 +     
            (self.hit_points / 2500) * 30
        )

        return max(0, min(100, int(score)))

    @property
    def mobility_rating(self):
        if not self.top_speed:
            return 0

        score = (
            (self.top_speed / 70) * 60 + 
            (self.tier / 10) * 40         
        )

        return max(0, min(100, int(score)))





class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tank_id = db.Column(db.Integer, db.ForeignKey("tank.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    comments = db.relationship("Comment", backref="post", lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)