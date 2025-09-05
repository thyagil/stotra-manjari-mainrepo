from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ====================
# Artists
# ====================
class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, nullable=False, unique=True)
    short_bio = db.Column(db.Text)
    image = db.Column(db.String)  # path to image file

    # many-to-many with projects (primary artists)
    projects = db.relationship(
        "Project",
        secondary="project_artists",
        back_populates="artists"
    )

    # one-to-many as contributors
    contributions = db.relationship("Contributor", back_populates="artist")


# ====================
# Project ↔ Artist link table (primary artists)
# ====================
project_artists = db.Table(
    "project_artists",
    db.Column("project_id", db.String, db.ForeignKey("projects.id"), primary_key=True),
    db.Column("artist_id", db.Integer, db.ForeignKey("artists.id"), primary_key=True),
)


# ====================
# Projects
# ====================
class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.String, primary_key=True)   # e.g. sgp_srimad_ramayanam
    friendly_name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)   # audiobook, ebook, music
    format = db.Column(db.String, nullable=False) # volume, chapter, standalone
    description = db.Column(db.Text)
    overview = db.Column(db.Text)
    preview = db.Column(db.Text)

    # app status
    featured = db.Column(db.Boolean, default=False)
    published = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    currency = db.Column(db.String, default="USD")
    price = db.Column(db.Float, default=0.0)

    # relationships
    artists = db.relationship(
        "Artist",
        secondary="project_artists",
        back_populates="projects"
    )
    images = db.relationship("ProjectImage", backref="project", cascade="all, delete-orphan")
    contributors = db.relationship("Contributor", back_populates="project", cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="project", cascade="all, delete-orphan")
    languages = db.relationship("Language", backref="project", cascade="all, delete-orphan")
    volumes = db.relationship("Volume", backref="project", cascade="all, delete-orphan")


# ====================
# Project Images
# ====================
class ProjectImage(db.Model):
    __tablename__ = "project_images"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey("projects.id"), nullable=False)
    key = db.Column(db.String, nullable=False)   # "cover", "banner", etc.
    path = db.Column(db.String, nullable=False)


# ====================
# Contributors (artist + role)
# ====================
class Contributor(db.Model):
    __tablename__ = "contributors"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey("projects.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    role = db.Column(db.String, nullable=False)   # e.g., Chanting, Translation

    # relationships
    project = db.relationship("Project", back_populates="contributors")
    artist = db.relationship("Artist", back_populates="contributions")


# ====================
# Categories
# ====================
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String, nullable=False)


# ====================
# Languages
# ====================
class Language(db.Model):
    __tablename__ = "languages"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String, db.ForeignKey("projects.id"), nullable=False)
    code = db.Column(db.String, nullable=False)  # "sa", "ta", "en"


# ====================
# Volumes
# ====================

class Volume(db.Model):
    __tablename__ = "volumes"

    id = db.Column(db.String, primary_key=True)   # volume01
    project_id = db.Column(db.String, db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String)
    thumbnail = db.Column(db.String)

    chapters = db.relationship("Chapter", backref="volume", cascade="all, delete-orphan")


# ====================
# Chapters
# ====================
class Chapter(db.Model):
    __tablename__ = "chapters"

    id = db.Column(db.String, primary_key=True)  # chapter001
    volume_id = db.Column(db.String, db.ForeignKey("volumes.id"), nullable=False)
    index = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String)
    subtitle = db.Column(db.String)
    state = db.Column(db.Integer, default=0)  # e.g., 0=draft, 1=in-progress, 2=final
