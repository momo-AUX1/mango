from wsgiref.simple_server import make_server
import json
from os.path import join
import sqlite3
from urllib.parse import parse_qs
import mimetypes
import cgi

templates_path : str = 'templates'

files_path : str = 'files'

static_path : str = 'static'

static_url : str = "/static"

static : bool = True

# Default route

def index():
  return html

routes : dict = {'/': index}

# Decorator for route registration

def route(path : str):

  def decorator(func : callable):

    routes[path] = func

    return func

  return decorator

# HTTP Response constants

OK : tuple = ('200 OK', [('Content-type', 'text/html')])

NOT_FOUND : tuple = ('404 NOT FOUND', [('Content-Type', 'text/html')])

FORBIDDEN : tuple = ('403 FORBIDDEN', [('Content-Type', 'text/html')])

NOT_ALLOWED : tuple = ('405 NOT ALLOWED', [('Content-Type', 'text/html')])

#Default HTTP response pages

page_404 : str = "<h1>404 NOT FOUND</h1>"

# Main application function

def app(environ, start_response):
  global response
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

            form_fields = {key: value[0] for key, value in data.items()}

            response = routes[path](form_fields) 
            start_response(*OK)

    elif req.startswith('multipart/form-data'):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
        formfields = {}
        files = []
        for key in form:
            if form[key].filename:  

                fileitem = form[key]
                files.append(fileitem)
            else:

                formfields[key] = form.getvalue(key)

        response = routes[path](formfields, files)
        start_response(*OK)


    else:
      response = "<h1> NOT ALLOWED </h1>"
      start_response(*NOT_ALLOWED)

  elif path in routes and method == 'GET':
    try:
      response, content_type, filename = routes[path]()
      if content_type == 'application/octet-stream':
        start_response(
          '200 OK',
          [('Content-Type', content_type),
          ('content-disposition', f'attachment; filename={filename}')])
      else:
         start_response(
                '200 OK',
                [('Content-Type', content_type),
                ('content-disposition', f'filename={filename}')])
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

  
  #NEW STATIC !!!!!

  elif path.startswith(static_url) and method == "GET" and static:
        try:
            with open(join(static_path, path.split('/')[2]), 'rb') as f:
                response = f.read()
                mime_type, _ = mimetypes.guess_type(path)
                start_response('200 OK', [('Content-Type', mime_type)])
        except:
            try:
             with open(path.split('/')[2], 'rb') as f:
                response = f.read()
                mime_type, _ = mimetypes.guess_type(path)
                start_response('200 OK', [('Content-Type', mime_type)])
            except:
              response = page_404
              start_response(*NOT_FOUND)

  else:
    response = page_404 
    start_response(*NOT_FOUND)

  try:
    if isinstance(response, tuple):
        response_data, content_type = response
        if content_type == 'application/json':
            return [response_data.encode('utf-8')]
    return [response.encode()]
  except:
    return [response]

# Function to run the application

def run(host:str = '127.0.0.1', port:int = 5000):
  server = make_server(host, port, app)
  print(f'Running at http://{host}:{port}')
  server.serve_forever()

# Helper functions

def render(template:str, context:dict = None) -> str :
    try:
      with open(join(templates_path, template), 'r') as f:
        template = f.read()
    except:
      try:
        with open(template, 'r') as f:
          template = f.read()
      except:
        pass
    if context is None:
      context = {}
    for key, value in context.items():
      placeholder = f"{{{{{key}}}}}"
      template = template.replace(placeholder, str(value))
    
    return template


def get_json(data:str) -> dict:
  return json.loads(data)


def send_json(data:str) -> dict:
     return json.dumps(data), 'application/json'


def save_file(data:bytes, name:str, path:str = None) -> None:
    if isinstance(data, bytes):
        content = data
    elif isinstance(data, cgi.FieldStorage):
        content = data.file.read()
    else:
        raise ValueError(f"Invalid data format. Expected bytes or FieldStorage object. got {type(data)}")
    
    if path is None:
        with open(name, 'wb') as f:
            f.write(content)
    elif path:
        with open(join(path, name), 'wb') as f:
            f.write(content)
         

