# Mango Framework

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Introduction

Mango is a lightweight Python framework for building web applications. It provides a simple and intuitive way to handle routing, render HTML templates, and serve files. With Mango, you can quickly set up a web server and define routes to handle different HTTP requests.

## Features

- Easy routing configuration
- Rendering HTML templates
- Serving static files
- Handling JSON data
- Lightweight and minimal dependencies
- Suitable for small to medium-sized web applications
- Human readible code even beginners could modify 
- Integrated basic ORM for DB functions

## Installation

Mango can be easily installed via pip:

```shell
pip install mango-framework
```

## Usage
1. Import the necessary modules and functions from Mango:

```python
from mango import route, run, render, send_json, send_file
```
2. Define your routes using the @route() decorator: 

```python
@route('/')
def index():
    return "Hello, Mango!"

@route('/greet')
def greet():
    return "Welcome to Mango!"
```

3. Run the Mango server:

```python
if __name__ == '__main__':
    run()
```
