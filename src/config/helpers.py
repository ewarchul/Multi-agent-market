import importlib


def get_object(module, name):
    """
    Gets object from given module by name
    :param module: full module name
    :param name: object name
    :return: loaded object
    """
    m = importlib.import_module(module)
    f = getattr(m, name)
    return f


def serialize_func(fun, args):
    """
    Serializes callable object with arguments

    :param fun: callable object
    :param args: arguments
    :return: dictionary with 'module', 'fun' and 'args'
    """
    return {
        'module': fun.__module__,
        'fun': fun.__name__,
        'args': args
    }


def deserialize_func(obj, default_fun, default_args):
    """
    Deserializes callable object with arguments

    object is identified by 'module' and 'fun' fields
    'args' field is optional

    :param obj: dictionary or None
    :param default_fun: default callable object value
    :param default_args: default arguments
    :return: (callable, arguments) pair
    """
    if obj:
        return get_object(
            obj.get('module'),
            obj.get('fun')
        ), obj.get('args', default_args)
    else:
        return default_fun, default_args
