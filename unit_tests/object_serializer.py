from json import dumps

from cfclogger import log, LOG_BASE, LOG_DEBG

from compiler.parser.ast import AST_Node

EQUAL = "EQUAL"
NOT_EQUAL = "NOT_EQUAL"
EXPECTED_NOT_FOUND = "EXP_NOT_FOUND"
FOUND_NOT_EXPECTED = "FOUND_NOT_EXP"
WRONG_TYPE = "WRONGE_TYPE"

EQUAL_COLOR = "\033[32m"
NOT_EQUAL_COLOR = "\033[31m"
EXPECTED_NOT_FOUND_COLOR = "\033[33m"
FOUND_NOT_EXPECTED_COLOR = "\033[95m"
WRONG_TYPE_COLOR = "\033[36m"

RELATION_COLORS = {
    EQUAL: EQUAL_COLOR,
    NOT_EQUAL: NOT_EQUAL_COLOR,
    EXPECTED_NOT_FOUND: EXPECTED_NOT_FOUND_COLOR,
    FOUND_NOT_EXPECTED: FOUND_NOT_EXPECTED_COLOR,
    WRONG_TYPE: WRONG_TYPE_COLOR
}

EXPAND_EQUALS = False


def serialize_item(item, already_serialized_objects):
    log(LOG_BASE, f"Serializing item {item}...")
    if isinstance(item, AST_Node):
        log(LOG_BASE, f"AST Node name {item.name}")
    if isinstance(item, int) or isinstance(item, str) or item is None \
            or isinstance(item, bool):
        return str(item)
    elif isinstance(item, list) or isinstance(item, tuple) \
            or isinstance(item, set):
        return_list = []
        for element in item:
            return_list.append(serialize_item(
                element,
                already_serialized_objects
            ))
        return return_list
    elif isinstance(item, dict):
        return_dict = {}
        for key in item:
            return_dict[key] = serialize_item(
                item[key],
                already_serialized_objects
            )
        return return_dict
    else:
        if item in already_serialized_objects:
            log(LOG_BASE, f"Ancestor list: {already_serialized_objects}")
            log(LOG_BASE, f"{item} is an ancestor")
            return "<ancestor>"
        return serialize_object(item, already_serialized_objects)


def serialize_object(obj, already_serialized_objects=[]) -> dict:
    already_serialized_objects.append(obj)
    res_dict = {}
    for key in obj.__dict__:
        if key.startswith("_"):
            continue
        log(LOG_BASE, key)
        item = obj.__getattribute__(key)
        res_dict[key] = serialize_item(item, already_serialized_objects)
    return {"_type": str(type(obj)), "_object": res_dict}


def pretty_serialized_item(obj, do_indent=True):
    if do_indent:
        return dumps(serialize_item(obj, []), indent=4)
    return dumps(serialize_item(obj, []))


def pretty_print(item, key="", prefix="", last=True, root=True):
    t_char = "├── "
    i_char = "│   "
    l_char = "└── "
    empty = "    "
    list_char = l_char if last else t_char
    follow_char = empty if last else i_char
    if root:
        list_char = follow_char = ""

    if isinstance(item, int) or isinstance(item, str) \
            or isinstance(item, bool):
        log(LOG_DEBG, f"{prefix+list_char}{key}: {item}")
    elif isinstance(item, dict):
        log(LOG_DEBG, f"{prefix+list_char}{key}")
        for i, key in enumerate(item):
            pretty_print(item[key], key, prefix+follow_char,
                         i == len(item) - 1, root=False)
    elif isinstance(item, list) or isinstance(item, tuple) \
            or isinstance(item, set):
        log(LOG_DEBG, f"{prefix+list_char}{key}")
        for i, key in enumerate(item):
            pretty_print(key, i, prefix+follow_char,
                         i == len(item) - 1, root=False)


def assert_equal(a, b):
    return a == b


def serial_to_dict(serial) -> dict:
    res_dict = {}
    if isinstance(serial, dict):
        for key in serial:
            res_dict[key] = serial_to_dict(serial[key])
    elif isinstance(serial, list) or isinstance(serial, tuple) \
            or isinstance(serial, set):
        for i, key in enumerate(serial):
            res_dict[str(i)] = serial_to_dict(key)
    else:
        return serial
    return res_dict


