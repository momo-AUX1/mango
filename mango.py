import threading
from wsgiref.simple_server import make_server
import json
from os.path import join
from urllib.parse import parse_qs
import mimetypes
import cgi
import os
import sys
import time

try:
   from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
   __jinja2__ = True
except:
    pass

templates_path : str = 'templates'

files_path : str = 'files'

static_path : str = 'static'

static_url : str = "/static"

static : bool = True

static_permissive : bool = False

debug : bool = False

debug_info : str = ""

__version__ : str = '1.5.2'

__app_url__ : str = 'https://pypi.org/project/mango-framework/'

if __jinja2__:
    env = Environment(loader=FileSystemLoader(templates_path), autoescape=select_autoescape(['html', 'xml']))

# Default route

def index():
  return html

routes : dict = {'/': index}

# Decorator for route registration

def route(path : str):
  "Function to register a route. Expects a path in string format. Returns a decorator."

  def decorator(func : callable):
    "Decorator to register a route. Expects a function. Returns a function."
    global routes

    routes[path] = func

    return func

  return decorator

# HTTP Response constants

OK : tuple = ('200 OK', [('Content-type', 'text/html')])

NOT_FOUND : tuple = ('404 NOT FOUND', [('Content-Type', 'text/html')])

FORBIDDEN : tuple = ('403 FORBIDDEN', [('Content-Type', 'text/html')])

NOT_ALLOWED : tuple = ('405 NOT ALLOWED', [('Content-Type', 'text/html')])

INTERNAL_SERVER_ERROR : tuple = ('500 Internal Server Error', [('Content-Type', 'text/html')])

#Default HTTP response pages

page_404 : str = "<h1>404 NOT FOUND</h1>"

page_405 : str = "<h1>405 NOT ALLOWED</h1>"

page_500 : str = "<h1>500 Internal Server Error</h1>"


# ANSI escape codes to set text color
ESC = "\x1b["  # ANSI escape code
YELLOW_TEXT = ESC + "33;1m"  # Bright Yellow
BLUE_TEXT = ESC + "34;1m"  # Bright Blue
RED_TEXT = ESC + "35;1m" # Bright Red
GREEN_TEXT = ESC + "32;1m" # Bright Green
RESET = ESC + "0m"  # Reset to default color


# Main application function

def app(environ, start_response):
  try:
    global response
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']
    req = environ['CONTENT_TYPE']
    query_string = environ.get('QUERY_STRING', '')
    
    if '=' in query_string:
      get_params_unsanitzed = parse_qs(query_string)
      get_params = {k: v[0] if len(v) == 1 else v for k, v in get_params_unsanitzed.items()}
      print("get_params", get_params)
    else:
      get_params = {}


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
        response = page_405
        start_response(*NOT_ALLOWED)

    elif path in routes and method == 'GET':
      try:
        response, content_type, filename = routes[path]() if not get_params else routes[path](get_params) # Remove this if get params doesn't work
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
          response, content_type = routes[path]() if not get_params else routes[path](get_params) # Remove this if get params doesn't work
          if content_type == 'redirect':
            start_response('302 Found', [('Content-Type', 'text/html'), ('Location', f'{response}')])
          else:
            start_response('200 OK', [('Content-Type', content_type)])
        except:
          response = routes[path]() if not get_params else routes[path](get_params) # Remove this if get params doesn't work
          start_response(*OK)

    
    #NEW STATIC !!!!!

    elif path.startswith(static_url) and method == "GET" and static:
          try:
              with open(join(static_path, path.split('/')[2]), 'rb') as f:
                  response = f.read()
                  mime_type, _ = mimetypes.guess_type(path)
                  start_response('200 OK', [('Content-Type', mime_type)])
          except:
                if static_permissive:
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

    else:
      response = page_404 if not debug else html_404.format(route_table=generate_routes_table(), __version__=__version__, __app_url__=__app_url__)
      start_response(*NOT_FOUND)

    try:
      if isinstance(response, tuple):
          response_data, content_type = response
          if content_type == 'application/json':
              return [response_data.encode('utf-8')]
      return [response.encode()]
    except:
      return [response]
  
  except Exception as e:
    global debug_info
    print(f"{RED_TEXT}Error: {e} {RESET}")
    debug_info = str(e)  
    start_response(*INTERNAL_SERVER_ERROR)
    if debug:
        response_body = html_500.format(debug_info=debug_info, __version__=__version__, __app_url__=__app_url__)
    else:
        response_body = page_500
    return [response_body.encode()]

