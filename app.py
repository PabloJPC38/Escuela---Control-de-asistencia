from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json



app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = 'EscuelaSanMiguel'  # Agrega una clave secreta para las sesiones


from models import db
from models import Estudiante, Preceptor, Curso, Asistencia, Padre
import hashlib


@app.route('/')
def inicio():
    
    return render_template("login.html")

@app.route('/login', methods=['GET','POST']) # type: ignore
def login():
    
    ruta_actual = request.url
    session['previous_page'] = ruta_actual
    
    if request.method == 'POST':
        
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        clave = hashlib.md5(bytes(contraseña, encoding='utf-8'))
        
        rol = request.form['rol']
        
        error = ""
        
        preceptor = Preceptor.query.filter(Preceptor.correo == correo, Preceptor.clave == clave.hexdigest()).first()
        padre = Padre.query.filter(Padre.correo == correo, Padre.clave == clave.hexdigest()).first()
        
        if preceptor is not None:
            
            if rol == "Preceptor":
                
                cursos = Curso.query.filter(Curso.idpreceptor == preceptor.id).all()
                
                fechas = Asistencia.query.filter(Asistencia.fecha)
                
                session['user_id'] = preceptor.id
                session['user_role'] = 'preceptor'
                
                serialized_cursos = [curso.to_dict() for curso in cursos]
                session['cursos'] = json.dumps(serialized_cursos)
                session['curso'] = 0
                serialized_preceptor = preceptor.to_dict()
                session['preceptor'] = json.dumps(serialized_preceptor)
                session['padre'] = None
                
                session['band'] = True
                
                return render_template("index.html", precept=preceptor, cursos=cursos, band=True)

            else:
                
                error = "ROL INVÁLIDO!!"
        
        elif padre is not None:
        
            if rol == "Padre":
                
                session['user_id'] = padre.id
                session['user_role'] = 'padre'
                serialized_padre = padre.to_dict()
                session['padre'] = json.dumps(serialized_padre)
                session['preceptor'] = None
                session['band'] = False
                
                return render_template("index.html", padre=padre, band=False)

            else:
                
                error = "ROL INVÁLIDO!!"
            
        else:
                
            error = "Usuario o contraseña inválidos"
        
        return render_template("login.html", error=error, band=True)
    
    
    elif request.method == 'GET':
        
        serialized_padre = session.get('padre')
        serialized_preceptor = session.get('preceptor')
        serialized_cursos = session.get('cursos')
        
        band = session.get('band')
        
        cursos = []
        preceptor = None
        padre = None

        if serialized_padre:
            
            padre_id = json.loads(serialized_padre)['id']
            padre = Padre.query.filter(Padre.id == padre_id).first()

        if serialized_preceptor:
            
            preceptor_id = json.loads(serialized_preceptor)['id']
            preceptor = Preceptor.query.filter(Preceptor.id == preceptor_id).first()
            
        if serialized_cursos:
            
            cursos = [Curso.query.get(curso_dict['id']) for curso_dict in json.loads(serialized_cursos)]

        return render_template("index.html", padre=padre, precept=preceptor, cursos=cursos, band=band)

from flask import redirect, request

@app.route('/logout')
def logout():
    if 'user_id' in session and 'user_role' in session:
        # Cerrar sesión
        session.clear()
        return redirect('/')
    elif 'previous_page' in session:
        # Volver a la página anterior
        previous_page = session['previous_page']
        session.pop('previous_page', None)  # Limpia la variable de sesión
        return redirect(previous_page)
    else:
        # En caso de no tener información para volver atrás o cerrar sesión, redirigir a la página de inicio
        return redirect('/')

def verificar_sesion():
    if 'user_id' in session and 'user_role' in session:
        return True
    else:
        return False

@app.route("/buscarHijo", methods=['GET'])
def buscarHijo():
    
    
    padre = request.args.get('padre')
    
    
    if not verificar_sesion():
        return redirect('/')  # Redirigir al usuario a la página de inicio de sesión si no ha iniciado sesión

    dni = request.args.get('dni')  # Usar request.args.get() para obtener el valor de los parámetros GET
    
    if dni == "":
        
        return render_template("index.html",band2 = True, error = "Campo vacío!!", padre = Padre.query.filter(Padre.id == session['user_id']).first())
    
    estudiante = Estudiante.query.filter(Estudiante.dni == dni).first()
    
    if estudiante == None:
        
        return render_template("index.html",band2 = True, error = "DNI desconocido!!", padre = Padre.query.filter(Padre.id == session['user_id']).first())
    
    inasistencias = Asistencia.query.filter(Asistencia.idestudiante == estudiante.id, Asistencia.asistio == "n").all()
    
    return render_template("hijo.html", estudiante = estudiante, inasistencias = inasistencias, total = len(inasistencias))
    

