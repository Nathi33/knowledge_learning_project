from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Retrieve a value from a dictionary using the given key.

    This filter allows access to dictionary items in Django templates.

    Args:
        dictionary (dict): The dictionary to retrieve the value from.
        key: The key to look up in the dictionary.

    Returns:
        The value corresponding to the key if it exists, otherwise None.
    """
    return dictionary.get(key)