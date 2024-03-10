# Mango Framework

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Mango Icon](https://th.bing.com/th/id/R.54bad49b520690f3858b1f396194779d?rik=QSeITH3EbHg4Vw&pid=ImgRaw&r=0)

## Introduction

Mango is a lightweight Python framework for building web applications. It provides a simple and intuitive way to handle routing, render HTML templates, and serve files. With Mango, you can quickly set up a web server and define routes to handle different HTTP requests. It is made to be accessible and highly modifiable even by beginners to learn and eventually move on to more mature frameworks such as Flask or Bottle. You only need python3 to run Mango and nothing else.

## Features

- Easy routing configuration
- Rendering HTML templates
- Serving static files
- Handling JSON data
- Handling of basic form data
- Lightweight and minimal dependencies
- Suitable for small to medium-sized web applications
- Human readible code even beginners could modify 
- Handling of file uploads
- Handling static files
- Dynamic route configuration via JSON

## Installation

Mango can be easily installed via pip:

```shell
pip install mango-framework
```

## Usage
1. Import the necessary modules and functions from Mango:

```python
from mango import route, run, render, send_json, send_file, get_json, save_file, set_404, set_405, set_static_url, enable_static, set_static_folder, set_static_permissive, load_from_json, set_routes, set_500
```
2. Define your routes using the @route() decorator: 

```python
@route('/')
def index():
    return "Hello, Mango!"
```

3. Get JSON data:

```python
@route('/post')
def post(post):
    user = get_json(post)
    return f"Hello, {user['name']}!"
```

4. Send JSON data:

```python
@route('/send')
def send():
    return send_json({'name':'john'})
```

5. Send a file for the user to download:

```python
@route('/download')
def download():
    return send_file('image.jpeg')

### as attachment

@route('/download')
def download():
    return send_file('image.jpeg', as_attachment=True)
```

6. Render the HTML to the user:

```python
@route('/render')
def render():
    return render('index.html')

### New reactive rendering

@route('/render')
def render():
    return render('index.html',{'name':'john'})
```

7. Get form data:

```python
@route('/form')
def form(form_data):
    name = form_data.get('name')
    return f"Hello, {name}!"
```
8. Get file upload with data:

```python
@route('/get')
def upload(form_fields, files):
    input1 = form_fields.get("input1")  
    input2 = form_fields.get("input2")

    file_item1 = files[0]  
    if file_item1.filename:  
        file_path1 = save_file(data=file_item1.file.read(), name=file_item1.filename, path='upload')

    file_item2 = files[1]
    if file_item2.filename:
        file_path2 = save_file(data=file_item2.file.read(), name=file_item2.filename, path='upload')

        #returns files in a list, forms in a dict

    return "files saved successfully"
```

9. Change the default 404 Page:

```python
set_404("<h1> not here ! </h1>")

## or pass an HTML or any file directly

set_404("404.html")
```

The page that will be shown if `debug_mode` is set to `False` and a path is not found, otherwise it will show the included 404 page.

10. Change the default 405 Page:

```python
set_405("<h1> Method not allowed ! </h1>")

## or pass an HTML or any file directly

set_405("405.html")
```

11. Change the default 500 Page:

```python
set_500("<h1> Internal Server Error ! </h1>")

## or pass an HTML or any file directly

set_500("500.html")
```

The page that will be shown if `debug_mode` is set to `False` and an error occurred, otherwise it will show the included 500 page.

12. Send static files to HTML:

```html
<link rel="stylesheet" type="text/css" href="/static/style.css">
```

13. Change the default Static URL

```python
set_static_url("/images")
```
Default URL is /static. the new link MUST start with / !

14. Enable or disable Static serving

```python
enable_static(True) # or False to disable
```

15. Set the static folder

```python
set_static_folder("static")
```

16. Set the static folder to be permissive

```python
set_static_permissive(True) # or False to disable
```

Defaults to `False`, it is used if you want the static handler to be permissive, meaning it will serve any file in the project root without checking if the file is in the static directory or not. Ideal if you want mango to act as a file server or CDN.

17. Set the routes manually

```python

def index():
    return "Hello, Mango!"

def post(data):
    user = get_json(data)
    return f"Hello, {user['name']}!"

paths = {
    '/' : index,
    '/post' : post
}

set_routes(paths)
```

Seperate the routes to introduce a seperation of concerns similar to django and make mango more scalable.

18. Run the Mango server:

```python
run(host='localhost', port=8080, debug_mode=True)
```


## What's New in 1.2

### Dynamic Route Configuration via JSON

Mango 1.2 introduces the ability to configure routes dynamically using a JSON file. This feature significantly simplifies route management by allowing developers to define routes, handlers, and their responses in a JSON format, making your web application easily configurable and adaptable without the need to directly modify the Python code, the included ORM has been removed in favor of third party more robust alternatives such as tinyDB.

#### How to Use JSON Route Configuration

1. **Define Routes in JSON**: Create a `routing.json` file within your project directory. This file will contain all your route definitions in a structured format.
   
2. **Load Routes**: Utilize the `load_from_json` function at the start of your application to load the routes defined in the `routing.json` file.

3. **Run Your Server**: With the routes dynamically loaded, start your Mango server as usual.

#### JSON Configuration Example

Below is an example of how to structure your `routing.json` to define various routes:

```json
{
    "GET": {
        "/": {
            "handler": "index",
            "return": {
                "type": "template",
                "name": "index.html",
                "context": {
                    "name": "test",
                    "time": "11AM"
                }
            }
        },
        "/json": {
            "handler": "send_json",
            "return": {
                "type": "json",
                "data": {
                    "name": "test",
                    "time": "11AM"
                }
            }
        },
        "/redirect": {
            "handler": "redirect_func",
            "return": {
                "type": "redirect",
                "url": "/json"
            }
        },
        "/plain": {
            "handler": "send_plain",
            "return": {
                "type": "plain",
                "data": "Hello World"
            }
        },
        "/file": {
            "handler": "send_file_func",
            "return": {
                "type": "file",
                "path": "a.jpg",
                "attachment": false
            }
        },
        "/data": {
            "handler": "send_data",
            "return": {
                "type": "data",
                "data": "Hello World"
            }
        }
    }
}
```

##### Loading and Running with JSON Routes 

To dynamically load the routes from your `routing.json` and start the server, include the following code in your application:

```python
data = open("routing.json").read()
json_data_routing = json.loads(data)
load_from_json(json_data_routing)
run()
``` 

This enhancement to Mango makes setting up and modifying your server simpler than ever before, promoting rapid development and easier management of web applications through external JSON configurations.

## Recommended Resources

### TinyDB 

[![TinyDB](https://img.shields.io/badge/TinyDB-lightweight-brightgreen)](https://tinydb.readthedocs.io/en/latest/)

TinyDB is a lightweight, document-oriented database that is perfect for small projects or to be used as a temporary storage. It is written in pure Python and has no external dependencies. The database is stored in a single file, making it easy to manage and share. TinyDB is simple to use and easy to learn, making it an ideal choice for beginners and small projects and its goals closely align with Mango.



### PicoCSS

[![PicoCSS](https://img.shields.io/badge/pico-css-brightgreen)](https://picocss.com/)

PicoCSS is a minimal CSS framework that provides a simple and lightweight way to style your web applications. It is designed to be easy to use and highly customizable, making it a great choice for small to medium-sized projects. PicoCSS is built with simplicity in mind, allowing you to quickly add styles to your web pages without the need for complex or bloated CSS frameworks. It is a perfect match for Mango, as both are designed to be lightweight and easy to use, making them a great combination for building web applications.
