from bottle import route,run, get, post, request, response, static_file
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader

searchpath = ['templates']
engine = Engine(
  loader = FileLoader(searchpath),
  extensions = [CoreExtension()]
)

@route('/')
def index():
  template = engine.get_template('master.html')
  return template.render({})

@get('/static/<filename:path>')
def serve_static(filename):
  return static_file(filename, root='static')

if __name__ == '__main__':
  run(host='0.0.0.0', port=8080)
