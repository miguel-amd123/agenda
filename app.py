from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy

import os
# Modulo para correo electrónico
from flask_mail import Mail
from flask_mail import Message
# Cifrar contraseña
from flask_bcrypt import Bcrypt

# Para manejo de sesiones
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.debug = True
# Permito que la aplicación a través de la instancia de la clase Bcrypt pueda 
bcrypt = Bcrypt()
bcrypt.init_app(app)

# Configuración de la app  para manejar  sesión
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.log_view='login'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# conexion base de datos
db = SQLAlchemy(app)
# app.config['SQLALCHEMY_DATABASE_URI']='postgresql+psycopg2://postgres:12345@localhost:5432/agenda'
app.config['SQLALCHEMY_DATABASE_URI']='postgres://ubupdjjyeuyfzc:1e0ca4fddf6edf312dde35c053bb6982ef98b4a2c3a3e5939f3ee0dca1ac7831@ec2-52-2-82-109.compute-1.amazonaws.com:5432/d3r00v1ev00nr7'
app.config['SQLALCHEMY_TRACK_NOOTIFICATIONS']=False
# hasta Aquí

#esta seccion es la configuracion del correo

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '15460179@colima.tecnm.mx'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



# esta seccion es base de datos las tablas

class usuarios(db.Model):
	usuario_id = db.Column(db.Integer, primary_key=True)
	usuario_name = db.Column(db.String(500),unique=True, nullable=False, index=True)
	usuario_passw = db.Column(db.String(500))
#declarasion de las secciones 
	def is_authenticated(self):
		return True
	
	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False
	
	def get_id(self):
		return str(self.usuario_id)
#Hasta Aquí

class agendas(db.Model):
	agendas_id = db.Column(db.Integer, primary_key=True)
	agenda_name = db.Column(db.String(50))

class contacto(db.Model):
	contacto_id = db.Column(db.Integer, primary_key=True)
	contacto_name = db.Column(db.String(50))
	telefono = db.Column(db.Integer)
	email = db.Column(db.String(50))
	calle = db.Column(db.String(50))
	numero = db.Column(db.Integer)
	colonia = db.Column(db.String(50))
	localidad = db.Column(db.String(50))
	municipio = db.Column(db.String(50))
	estado = db.Column(db.String(50))

# Relacion
	# agendas_id = db.Column(db.Integer, db.ForeignKey('agendas_id'))
# hasta Aquí

# Vistas de la aplicacion
@app.route("/loginin" , methods=['GET','POST'])
def loginin():
	if request.method == 'POST':
		# Query filter_by por usuario_name
		login = request.form["login"]
		passw = request.form["passw"]
		usuario_exite = usuarios.query.filter_by(usuario_name=login).first()
		# mensaje= usuario_exite.usuario_name
		#Si lo encuentra entonces
		if usuario_exite != None:
			print("Existe")
			if bcrypt.check_password_hash(usuario_exite.usuario_passw, passw):
				print("Usuario autenticado")
				# Aquí se agregó el método login_user para vincular
				# el usuario autenticado a la sesión
				login_user(usuario_exite)
				
				if current_user.is_authenticated:
					flash("Inicio de Sesión Exitoso!!")
					return redirect("/menu")
		else:
			mensaje = "No existe ese correo por favor registrate"
			return render_template("login.html", mensaje = mensaje)						
		return render_template("login.html")
	print("Login in...")
	return render_template("login.html")


@login_manager.user_loader
def load_user(user_id):
 	return usuarios.query.filter_by(usuario_id=user_id).first()

@app.route('/')
def login():
	return render_template("login.html")

@app.route('/menu')
def menu():
	return render_template("menu.html")

@app.route('/nueva_agenda',methods=['GET','POST'])
def nueva_agenda():
	if request.method == "POST":
		campo_agenda_name = request.form['nombre_a']
		agenda = agendas(agenda_name = campo_agenda_name)
		db.session.add(agenda)
		db.session.commit()
		return render_template("nuevo_contacto.html")
	return render_template("nueva_agenda.html")	

