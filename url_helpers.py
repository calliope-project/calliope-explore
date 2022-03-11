# Copyright (C) 2022 by Edward O.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without l> imitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

#
# Source: https://github.com/plotly/dash/issues/188#issuecomment-602233549
# Source: https://gist.github.com/eddy-geek/73c8f73c089b0f998a49541b15a694b1
#

import ast
import re
from urllib.parse import urlparse, parse_qsl, quote, urlencode


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


def update_url_state(component_ids, values):
    """Updates URL from component values."""

    keys = [param_string(id, p) for id, param in component_ids.items() for p in param]
    state = dict(zip(keys, map(myrepr, values)))
    params = urlencode(state, safe="%/:?~#+!$,;'@()*[]\"", quote_via=quote)
    return f"?{params}"
