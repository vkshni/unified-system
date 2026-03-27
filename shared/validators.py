from datetime import datetime
import re


# Validate empty fields
def validate_not_empty(value: str, field_name="Field"):
    if value is None or value == "" or value.isspace():
        return (False, f"{field_name} cannot be empty")
    return (True, "")


# Validate positive number
def validate_positive_number(value, field_name="Amount"):
    try:
        if float(value) > 0:  # ✅ Use float to accept decimals
            return (True, "")
        else:
            return (False, f"{field_name} must be positive")
    except (ValueError, TypeError):
        return (False, f"{field_name} must be a number")


# Validate dates
DATE_FORMATS = {
    "iso": "%Y-%m-%dT%H:%M:%S",
    "slash": "%d/%m/%Y",
    "dash": "%d-%m-%Y",
    "datetime": "%d-%m-%YT%H:%M:%S",
}


def validate_date_format(date_string, format="datetime"):
    if format in DATE_FORMATS:
        format_str = DATE_FORMATS[format]
    else:
        format_str = format

    try:
        datetime.strptime(date_string, format_str)
        return (True, "")
    except ValueError:
        return (False, "Invalid date format")


# Validate URLs
def validate_url(url: str):
    if not url or len(url) > 2000:
        return (False, "Invalid URL length")

    if not (url.startswith("https://") or url.startswith("http://")):
        return (False, "URL must start with http:// or https://")

    domain = url.replace("https://", "").replace("http://", "")
    if "." not in domain and "localhost" not in domain:
        return (False, "Invalid URL domain")

    return (True, "")


# Validate choices
def validate_choice(value, valid_choices, field_name="Value"):
    if value not in valid_choices:
        return (
            False,
            f"{field_name} must be one of: {', '.join(map(str, valid_choices))}",
        )
    return (True, "")


# Validate tags
def validate_tag(tag: str):
    if not tag or tag.isspace():
        return (False, "Invalid tag")

    corrected_tag = tag.lower().replace(" ", "_").replace("-", "_")
    return (True, corrected_tag)


# Validate emails
def validate_email(email: str):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email):
        return (True, "")
    return (False, "Invalid email format")
