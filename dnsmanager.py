from bottle import route,run, get, post, request, response, static_file, Bottle,\
  redirect
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader
import ldap

searchpath = ['templates']
engine = Engine(
  loader = FileLoader(searchpath),
  extensions = [CoreExtension()]
)

app = application = Bottle()

app.config.load_config("config.ini")

@app.route('/')
def index():
  signing_key = app.config['security.key']
  auth = request.get_cookie("auth", secret=signing_key)
  
  template = engine.get_template('index.html')
  return template.render({'auth':auth})

@app.get('/logout')
def do_logout():
  response.delete_cookie("auth")
  redirect("/")

@app.get('/login')
def login_form():
  template = engine.get_template('login.html')
  return template.render({'ldap_error':None})

@app.post('/login')
def do_login():
  proxy_user = app.config['ldap.proxy_user']
  proxy_pass = app.config['ldap.proxy_pass']
  ldap_server = app.config['ldap.ldap_server']
  ldap_search_base = app.config['ldap.ldap_search_base']
  signing_key = app.config['security.key']

  username = request.forms.get('username')
  password = request.forms.get('password')
  filter = app.config['ldap.username_attribute'] + "=" + username

  try:
    l = ldap.initialize(ldap_server)
    l.simple_bind_s(proxy_user, proxy_pass)
    result = l.search_s(ldap_search_base, ldap.SCOPE_SUBTREE, filter, None)
    if result == []:
      template = engine.get_template('login.html')
      return template.render({'ldap_error':'User ' + username + ' not found!'})
    bind_dn = result[0][0]
    l.unbind_s()

    l = ldap.initialize(ldap_server)
    l.simple_bind_s(bind_dn, password)

  except ldap.LDAPError as e:
    template = engine.get_template('login.html')
    return template.render({'ldap_error':e})
  
  response.set_cookie("auth", username, secret=signing_key, httponly=True)
  redirect("/")

@app.get('/static/<filename:path>')
def serve_static(filename):
  return static_file(filename, root='static')

if __name__ == '__main__':
  run(app, host='0.0.0.0', port=8080)