@app.route("/listadoAsistencia", methods=['GET', 'POST'])

def listadoAsistencia():
        
    if request.method == 'POST':
        
        curso_id = request.form['curso']
        estudiantes = Estudiante.query.filter(Estudiante.idcurso == curso_id).order_by(Estudiante.apellido).all()
        ids_estudiantes = [estudiante.id for estudiante in estudiantes]
        clase = request.form['clase']
        fecha = request.form['fecha']
        asistencias = Asistencia.query.filter(Asistencia.codigoclase == clase , Asistencia.idestudiante.in_(ids_estudiantes)).all()
            
        return render_template("listado_de_fecha.html", data = zip(estudiantes,asistencias))
    
    else:
        
        return render_template("index.html")
        

@app.route("/buscarEstudiantes", methods=['GET','POST']) # type: ignore
def buscarEstudiantes():

    if request.method == 'POST':
        id = request.form['curso']
        estudiantes = Estudiante.query.filter(Estudiante.idcurso == id).order_by(Estudiante.apellido).all()

        aulaPresente ,eduFPresente, aulaJust, eduFJust, aulaInjust, eduFInjust = [], [], [], [], [], []

        
        aulaPContador, eduPContador, aulaContadorJust, aulaContadorInjust, eduAContadorJust, eduAContadorInjust = 0, 0, 0, 0, 0, 0
        
        for i, estudiante in enumerate(estudiantes):
            
            asistencias = Asistencia.query.filter(Asistencia.idestudiante == estudiante.id).all()
            
            for asistencia in asistencias:
                
                
                if asistencia.asistio == "s" and asistencia.codigoclase == 1:
                    
                    aulaPContador += 1

                elif asistencia.asistio == "s" and asistencia.codigoclase == 2:
                    
                    eduPContador += 1

                elif asistencia.asistio == "n" and asistencia.codigoclase == 1 and asistencia.justificacion != "":

                    aulaContadorJust += 1
                
                elif asistencia.asistio == "n" and asistencia.codigoclase == 1 and asistencia.justificacion == "":
                    
                    aulaContadorInjust += 1
                    
                elif asistencia.asistio == "n" and asistencia.codigoclase == 2 and asistencia.justificacion != "":
                    
                    eduAContadorJust += 0.5
                
                elif asistencia.asistio == "n" and asistencia.codigoclase == 2 and asistencia.justificacion == "":
                
                    eduAContadorInjust += 1
                
            aulaPresente.append(aulaPContador)
            eduFPresente.append(eduPContador)
            aulaJust.append(aulaContadorJust)
            eduFJust.append(eduAContadorJust)
            aulaInjust.append(aulaContadorInjust)
            eduFInjust.append(eduAContadorInjust)
            
            aulaPContador = 0
            eduPContador = 0
            aulaContadorJust = 0
            eduAContadorJust = 0
            aulaContadorInjust = 0
            eduAContadorInjust = 0
            
            session['data'] = [(estudiante.to_json(), aulaP, eduP, aulaJ, eduJ, aulaI, eduI)
                           for estudiante, aulaP, eduP, aulaJ, eduJ, aulaI, eduI in zip(
                               estudiantes, aulaPresente, eduFPresente, aulaJust, eduFJust, aulaInjust, eduFInjust)]
            
            session['band'] = True
            
        return render_template("listado.html",data = zip(estudiantes,aulaPresente,eduFPresente,aulaJust,eduFJust,aulaInjust,eduFInjust), band = True)

    
    elif request.method == 'GET':
        serialized_estudiante = session.get('estudiante')
        serialized_inasistencias = session.get('inasistencias')
        total = session.get('total')
        data = session.get('data')
        band = session.get('band')

        estudiantes = []
        inasistencias = []

        if serialized_estudiante:
            estudiante_dict = json.loads(serialized_estudiante)
            estudiante = Estudiante.from_dict(estudiante_dict)
            estudiantes.append(estudiante)

        if serialized_inasistencias:
            inasistencias_dicts = json.loads(serialized_inasistencias)
            inasistencias = [Asistencia.from_dict(inasistencia_dict) for inasistencia_dict in inasistencias_dicts]

        if data:
            estudiantes = [estudiante for estudiante, _, _, _, _, _, _ in data]
            inasistencias = [inasistencias for _, _, _, _, inasistencias, _, _ in data]
            total = len(inasistencias)

        return render_template("listado.html", data=data, band=band, estudiantes=estudiantes,
                               inasistencias=inasistencias, total=total)
    
