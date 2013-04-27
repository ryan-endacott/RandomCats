import os
from flask import Flask, render_template
from dropbox import client, session
from collections import defaultdict
from random import shuffle
from datetime import datetime, timedelta
from dateutil import parser
import pytz

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
  return render_template('application.html', cat_urls=get_cat_urls())

@app.route('/random_cat')
def random_cat():
  return render_template('singlecat.html', cat_source=get_cat_urls()[0])

def request_cat_media_links():
  files = client.metadata('/')['contents'] # Get all the files in cat folder
  paths = [file['path'] for file in files] # Get the paths of all files
  return [client.media(path) for path in paths] # Get media for each path

def get_cat_urls():
  # If media links are expired, get new ones
  if get_cat_urls.expiration < datetime.now(pytz.utc):
    print 'Media links are expired, getting new ones'
    links = request_cat_media_links()
    get_cat_urls.expiration = parser.parse(links[0]['expires']) # Get the expiration of the first one requested
    get_cat_urls.urls = [media['url'] for media in links] # Get the URLs

  shuffle(get_cat_urls.urls)
  return get_cat_urls.urls

# Set to already expired (yesterday) to begin with
get_cat_urls.expiration = datetime.now(pytz.utc)-timedelta(days=1)

if __name__ == '__main__':
  app.run()