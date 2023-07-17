from wsgiref.simple_server import make_server
import json
from os.path import join
import sqlite3

templates_path = 'templates'

files_path = 'files'

# Default route

def index():
  return html


routes = {'/': index}

# Decorator for route registration

def route(path):

  def decorator(func):

    routes[path] = func

    return func

  return decorator


# HTTP Response constants

OK = ('200 OK', [('Content-type', 'text/html')])

NOT_FOUND = ('404 NOT FOUND', [('Content-Type', 'text/html')])

FORBIDDEN = ('403 FORBIDDEN', [('Content-Type', 'text/html')])

NOT_ALLOWED = ('405 NOT ALLOWED', [('Content-Type', 'text/html')])

# Main application function

def app(environ, start_response):
  path = environ['PATH_INFO']
  method = environ['REQUEST_METHOD']
  req = environ['CONTENT_TYPE']

  if path in routes and method == 'POST':
    if req == 'application/json':
      length = int(environ.get('CONTENT_LENGTH', 0))
      body = environ['wsgi.input'].read(length).decode('utf-8')
      response = routes[path](body)
      start_response(*OK)
    else:
      response = "<h1> NOT ALLOWED </h1>"
      start_response(*NOT_ALLOWED)
  elif path in routes and method == 'GET':
    try:
      response, content_type, filename = routes[path]()
      start_response(
        '200 OK',
        [('Content-Type', content_type),
         ('content-disposition', f'attachment; filename={filename}')])
    except:
      try:
        response, content_type = routes[path]()
        start_response('200 OK', [('Content-Type', content_type)])
      except:
        response = routes[path]()
        start_response(*OK)
  else:
    response = "<h1>404 NOT FOUND</h1>"
    start_response(*NOT_FOUND)

  try:
    return [response.encode()]
  except:
    return [response]

# Function to run the application

def run(host='127.0.0.1', port=5000):
  server = make_server(host, port, app)
  print(f'Running at http://{host}:{port}')
  server.serve_forever()

# Helper functions

def render(path):
  try:
    with open(join(templates_path, path), 'r') as f:
      response = f.read()
  except:
    with open(path, 'r') as f:
      response = f.read()
  return response


def get_json(data):
  return json.loads(data)


def send_json(data):
  return json.dumps(data), 'application/json'


def send_file(path):
  try:
    with open(join(files_path, path), 'rb') as f:
      response = f.read()
  except:
    with open(path, 'rb') as f:
      response = f.read()
  return response, 'application/octet-stream', path


def redirect(link):
  return f"<script>window.location.href = '{link}'</script>"

# Default page

html = """<!DOCTYPE html>
<html>
<head>
    <title>Mango Server</title>
    <style>
        body {
            background-color: white;
            color: orange;
            text-align: center;
            font-family: Arial, sans-serif;
            margin-top: 150px;
        }

        h1 {
            font-size: 24px;
        }

        footer {
            background-color: #f5f5f5;
            padding: 10px;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 12px;
            color: #888;
        }

        .mango-img {
            width: 150px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <h1>Server successfully started, but there are no routes or the "/" route is empty</h1>
    <img class="mango-img" src="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0" alt="Mango">
    <footer>
        Version: 0.5
    </footer>
</body>
</html>"""


#Native User DB 

conn = sqlite3.connect('databse.sqlite')

conn.execute('CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, firstname TEXT, lastname TEXT, email TEXT, password TEXT)')

def user():
    def insert(username=None, firstname=None, lastname=None, email=None, password=None):
        conn.execute('INSERT INTO Users (username, firstname, lastname, email, password) VALUES (?,?,?,?,?)',
                     (username, firstname, lastname, email, password))
        conn.commit()

    def search(search):
        search_term = f"%{search}%"
        result = conn.execute('SELECT * FROM Users WHERE username LIKE ? OR firstname LIKE ? OR lastname LIKE ? OR email LIKE ? OR password LIKE ?',
                              (search_term, search_term, search_term, search_term, search_term))
        return result.fetchall()

    def delete(search):
        search_term = f"%{search}%"
        conn.execute('DELETE FROM Users WHERE username LIKE ? OR firstname LIKE ? OR lastname LIKE ? OR email LIKE ? OR password LIKE ?',
                     (search_term, search_term, search_term, search_term, search_term))
        conn.commit()

    def get_user_by_username(username):
        result = conn.execute('SELECT * FROM Users WHERE username = ?', (username,))
        return result.fetchone()
    
    def get_user_by_firstname(firstname):
        result = conn.execute('SELECT * FROM Users WHERE firstname = ?', (firstname,))
        return result.fetchone()
    
    def get_user_by_lastname(lastname):
        result = conn.execute('SELECT * FROM Users WHERE lastname = ?', (lastname,))
        return result.fetchone()
    
    def get_user_by_email(email):
        result = conn.execute('SELECT * FROM Users WHERE email = ?', (email,))
        return result.fetchone()
    
    def get_user_by_password(password):
        result = conn.execute('SELECT * FROM Users WHERE password = ?', (password,))
        return result.fetchone()

    return insert, search, delete, get_user_by_username, get_user_by_firstname, get_user_by_lastname, get_user_by_email, get_user_by_password
