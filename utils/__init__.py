from importlib import reload

from . import errors, services, users, weather

# To reload the modules when you reload the bot.
reload(errors)
reload(weather)
reload(services)
reload(users)
