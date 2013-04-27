import os
from flask import Flask, render_template
from dropbox import client, session
from collections import defaultdict
from random import shuffle, choice
app = Flask(__name__, static_path = '/assets')

# A bad hack to make dot syntax work for dictionaries
# This way accessing setting module variables can be the same
# as accessing dictionary elements when loading the environment vars
class AttrDict(defaultdict):
  __getattr__= defaultdict.__getitem__
  __setattr__= defaultdict.__setitem__
  __delattr__= defaultdict.__delitem__

def try_to_load_settings():
  try:
    import settings
  except ImportError:
    return AttrDict(lambda: False)
  else:
    return settings

# Load Environment
settings = try_to_load_settings()

APP_KEY = settings.APP_KEY or os.environ['APP_KEY']
APP_SECRET = settings.APP_SECRET or os.environ['APP_SECRET']
ACCESS_TYPE = settings.ACCESS_TYPE or os.environ['ACCESS_TYPE']
TOKEN_KEY = settings.TOKEN_KEY or os.environ['TOKEN_KEY']
TOKEN_SECRET = settings.TOKEN_SECRET or os.environ['TOKEN_SECRET']

sess = session.DropboxSession(APP_KEY,APP_SECRET, ACCESS_TYPE )
sess.set_token(TOKEN_KEY, TOKEN_SECRET)
client = client.DropboxClient(sess)


@app.route('/')
def all_cats():
  return render_template('application.html', cat_urls=get_all_cat_urls())

@app.route('/random_cat')
def random_cat():
  return render_template('singlecat.html', cat_source=get_random_cat_url())

def get_cat_paths():
  files = client.metadata('/')['contents'] # Get all the files in cat folder
  paths = [file['path'] for file in files] # Get the paths of all files
  shuffle(paths) 
  return paths

def get_all_cat_urls():
  return [client.media(path)['url'] for path in get_cat_paths()] # Get media url for each path


def get_random_cat_url():
  path = get_cat_paths()[0] # First one will be random because it was shuffled
  return client.media(path)['url'] # Return the dropbox media url


if __name__ == '__main__':
  app.run()