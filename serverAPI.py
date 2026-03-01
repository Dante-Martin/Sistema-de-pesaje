from flask import Flask,request,jsonify,render_template,redirect, url_for,session
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

app.secret_key = 'star'  # Necesario para usar sesiones

CORS(app,supports_credentials=True)  #Esto permite solicitudes desde cualquier origen, como http://127.0.0.1:5500 # Permitir credenciales (cookies/sesiones) en CORS  

 # Ruta de la base de datos (se crea automáticamente)
DATABASE = 'database.db'

# Función para ejecutar consultas SQL
def query_db(query, args=(), one=False): # args=() indica que no hay argumentos para los placeholders -> ? , one=False → Si es True, la función devolverá solo un registro; si es False, devolverá todos los registros.
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor() #interprete entre las sentencias SQL escritas en python con SQLite
    cursor.execute(query, args)# ejecuta la consulta SQL segun los parametros.  
    conn.commit()# guarda cambios en el archivo de base de datos 
    results = cursor.fetchall() # devuelve lista de tuplas
    conn.close()
    return (results[0] if results else None) if one else results #Si one=False, devuelve toda la lista results.

# Crear tabla de usuarios (solo una vez)
def init_db():
    query_db('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT DEFAULT "user" NOT NULL
        )
    ''')
    query_db('''
        CREATE TABLE IF NOT EXISTS prod (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            grupo TEXT DEFAULT "generico" NOT NULL
        )
    ''')
    
    print("Tabla users y prod creada/existe.")
    
# Inicializar la BD al iniciar el servidor
with app.app_context():
    init_db()   
        
#usuario default
    query_db('''
            INSERT INTO users (username, password, rol) 
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO NOTHING
        ''', ("1", "1", "admin"))
    

    
# Ruta principal - GET
@app.route('/')
def index():
    return render_template('login.html')


# verificar un nuevo usuario - POST
@app.route('/autenticacion', methods=['POST'])
def verificar_usuario():
    print(request)
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    if not username or not password:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    print(username)
    
    user = query_db('''
        SELECT rol
        FROM users
        WHERE username = ? AND password = ?
    ''', (username, password), one=True)
    if  user:
        print(f"Usuario {username} autenticado exitosamente")
        session['logged_in'] = True
        session['username'] = username
        print(f"Sesión establecida: {session}")
        
        if user == "admin":
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user'))
    else:
        print(f"Autenticación fallida para {username}")
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

# Ruta protegida para administrador.html
@app.route('/admin')
def admin():
    print(f"Accediendo a /admin, sesión: {session.get('logged_in')}")
    if not session.get('logged_in'):
        print("No autenticado, redirigiendo a login")
        return redirect(url_for('index'))
    return render_template('administrador.html')

# Ruta protegida para usuario.html
@app.route('/user')
def user():
    print(f"Accediendo a /user, sesión: {session.get('logged_in')}")
    if not session.get('logged_in'):
        print("No autenticado, redirigiendo a login")
        return redirect(url_for('index'))
    return render_template('administrador.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    print(f"Cerrando sesión, sesión actual: {session}")
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))


# Ruta para listar usuarios - GET
@app.route('/api/users', methods=['GET'])
def get_users():
    if not session.get('logged_in'):
        return jsonify({"error": "No autorizado"}), 401
    users = query_db('SELECT id, username, rol FROM users')
    return jsonify([{"id": user[0], "username": user[1], "rol": user[2]} for user in users]), 200

# Ruta para crear usuario - POST
@app.route('/api/users', methods=['POST'])
def create_user():
    if not session.get('logged_in'):
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    rol = data.get('rol')
    if not username or not password:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    try:
        query_db('INSERT INTO users (username, password, rol) VALUES (?, ?, ?)', (username, password, rol))
        print(f"Usuario {username} creado exitosamente")
        return jsonify({"message": "Usuario creado exitosamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El nombre de usuario ya existe"}), 400

# Ruta para actualizar usuario - PUT
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if not session.get('logged_in'):
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    rol = data.get("rol")
    if not username or not password:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    try:
        print('UPDATE users SET username = ?, password = ?, rol= ? WHERE id = ?', (username, password, rol, user_id))
        query_db('UPDATE users SET username = ?, password = ?, rol= ? WHERE id = ?', (username, password, rol, user_id))
        print(f"Usuario ID {user_id} actualizado")
        return jsonify({"message": "Usuario actualizado exitosamente"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "El nombre de usuario ya existe"}), 400

# Ruta para eliminar usuario - DELETE
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not session.get('logged_in'):
        return jsonify({"error": "No autorizado"}), 401
    # Evitar eliminar al usuario actual
    if session.get('username') == query_db('SELECT username FROM users WHERE id = ?', [user_id], one=True)[0]:
        return jsonify({"error": "No puedes eliminar tu propio usuario"}), 403
    query_db('DELETE FROM users WHERE id = ?', [user_id])
    print(f"Usuario ID {user_id} eliminado")
    return jsonify({"message": "Usuario eliminado exitosamente"}), 200


# Configuración y ejecución del servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)