def send_file(path:str, as_attachment:str = False) -> bytes:
  if as_attachment:
    try:
      with open(join(files_path, path), 'rb') as f:
        response = f.read()
        return response, 'application/octet-stream', path
    except:
      try:
          with open(path, 'rb') as f:
            response = f.read()
          return response, 'application/octet-stream', path
      except:
        raise FileNotFoundError(f"File {path} not found at the specified directory.")
  else:
        try:
            with open(join(files_path, path),'rb') as f:
             response = f.read()
        except:
          
           with open(path, 'rb') as f:
              response = f.read()
        try:
          mime_type, _ = mimetypes.guess_type(path)
          return response, mime_type, path
        except:
           raise FileNotFoundError(f"File {path} not found at the specified directory.")


def redirect(link:str) -> str:
  return link, 'redirect'

def set_404(info:str ="<h1>404 NOT FOUND</h1>") -> str:
   global page_404
   try:
      with open(join(templates_path, info), 'r') as f:
         page_404 = f.read()
   except:
    try:
       with open(info, 'r') as f:
         page_404 = f.read()
    except:
      page_404 = str(info)

def set_static_url(url:str) -> str:
   global static_url
   static_url = url

def enable_static(value:bool = None):
    global static
    if isinstance(value, bool):
      static = value
    else:
       raise ValueError(f"Expected Boolean value got {type(value)}")


# Default page

html : str = """
<!DOCTYPE html>
<html>
<head>
    <link rel="icon" type="image/x-icon" href="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mango</title>
    <style>
        :root {
            --background-color-light: white;
            --text-color-light: orange;
            --background-color-dark: #121212;
            --text-color-dark: orange;
        }

        body {
            background-color: var(--background-color-light);
            color: var(--text-color-light);
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

        @media (prefers-color-scheme: dark) {
            body {
                background-color: var(--background-color-dark);
                color: var(--text-color-dark);
            }
            footer {
                background-color: rgb(52, 52, 52);
                color: white;
            }
        }
    </style>
</head>
<body>
    <h1>Server successfully started, but there are no routes or the "/" route is empty</h1>
    <img class="mango-img" src="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0" alt="Mango">
    <footer>
        Version: 1.1.1
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

    def insert(self, username : str = None, firstname : str = None, lastname : str = None, email : str = None, password : str = None):
        self.conn.execute('INSERT INTO Users (username, firstname, lastname, email, password) VALUES (?,?,?,?,?)',
                     (username, firstname, lastname, email, password))
        self.conn.commit()

    def search(self, search:str):
        search_term = f"%{search}%"
        result = self.conn.execute('SELECT * FROM Users WHERE username LIKE ? OR firstname LIKE ? OR lastname LIKE ? OR email LIKE ? OR password LIKE ?',
                              (search_term, search_term, search_term, search_term, search_term))
        return result.fetchall()

    def delete(self, search:str):
        search_term = f"%{search}%"
        self.conn.execute('DELETE FROM Users WHERE username LIKE ? OR firstname LIKE ? OR lastname LIKE ? OR email LIKE ? OR password LIKE ?',
                     (search_term, search_term, search_term, search_term, search_term))
        self.conn.commit()

    def get_user_by_username(self, username:str):
        result = self.conn.execute('SELECT * FROM Users WHERE username = ?', (username,))
        return result.fetchone()
    
    def get_user_by_firstname(self, firstname:str):
        result = self.conn.execute('SELECT * FROM Users WHERE firstname = ?', (firstname,))
        return result.fetchone()
    
    def get_user_by_lastname(self, lastname:str):
        result = self.conn.execute('SELECT * FROM Users WHERE lastname = ?', (lastname,))
        return result.fetchone()
    
    def get_user_by_email(self, email:str):
        result = self.conn.execute('SELECT * FROM Users WHERE email = ?', (email,))
        return result.fetchone()
    
    def get_user_by_password(self, password:str):
        result = self.conn.execute('SELECT * FROM Users WHERE password = ?', (password,))
        return result.fetchone()
    
    def raw_sql_exec(self, query:str):
       self.conn.execute(query)