def get_comparison_dict(exp, got):
    not_received = KeyError()   # very scuffed implementation ik

    assert isinstance(exp, dict)
    assert isinstance(got, dict)
    res_dict = {}
    for key in exp:
        expected_value = exp[key]
        got_value = got.get(key, not_received)
        if got_value is not not_received:
            if type(expected_value) is not type(got_value):
                res_dict[key] = (
                    WRONG_TYPE,
                    str(type(expected_value)),
                    str(type(got_value))
                )
            else:
                if assert_equal(got_value, expected_value):
                    relation = EQUAL
                else:
                    relation = NOT_EQUAL
                if isinstance(expected_value, dict):
                    item_value = get_comparison_dict(
                        expected_value, got_value
                    )
                    res_dict[key] = (
                        relation,
                        item_value
                    )
                else:
                    res_dict[key] = (
                        relation,
                        expected_value,
                        got_value
                    )
        else:
            res_dict[key] = (
                EXPECTED_NOT_FOUND,
                expected_value
            )
    for key in got.keys() - exp.keys():
        res_dict[key] = (FOUND_NOT_EXPECTED, got[key])
    # return formats
    # (n)eq = (relation, item_value [dict])
    # (n)eq = (relation, expected, [got])
    # enf / fne = (relation, item)
    # w type = (relation, exp, got)
    return res_dict


def serial_comparison_dict(exp, got):
    return get_comparison_dict(
        serial_to_dict(exp),
        serial_to_dict(got)
    )


def pretty_print_item(prefix, key, comparison_tuple, follow_char,
                      list_char):
    relation, item, *got = comparison_tuple
    got = got[0] if got else "<None>"
    if isinstance(item, str):
        item = item.replace("\n", "\\n")
    got = got.replace("\n", "\\n")
    if relation is EQUAL:
        c = EQUAL_COLOR
        prefix = prefix+c+list_char
        if isinstance(item, dict):
            log(LOG_DEBG, f"{c}{prefix}{key}\033[0m")
        else:
            log(LOG_DEBG, f"{c}{prefix}{key}: {item}\033[0m")
    elif relation is NOT_EQUAL:
        c = NOT_EQUAL_COLOR
        prefix = prefix+c+list_char
        if isinstance(item, dict):
            log(LOG_DEBG, f"{c}{prefix}{key}\033[0m")
        else:
            log(LOG_DEBG, f"{c}{prefix}{key}: {got} [{item}]\033[0m")
    elif relation is EXPECTED_NOT_FOUND \
            or relation is FOUND_NOT_EXPECTED:
        c = EXPECTED_NOT_FOUND_COLOR
        c = c if relation is EXPECTED_NOT_FOUND else FOUND_NOT_EXPECTED_COLOR
        prefix = prefix+c+list_char
        if isinstance(item, dict):
            log(LOG_DEBG, f"{c}{prefix}{key}\033[0m")
        else:
            log(LOG_DEBG, f"{c}{prefix}{key}: {item}\033[0m")
    elif relation is WRONG_TYPE:
        c = WRONG_TYPE_COLOR
        prefix = prefix+c+list_char
        log(LOG_DEBG, f"{c}{prefix}{key}; {got} [{item}]\033[0m")
    return c+follow_char


def pretty_print_comparison_dict(cd, pref="", root=False):
    t_char = "├── "
    i_char = "│   "
    l_char = "└── "
    empty = "    "

    for i, key in enumerate(cd):
        last = i == len(cd) - 1
        list_char = l_char if last else t_char
        follow_char = empty if last else i_char
        if root:
            list_char = follow_char = ""
        relation, next_cd, *literal_got = cd[key]
        p = pretty_print_item(pref, key, cd[key], follow_char, list_char)
        if relation is NOT_EQUAL or relation is EQUAL and EXPAND_EQUALS:
            if isinstance(next_cd, dict):
                pretty_print_comparison_dict(
                    next_cd, pref+p
                )


def pretty_compare_serials(exp, got):
    comparison_dict = serial_comparison_dict(exp, got)
    pretty_print_comparison_dict(comparison_dict, root=True)


def assert_equal_dicts(s_exp, s_got):
    cd = serial_comparison_dict(s_exp, s_got)
    for k in cd:
        relation, *v = cd[k]
        if relation is not EQUAL:
            return False
    return True


def assert_object_equal_dict(obj, dict_):
    return assert_equal_dicts(dict_, serialize_item(obj, []))