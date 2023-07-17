from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(app)


class Estudiante(db.Model):
    
    __tablename__ = "estudiante"
    
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(80), nullable = False)
    apellido = db.Column(db.String(80), nullable = False)
    dni = db.Column(db.String(10), nullable = False)
    idcurso = db.Column(db.Integer, db.ForeignKey('curso.id'))
    idpadre = db.Column(db.Integer, db.ForeignKey('padre.id'))
    
    """
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'dni': self.dni,
            'idcurso': self.idcurso,
            'idpadre': self.idpadre
        }

    @staticmethod
    def from_dict(obj_dict):
        return Estudiante(
            id=obj_dict['id'],
            nombre=obj_dict['nombre'],
            apellido=obj_dict['apellido'],
            dni=obj_dict['dni'],
            idcurso=obj_dict['idcurso'],
            idpadre=obj_dict['idpadre']
        )
    """
    def to_json(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'dni': self.dni,
            'idcurso': self.idcurso,
            'idpadre': self.idpadre
        }

    @staticmethod
    def from_json(json_data):
        return Estudiante(
            id=json_data['id'],
            nombre=json_data['nombre'],
            apellido=json_data['apellido'],
            dni=json_data['dni'],
            idcurso=json_data['idcurso'],
            idpadre=json_data['idpadre']
        )

class Padre(db.Model):
    
    __tablename__ = "padre"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    clave = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'correo': self.correo,
            'clave': self.clave
        }

    def json_serializable(self):
        return self.to_dict()
    
    @staticmethod
    def from_dict(obj_dict):
        return Padre(
            id=obj_dict['id'],
            nombre=obj_dict['nombre'],
            apellido=obj_dict['apellido'],
            correo=obj_dict['correo'],
            clave=obj_dict['clave']
        )


class Preceptor(db.Model):
    
    __tablename__ = "preceptor"
    
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(80), nullable = False)
    apellido = db.Column(db.String(80), nullable = False)
    correo = db.Column(db.String(120), nullable = False)
    clave = db.Column(db.String(120), nullable = False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'correo': self.correo,
            'clave': self.clave
        }

    @staticmethod
    def from_dict(obj_dict):
        return Preceptor(
            obj_dict['id'],
            obj_dict['nombre'],
            obj_dict['apellido'],
            obj_dict['clave']
        )
    

class Curso(db.Model):
    
    __tablename__ = "curso"
    
    id = db.Column(db.Integer, primary_key = True)
    anio = db.Column(db.String(80), nullable = False)
    division = db.Column(db.String(80), nullable = False)
    idpreceptor = db.Column(db.Integer, db.ForeignKey('preceptor.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'anio': self.anio,
            'division': self.division,
            'idpreceptor': self.idpreceptor
        }

    @staticmethod
    def from_dict(obj_dict):
        return Curso(
            obj_dict['id'],
            obj_dict['anio'],
            obj_dict['division'],
            obj_dict['idpreceptor']
        )
    

class Asistencia(db.Model):
    
    __tablename__ = "asistencia"
    
    id = db.Column(db.Integer, primary_key = True)
    fecha = db.Column(db.Date)
    codigoclase = db.Column(db.Integer)
    asistio = db.Column(db.Text)
    justificacion = db.Column(db.String(100), nullable = False)
    idestudiante = db.Column(db.Integer, db.ForeignKey('estudiante.id'))