@app.route("/asistencia/<int:estudiante_id>")
def asistencia(estudiante_id):

    return render_template("asistencia.html", asistencias = Asistencia.query.filter(Asistencia.idestudiante == estudiante_id).all() ,band = True)

@app.route("/registrarEstudiante", methods=['POST'])
def registrarEstudiante():
    date = request.form['fecha']
    id_curso = request.form['curso']
    asistencia_total = Estudiante.query.filter(Estudiante.idcurso == id_curso).count()
            
    asistencia = Asistencia.query.filter(Asistencia.fecha == date, Asistencia.codigoclase == int(request.form['clase'])).first()
    asistencia_parcial = Asistencia.query.filter(Asistencia.fecha == date, Asistencia.codigoclase == int(request.form['clase'])).count()
    
    if asistencia:
       
        estudiante = Estudiante.query.filter(Estudiante.id == asistencia.idestudiante).first()
        
        if estudiante.idcurso != int(id_curso) or asistencia_parcial< asistencia_total:
            c = ""
            
            if request.form['clase'] == "1":
                c = "Aula"
            else:
                c = "Educación Física"
            
            estudiantes = Estudiante.query.filter(Estudiante.idcurso == id_curso).all()
            estudiantes_json = json.dumps([estudiante.to_json() for estudiante in estudiantes])
            
            return render_template("listado.html", estudiantes=estudiantes, estudiantes_json=estudiantes_json, clase=c, fecha=date, ID=id_curso, asistencias=Asistencia.query.filter(Asistencia.fecha == date, Asistencia.codigoclase == int(request.form['clase'])).all(), band=False)
        
        else:
            serialized_padre = session.get('padre')
            serialized_preceptor = session.get('preceptor')
            serialized_cursos = session.get('cursos')
            band = session.get('band')
            cursos = []
            preceptor = None
            padre = None
            
            if serialized_padre:
                padre_id = json.loads(serialized_padre)['id']
                padre = Padre.query.filter(Padre.id == padre_id).first()
            
            if serialized_preceptor:
                preceptor_id = json.loads(serialized_preceptor)['id']
                preceptor = Preceptor.query.filter(Preceptor.id == preceptor_id).first()
            
            if serialized_cursos:
                cursos = [Curso.query.get(curso_dict['id']) for curso_dict in json.loads(serialized_cursos)]
        
            return render_template("index.html", error="El curso ya tiene registrada la asistencia en esta fecha.", cursos=cursos, padre=padre, precept=preceptor, band=band, band3=True)
    
    else:
        c = ""
        
        if request.form['clase'] == "1":
            c = "Aula"
        else:
            c = "Educación Física"
        
        estudiantes = Estudiante.query.filter(Estudiante.idcurso == id_curso).all()
        estudiantes_json = json.dumps([estudiante.to_json() for estudiante in estudiantes])
        
        return render_template("listado.html", estudiantes=estudiantes, estudiantes_json=estudiantes_json, clase=c, fecha=date, ID=id_curso, asistencias=Asistencia.query.filter(Asistencia.fecha == date, Asistencia.codigoclase == int(request.form['clase'])).all(), band=False)

@app.route("/registrarAsistencia", methods=['POST'])
def registrarAsistencia():
    
    clase = request.form['clase']
    idestudiante = request.form['idestudiante']
    fecha = request.form['fecha']
    codigoclase = request.form['codigoclase']
    asistio = request.form['asistencia']

    estudiantes_json = request.form['estudiantes']
    estudiantes = [Estudiante.from_json(json_data) for json_data in json.loads(estudiantes_json)]

    
    # Verificar si el campo de justificación está presente en request.form
    if 'justificacion' in request.form:
        justificacion = request.form['justificacion']
    else:
        justificacion = ''  # Asignar una cadena vacía si no está presente
    
    
    
    # Crear un nuevo objeto Asistencia con los datos del formulario
    nueva_asistencia = Asistencia(
        fecha = datetime.strptime(fecha, '%Y-%m-%d'),
        codigoclase = int(codigoclase),
        asistio = asistio,
        justificacion = justificacion,
        idestudiante = int(idestudiante)
    )
    # Guardar la nueva asistencia en la base de datos
    db.session.add(nueva_asistencia)
    db.session.commit()
    
    
    return render_template("listado.html",estudiantes = estudiantes,estudiantes_json = estudiantes_json,fecha = fecha,clase = clase, asistencias = Asistencia.query.filter(Asistencia.fecha == fecha , Asistencia.codigoclase == int(codigoclase)).all(), band = False)


if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()
    app.run(debug = True)	