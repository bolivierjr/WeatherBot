from importlib import reload
from . import errors, helpers

# To reload the modules when you reload the bot.
reload(errors)
reload(helpers)
