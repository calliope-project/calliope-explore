#
# Source: https://github.com/plotly/dash/issues/188#issuecomment-602233549
# Source: https://gist.github.com/eddy-geek/73c8f73c089b0f998a49541b15a694b1
#

import ast
import re
from urllib.parse import urlparse, parse_qsl


def apply_default_value(params):
    """
    :param params: the state decoded from url
    """

    def wrapper(func):
        def apply_value(*args, **kwargs):
            if "id" in kwargs and kwargs["id"] in params:
                param_key_dict = params[kwargs["id"]]
                kwargs.update(param_key_dict)
            return func(*args, **kwargs)

        return apply_value

    return wrapper


ID_PARAM_SEP = "::"


def parse_state(url):
    parse_result = urlparse(url)
    query_string = parse_qsl(parse_result.query)

    state = {}
    for key, value in query_string:
        if ID_PARAM_SEP in key:
            id, param = key.split(ID_PARAM_SEP)
        else:
            id, param = key, "value"
        state.setdefault(id, {})[param] = ast.literal_eval(value)

    return state


def param_string(id, p):
    return id if p == "value" else id + ID_PARAM_SEP + p


RE_SINGLE_QUOTED = re.compile("^'|'$")


def myrepr(o):
    """Optional but chrome URL bar hates "'" """
    return RE_SINGLE_QUOTED.sub('"', repr(o))
