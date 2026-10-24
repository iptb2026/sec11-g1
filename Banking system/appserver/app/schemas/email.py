import re
from typing import Annotated, Optional

from pydantic import BeforeValidator

# Same rule as the frontend (appclient/src/utils/validation.js): something@something.something.
# Pydantic's EmailStr was stricter: it refused special-use domains such as
# admin@bank.local (the seeded admin), so that admin could not save their own
# profile, and it refused "" from a form whose email field was left empty.
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _check_email(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("value is not a valid email address")
    value = value.strip()
    if value == "":
        return None  # empty field = no email (also keeps the UNIQUE index happy)
    if not EMAIL_PATTERN.match(value):
        raise ValueError("value is not a valid email address")
    return value


OptionalEmail = Annotated[Optional[str], BeforeValidator(_check_email)]
