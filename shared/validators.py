# Validation happens here!
from datetime import datetime


# Validate empty fields
def validate_not_empty(value: str, field_name="Field"):

    if value is None or value == "" or value.isspace():
        return (False, f"{field_name} cannot be empty")

    return (True, "")


# Validate positive number
def validate_positive_number(value: int, field_name="Amount"):

    try:
        if int(value) > 0:
            return (True, "")
        else:
            return (False, f"{field_name} must be positive")
    except ValueError:
        return (False, f"{field_name} must be number")


# validate dates
def validate_date_format(date_string, format="DD-MM-YYYYTHH:MM:SS"):

    try:
        date_obj = datetime.strptime(date_string, format)
        return (True, "")
    except:
        return (False, "Invalid date format")


# validate urls
def validate_url(url: str):

    if len(url) > 2000:
        return (False, "Invalid URL format, max length exceeded")

    if not (url.startswith("https://") or url.startswith("http://")):
        return (False, "Invalid URL format")

    if "." not in url:
        return (False, "Invalid URL format")

    return (True, "")


# validate choices
def validate_choice(value, valid_choices, field_name="Value"):

    if value not in valid_choices:
        return (False, f"Must be one of {valid_choices}")

    return (True, "")


# validate tags
def validate_tag(tag: str):

    if tag.isspace():
        return (False, "Invalid tag")

    if len(tag.split(" ")) >= 1:
        corrected_tag = tag.lower().replace(" ", "_")
        return (True, corrected_tag)

    return (False, "Invalid tag")


# validate emails
def validate_email(email: str):

    if "@gmail.com" not in email or len(email) < 10:
        return (False, "Invalid email")

    return (True, "")


if __name__ == "__main__":
    # amount = 100
    # is_valid, error_msg = validate_positive_number(amount)
    # if not is_valid:
    #     print(f"Error: {error_msg}")

    # is_valid, corrected_tag = validate_tag("")
    # if is_valid:
    #     use_tag = corrected_tag
    #     print(use_tag)

    print(validate_not_empty("hello"))
    print(validate_not_empty(""))
    print(validate_not_empty("  "))
    print(validate_not_empty(None))

    print(validate_positive_number(5))
    print(validate_positive_number("5"))
    print(validate_positive_number(0))
    print(validate_positive_number(-10))
    print(validate_positive_number("abc"))

    print(validate_url("https://google.com"))
    print(validate_url("http://site.co"))
    print(validate_url("google.com"))
    print(validate_url("https://"))

    print(validate_tag("python"))
    print(validate_tag("Python Code"))
    print(validate_tag("REACT-HOOKS"))
