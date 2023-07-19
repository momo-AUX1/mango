from wsgiref.simple_server import make_server
import json
from os.path import join
import sqlite3
from urllib.parse import parse_qs

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

    elif req == 'application/x-www-form-urlencoded':
      length = int(environ.get('CONTENT_LENGTH', 0))
      body = environ['wsgi.input'].read(length).decode('utf-8')
      data = parse_qs(body)
      response = routes[path](data)
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
        if content_type == 'redirect':
          start_response('302 Found', [('Content-Type', 'text/html'), ('Location', f'{response}')])
        else:
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


def get_data(info,query):
  data = info[query][0]
  return data


def send_file(path):
  try:
    with open(join(files_path, path), 'rb') as f:
      response = f.read()
  except:
    with open(path, 'rb') as f:
      response = f.read()
  return response, 'application/octet-stream', path


def redirect(link):
  return link, 'redirect'

# Default page

html = """
<!DOCTYPE html>
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

        .link {
            color: orange;
            text-decoration: underline;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Server successfully started, but there are no routes or the "/" route is empty</h1>
    <img class="mango-img" src="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0" alt="Mango">
    <footer>
        Version: 0.7.6
        <br>
        <a class="link" href="https://pypi.org/project/mango-framework/">Check out the development!</a>
    </footer>
</body>
</html>
"""


#Native User DB 

class User:
    def __init__(self):
      self.conn = sqlite3.connect('DB.sqlite')
      self.conn.execute('CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, firstname TEXT, lastname TEXT, email TEXT, password TEXT)')

    def insert(self, username=None, firstname=None, lastname=None, email=None, password=None):
        self.conn.execute('INSERT INTO Users (username, firstname, lastname, email, password) VALUES (?,?,?,?,?)',
                     (username, firstname, lastname, email, password))
        self.conn.commit()

    def search(self, search):
        search_term = f"%{search}%"
        result = self.conn.execute('SELECT * FROM Users WHERE username LIKE ? OR firstname LIKE ? OR lastname LIKE ? OR email LIKE ? OR password LIKE ?',
                              (search_term, search_term, search_term, search_term, search_term))
        return result.fetchall()

    def delete(self, search):
        search_term = f"%{search}%"
        self.conn.execute('DELETE FROM Users WHERE username LIKE ? OR firstname LIKE ? OR lastname LIKE ? OR email LIKE ? OR password LIKE ?',
                     (search_term, search_term, search_term, search_term, search_term))
        self.conn.commit()

    def get_user_by_username(self, username):
        result = self.conn.execute('SELECT * FROM Users WHERE username = ?', (username,))
        return result.fetchone()
    
    def get_user_by_firstname(self, firstname):
        result = self.conn.execute('SELECT * FROM Users WHERE firstname = ?', (firstname,))
        return result.fetchone()
    
    def get_user_by_lastname(self, lastname):
        result = self.conn.execute('SELECT * FROM Users WHERE lastname = ?', (lastname,))
        return result.fetchone()
    
    def get_user_by_email(self, email):
        result = self.conn.execute('SELECT * FROM Users WHERE email = ?', (email,))
        return result.fetchone()
    
    def get_user_by_password(self, password):
        result = self.conn.execute('SELECT * FROM Users WHERE password = ?', (password,))
        return result.fetchone()

#Native template engine Shake! 

class Shake:
  def render(self,template,context=None):
    try:
      with open(join(templates_path, template), 'r') as f:
        template = f.read()
    except:
      try:
        with open(join(template), 'r') as f:
          template = f.read()
      except:
        pass
    if context is None:
      context = {}
    for key, value in context.items():
      placeholder = f"{{{{{key}}}}}"
      template = template.replace(placeholder, str(value))
    
    return template
  


# native Shake template engine 

  #def render(template, context=None):
 #   if context is None:
 #       context = {}
  #  for key, value in context.items():
  #      placeholder = f"{{{{{key}}}}}"
   #     template = template.replace(placeholder, str(value))
   # return template
