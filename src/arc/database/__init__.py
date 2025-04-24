from .core import Base, _ENGINE  # noqa: F401
from . import models

# Create tables once at import time
Base.metadata.create_all(_ENGINE)
