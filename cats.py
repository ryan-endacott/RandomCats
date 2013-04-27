import os
from flask import Flask, render_template
from dropbox import client, session
from collections import defaultdict
from random import choice
app = Flask(__name__)


def try_to_load_settings():
  try:
    import settings
  except ImportError:
    return defaultdict(None)
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
def random_cat():
  src = get_random_cat_url()
  return render_template('application.html', cat_source=src)

def get_random_cat_url():
  contents = client.metadata('/')['contents'] # Get all the files in cat folder
  path = choice(contents)['path'] # Select a random one and get its path
  return client.media(path)['url'] # Return the dropbox media url


if __name__ == '__main__':
  app.run(use_debugger=True, debug=True,
            use_reloader=True, host='0.0.0.0')