import os
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))

db_dir = os.path.join(basedir, 'database')
os.makedirs(db_dir, exist_ok=True)

database_filename = 'casting_agency.db'
database_path = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(db_dir, database_filename)}')

if database_path and database_path.startswith('postgres://'):
    database_path = database_path.replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy()
migrate = Migrate()

movie_actor = Table('movie_actor', db.Model.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('actor_id', Integer, ForeignKey('actors.id'), primary_key=True)
)

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)


class Movie(db.Model):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    release_date = Column(Date, nullable=False)

    actors = relationship('Actor', secondary=movie_actor, back_populates='movies')

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self, include_actors=False):
        result = {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.strftime('%Y-%m-%d')
        }
        if include_actors:
            result['actors'] = [{'id': actor.id, 'name': actor.name} for actor in self.actors]
        return result


class Actor(db.Model):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)

    movies = relationship('Movie', secondary=movie_actor, back_populates='actors')

    def __init__(self, name, birth_date, gender):
        self.name = name
        self.birth_date = birth_date
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def calculate_age(self):
        from datetime import date
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def format(self, include_movies=False):
        result = {
            'id': self.id,
            'name': self.name,
            'birth_date': self.birth_date.strftime('%Y-%m-%d'),
            'age': self.calculate_age(),
            'gender': self.gender
        }
        if include_movies:
            result['movies'] = [{'id': movie.id, 'title': movie.title} for movie in self.movies]
        return result


def db_drop_and_create_all():
    from datetime import date

    db.drop_all()
    db.create_all()

    movies = [
        Movie(title='The Shawshank Redemption', release_date=date(1994, 9, 23)),
        Movie(title='The Godfather', release_date=date(1972, 3, 24)),
        Movie(title='The Dark Knight', release_date=date(2008, 7, 18)),
        Movie(title='Pulp Fiction', release_date=date(1994, 10, 14)),
        Movie(title='Forrest Gump', release_date=date(1994, 7, 6))
    ]

    for movie in movies:
        movie.insert()

    actors = [
        Actor(name='Morgan Freeman', birth_date=date(1937, 6, 1), gender='Male'),
        Actor(name='Marlon Brando', birth_date=date(1924, 4, 3), gender='Male'),
        Actor(name='Christian Bale', birth_date=date(1974, 1, 30), gender='Male'),
        Actor(name='Uma Thurman', birth_date=date(1970, 4, 29), gender='Female'),
        Actor(name='Tom Hanks', birth_date=date(1956, 7, 9), gender='Male')
    ]

    for actor in actors:
        actor.insert()

    movies[0].actors.append(actors[0])
    movies[1].actors.append(actors[1])
    movies[2].actors.append(actors[2])
    movies[3].actors.append(actors[3])
    movies[4].actors.append(actors[4])

    movies[2].actors.append(actors[0])

    db.session.commit()