from os import path
basedir = path.abspath(path.dirname(__file__))
database_path = path.join(basedir,'database','datos.db')
SECRET_KEY = "GDtfDCFYjD"
SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_path}'
SQLALCHEMY_TRACK_MODIFICATIONS = False