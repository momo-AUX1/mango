# Mango Framework

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

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
- Integrated basic ORM for DB functions
- Integrated basic Template engine Shake

## Installation

Mango can be easily installed via pip:

```shell
pip install mango-framework
```

## Usage
1. Import the necessary modules and functions from Mango:

```python
from mango import route, run, render, send_json, send_file, Shake, get_json
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
```

6. Render the HTML to the user:

```python
@route('/render')
def render():
    return render('index.html')
```

7. Render the HTML to the user as a template with Shake:

```python
@route('/render')
def shake():
    return Shake().render('index.html',{'name':'john'})
```

8. Get form data:

```python
@route('/form')
def form(form_data):
    name = get_data(form_data,'name')
    return f"Hello, {name}!"
```

3. Run the Mango server:

```python
run()
```