@app.route('/nuevo_contacto', methods=['GET','POST'])
def nuevo_contacto():
	if request.method =="POST":

		campo_contacto_name = request.form['nombre']
		campo_telefono = request.form['telefono']
		campo_email = request.form['email']
		campo_calle = request.form['calle']
		campo_numero = request.form['numero']
		campo_colonia = request.form['colonia']
		campo_localidad = request.form['localidad']
		campo_municipio = request.form['municipio']
		campo_estado = request.form['estado']
		contactos = contacto(contacto_name=campo_contacto_name,telefono=campo_telefono,email=campo_email,
		calle=campo_calle,numero=campo_numero,colonia=campo_colonia,localidad=campo_localidad,
		municipio=campo_municipio,estado=campo_estado)
		db.session.add(contactos)
		db.session.commit()
		mensaje = "Contacto agregado exitosamente"
		return render_template("menu.html", mensaje = mensaje)
	return render_template("nuevo_contacto.html")

# seccion para eliminar datos 
@app.route('/eliminar/<contacto_id>')
def eliminar(contacto_id):
	reg = contacto.query.filter_by(contacto_id = contacto_id).delete()
	db.session.commit()
	return redirect(url_for('lista_contacto'))

@app.route('/borrar/<agendas_id>')
def borrar(agendas_id):
	reg1 = agendas.query.filter_by(agendas_id = agendas_id).delete()
	db.session.commit()
	return redirect(url_for('lista_contacto'))	
# seccion para editar los contactos
@app.route('/editar_contacto/<contacto_id>')
def editar_contacto(contacto_id):
	reg = contacto.query.filter_by(contacto_id = contacto_id).first() 
	return render_template("editar_contacto.html", contactos = reg)			
# Seccion mostrar los datos almacenados
@app.route('/lista_contacto')
def lista_contacto():
	consulta = contacto.query.all()
	consultar = agendas.query.all()
	return render_template("lista_contacto.html",arg = consulta, a = consultar)

# Seccion de actualizar los datos 
@app.route('/actualizar', methods=['GET','POST'])
def actualizar():
	if request.method == "POST":
		query = contacto.query.get(request.form['contacto_id'])
		query.contacto_name = request.form['nombre']
		query.telefono = request.form['telefono']
		query.email = request.form['email']
		query.calle = request.form['calle']
		query.numero = request.form['numero']
		query.colonia = request.form['colonia']
		query.localidad = request.form['localidad']
		query.municipio = request.form['municipio']
		query.estado =  request.form['estado']
		db.session.commit()
		return redirect(url_for('lista_contacto'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
	mensaje = ""
	msg=""
	if request.method=='POST':
		passw = request.form["passw"]
		confirmar = request.form["confirmar"]
		if passw != confirmar:
			mensaje = "Contraseñas no coinciden, intenta de nuevo!"
			return render_template("registro.html", mensaje = mensaje)
		else:
			#Crear usuario en la base de datos
			usuario_name=request.form["nombre_usuario"]
			usuario_passw = request.form["passw"]
			# Crear objeto para el registro del usuario
			usuario = usuarios(
				usuario_name = usuario_name,
				usuario_passw = bcrypt.generate_password_hash(usuario_passw).decode('utf-8')
			)
			db.session.add(usuario)
			db.session.commit()
			mensaje = "Usuario registrado!"
			#Enviar correo
			msg = Message("Gracias por registrarte en tu agenda personal", sender="15460179@colima.tecnm.mx", recipients=[usuario_name])
			msg.body = "Este es un email de prueba"
			msg.html = "<p>Gracias por registrarte y usar la aplicacion de agenda con el correo 15460179@colima.tecnm.mx </p>"
			mail.send(msg)
			return render_template("registro.html", mensaje = mensaje)
	return render_template("registro.html", mensaje = mensaje)





# Hasta Aquí

if __name__ == "__main__":
	db.create_all()
	app.run()