# Function to run the application

def run(host:str = '127.0.0.1', port:int = 5000, debug_mode=False) -> None:
  "Function to run the application. expects host in string format and port in integer format. If debug mode is set to True, it will show the error 500 page with the error details. Returns None"
  global debug
  debug = debug_mode
  server = make_server(host, port, app)
  print(f"{YELLOW_TEXT}This is a development server. Do not use it in a production deployment.{RESET}")

  if __jinja2__:
    print(f"{GREEN_TEXT}Jinja2 is installed. The app will use it to render templates.{RESET}")

  if debug:
    print(f"{BLUE_TEXT}Debug mode is on. The server will show debug info when a 404 or 500 errors occurs.{RESET}")
    monitor_thread = threading.Thread(target=monitor_changes, args=('.',), daemon=True)
    monitor_thread.start()

  print(f'Running at http://{host}:{port}')
  server.serve_forever()

# Helper functions

def render(template:str, context:dict = None) -> str :
    "Function to render a template. Expects template name and context as dictionary. Returns a string. If jinja2 is not found it will only handle simple contexts otherwise it will handle jinja2 templates."
    if __jinja2__:
        try:
            template = env.get_template(template)
            return template.render(context if context is not None else "")
        except TemplateNotFound:
            template = env.from_string(template)
            return template.render(context if context is not None else "")
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

    if '{% extends' in template:
        parent_template_name = template.split('{% extends')[1].split('%}')[0].strip().strip('"').strip("'")
        print(f"{RED_TEXT}Error:  Template inheritance, loops and conditionals are not supported YET. You may use them currently if you have Jinja2 installed.{RESET}")

        try:
            with open(join(templates_path, parent_template_name), 'r') as f:
                parent_template = f.read()
        except:
            try:
                with open(parent_template_name, 'r') as f:
                    parent_template = f.read()
            except:
                parent_template = ""
    
    return template

def generate_routes_table() -> str:
    "Generates a table of routes and their corresponding functions."
    sorted_routes = sorted(routes.items(), key=lambda x: x[0])
    table_rows = ''.join(
        f'<tr><td>{route}</td><td>{func.__name__}</td></tr>' for route, func in sorted_routes
    )
    return table_rows

def get_json(data:dict) -> dict:
  "Function to get JSON data. Expects a dictionary. Returns a python dictionary."
  return json.loads(data)


def send_json(data:dict) -> dict:
     "Function to send JSON data. Expects a dictionary. Returns a dictionary to the user."
     return json.dumps(data), 'application/json'


def save_file(data:bytes, name:str, path:str = None) -> None:
    "Function to save a file. Expects data in bytes, name in string format and path in string format. Returns None."
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
         

def send_file(path:str, as_attachment:str = False) -> tuple:
  "Function to send a file. Expects path in string format and as_attachment in boolean format. Returns a tuple."
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


def redirect(link:str) -> tuple:
  "Function to redirect to a link. Expects a link in string format. Returns a tuple."
  return link, 'redirect'

def set_404(info:str = "<h1>404 NOT FOUND</h1>") -> None:
   "Function to set a custom 404 page. Expects a string. Returns None."
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

def set_405(info:str = "<h1>405 NOT ALLOWED</h1>") -> None:
   "Function to set a custom 405 page. Expects a string. Returns None."
   global page_405
   try:
      with open(join(templates_path, info), 'r') as f:
         page_405 = f.read()
   except:
    try:
       with open(info, 'r') as f:
         page_405 = f.read()
    except:
      page_405 = str(info)

def set_500(info:str = "<h1>500 Internal Server Error</h1>") -> None:
   "Function to set a custom 500 page. Expects a string. Returns None."
   global page_500
   try:
      with open(join(templates_path, info), 'r') as f:
         page_500 = f.read()
   except:
    try:
       with open(info, 'r') as f:
         page_500 = f.read()
    except:
      page_500 = str(info)

def set_static_url(url:str) -> None:
   "Function to set the static url. Expects a string. Returns a None."
   global static_url
   static_url = url

