from importlib import reload
from . import errors, weather, services

# To reload the modules when you reload the bot.
reload(errors)
reload(weather)
reload(services)
