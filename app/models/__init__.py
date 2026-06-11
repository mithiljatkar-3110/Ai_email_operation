import importlib
import pkgutil

from app.models.action import Action
from app.models.contact import Contact
from app.models.email import Email
from app.models.enums import ContactStatus, EmailStatus, ThreadStatus
from app.models.thread import Thread

__all__ = [
    "Action",
    "Contact",
    "ContactStatus",
    "Email",
    "EmailStatus",
    "Thread",
    "ThreadStatus",
    "load_models",
]


def load_models() -> None:
    """Import every model module so tables register with Base.metadata."""
    package = __name__
    for module in pkgutil.iter_modules(__path__, prefix=f"{package}."):
        if module.name.endswith(".enums"):
            continue
        importlib.import_module(module.name)


load_models()