def set_static_folder(path:str) -> None:
    "Function to set the static folder. Expects a string. Returns a None."
    global static_path
    static_path = path

def set_templates_folder(path:str) -> None:
    "Function to set the templates folder. Expects a string. Returns a None. Useful if jinja2 is installed to tell it where to find the template otherwise it isn't needed."
    global templates_path
    templates_path = path

def set_routes(paths:dict) -> None:
    "Function to set the routes manually. Expects a dictionary. Returns a None. Useful if you want to do it more akin to django's seperation of concerns."
    global routes
    routes = paths

def set_static_permissive(value:bool = None) -> None:
    "Function to set the static permissive. Expects a boolean. Returns a None."
    global static_permissive
    if isinstance(value, bool):
      static_permissive = value
    else:
       raise ValueError(f"Expected Boolean value got {type(value)}")

def enable_static(value:bool = None) -> None:
    "Function to enable static. Expects a boolean. Returns a None."
    global static
    if isinstance(value, bool):
      static = value
    else:
       raise ValueError(f"Expected Boolean value got {type(value)}")
    
def load_from_json(json_data:dict):
    "Function to load routes from JSON data. Expects a dictionary. Returns multiple routes."
    print("Starting to load routes from JSON data...")

    for method, paths in json_data.items():
        for path, config in paths.items():
            handler_return = config['return']
            handler_type = handler_return['type']

            def make_route_handler(handler_type, handler_return):
                def route_handler(*args, **kwargs):
                    print(f"Handling route: {path} with method: {method} using handler type: {handler_type}")
                    if handler_type == 'template':
                        return render(handler_return['name'], handler_return.get('context', {}))
                    elif handler_type == 'json':
                        return send_json(handler_return['data'])
                    elif handler_type == 'redirect':
                        return redirect(handler_return['url'])
                    elif handler_type == 'plain':
                        return handler_return['data'], 'text/plain'
                    elif handler_type == 'data':
                        return handler_return['data']
                    elif handler_type == 'file':
                        return send_file(handler_return['path'], as_attachment=handler_return.get('attachment', False))
                    else:
                        print(f"Unknown handler type: {handler_type}")
                return route_handler

            new_handler = make_route_handler(handler_type, handler_return)
            route(path)(new_handler)
            print(f"Registered new route: {path} with dynamic handler for {handler_type}")

    print("Finished loading routes from JSON. Current routes dictionary:")
    for route_path, func in routes.items():
        print(f"Path: {route_path}, Handler Function: {func.__name__ if hasattr(func, '__name__') else 'Anonymous Function'}")


def monitor_changes(directory: str, interval: int=1) -> None:
    """Monitor the directory for changes and restart the server if a change is detected. Returns None."""
    mtimes = {}
    while True:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    try:
                        mtime = os.path.getmtime(filepath)
                        if filepath not in mtimes:
                            mtimes[filepath] = mtime
                        elif mtime != mtimes[filepath]:
                            print(f"{YELLOW_TEXT}Detected change in {filepath}. Reloading...{RESET}")
                            os.execv(sys.executable, ['python'] + sys.argv)
                    except FileNotFoundError:
                        pass
        time.sleep(interval)



# Default page

html : str = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="icon" type="image/x-icon" href="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mango</title>
    <style>
        :root {{
            --background-color-light: white;
            --text-color-light: orange;
            --background-color-dark: #121212;
            --text-color-dark: orange;
        }}

        body {{
            background-color: var(--background-color-light);
            color: var(--text-color-light);
            text-align: center;
            font-family: Arial, sans-serif;
            margin-top: 150px;
        }}

        h1 {{
            font-size: 24px;
        }}

        footer {{
            background-color: #f5f5f5;
            padding: 10px;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 12px;
            color: #888;
        }}

        .mango-img {{
            width: 150px;
            margin: 0 auto;
        }}

        .link {{
            color: orange;
            text-decoration: underline;
            margin-top: 10px;
        }}

        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: var(--background-color-dark);
                color: var(--text-color-dark);
            }}
            footer {{
                background-color: rgb(52, 52, 52);
                color: white;
            }}
        }}
    </style>
</head>
<body>
    <h1>Server successfully started, but there are no routes or the "/" route is empty</h1>
    <img class="mango-img" src="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0" alt="Mango">
    <footer>
        Version: {__version__}
        <br>
        <a class="link" href="{__app_url__}">Check out the development!</a>
    </footer>
</body>
</html>
"""


# New 500 Dev HTML default 

html_500 : str = """
<!DOCTYPE html>
<html>
<head>
    <link rel="icon" type="image/x-icon" href="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mango - Error</title>
    <style>
        :root {{
            --background-color-light: #FFFDE7;
            --text-color-light: #FF6F00;
            --background-color-dark: #121212;
            --text-color-dark: #FFA726;
        }}

        body {{
            background-color: var(--background-color-light);
            color: var(--text-color-light);
            text-align: center;
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding-top: 150px;
        }}

        h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .mango-img {{
            width: 150px;
            margin: -30px;
        }}

        .error-container {{
            background-color: #FFFFFF;
            margin: 0 auto;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px 0 rgba(0,0,0,0.2);
            display: inline-block;
            max-width: 80%;
        }}

        .error-message {{
            background-color: #FFCCBC;
            color: #E65100;
            padding: 15px;
            border-left: 5px solid #E64A19;
            text-align: left;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
            word-wrap: break-word;
        }}

        footer {{
            background-color: #FBE9E7;
            padding: 10px;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 12px;
            color: #555;
        }}

        .link {{
            color: var(--text-color-dark);
            text-decoration: underline;
        }}

        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: var(--background-color-dark);
                color: var(--text-color-dark);
            }}
            .error-container {{
                background-color: #424242;
            }}
            .error-message {{
                background-color: #6A1B9A;
                color: #F3E5F5;
                border-left-color: #AD1457;
            }}
            footer {{
                background-color: #263238;
                color: #CFD8DC;
            }}
        }}
    </style>
</head>
<body>
 <img class="mango-img" src="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0" alt="Mango">
    <h1>Server Error</h1>
    <div class="error-container">
        <p>The server encountered an unexpected condition that prevented it from fulfilling the request.</p>
        <div class="error-message">
            Error details: {debug_info}
        </div>
        <p>You are seeing this error because you have "debug_mode" set to true. Set it to false or don't include it in your run function to see the standard error 500 page.
    </div>
    
    <footer>
        Version: {__version__}
        <br>
        <a class="link" href="{__app_url__}">Need help? Read the documentation</a>
    </footer>
</body>
</html>
"""

# New 404 Dev HTML default 

html_404 : str = """
<!DOCTYPE html>
<html>
<head>
    <link rel="icon" type="image/x-icon" href="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mango - Not Found</title>
    <style>
        :root {{
            --background-color-light: white;
            --text-color-light: orange;
            --background-color-dark: #121212;
            --text-color-dark: orange;
        }}
        body {{
            background-color: var(--background-color-light);
            color: var(--text-color-light);
            text-align: center;
            font-family: Arial, sans-serif;
            padding-top: 50px;
        }}
        h1 {{
            font-size: 24px;
        }}
        table {{
            margin: 20px auto;
            border-collapse: collapse;
            border: 1px solid #ddd;
            width: 80%;
            max-width: 600px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }}
        th {{
            background-color: orange;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        img.mango-logo {{
            width: 100px;
            margin-bottom: 20px;
        }}
        footer {{
            background-color: #f5f5f5;
            padding: 10px;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 12px;
            color: #888;
        }}
        .link {{
            color: orange;
            text-decoration: none;
            font-weight: bold;
        }}
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: var(--background-color-dark);
                color: var(--text-color-dark);
            }}
            footer {{
                background-color: rgb(52, 52, 52);
                color: white;
            }}
            th {{
                background-color: #555;
            }}
            tr:nth-child(even) {{
                background-color: #333;
            }}
        }}
    </style>
</head>
<body>
    <img class="mango-logo" src="https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0" alt="Mango Logo">
    <h1>404 Not Found</h1>
    <p>The requested URL was not found on this server. Here are the available routes:</p>
    <table>
        <tr>
            <th>Route</th>
            <th>Function Name</th>
        </tr>
        {route_table}
    </table>
    <p style='text-align:center'>you are seeing this error because you have "debug_mode" set to true. Set it to false or don't include it in your run function to see the standard error 404 page.</p>
    <footer>
        Version: {__version__}
        <br>
        <a href="{__app_url__}" class="link">Check out the development!</a>
    </footer>
</body>
</html>
"""
