from time import perf_counter

from functools import wraps

from locals import *

launch = perf_counter()

log_indent_count = 0

log_spacing = 4

log_file = None

class Timer:
    def __init__(self):
        self._timer = perf_counter()
    
    def reset(self):
        self._timer = perf_counter()

    def time_since_launch(self):
        return perf_counter() - self._timer

timer = Timer()

def sfmt(str_: str, len_: int, ws=False):
    strlen = len(str_)
    remain = len_ - strlen
    return str_ + remain * (" " if ws else ".")

def ts() -> str:
    global launch
    odd_len_text = f"{round(perf_counter()-launch, 4)}"
    return odd_len_text.zfill(10)

def log_indent():
    global log_indent_count
    log_indent_count += log_spacing

def log_dedent():
    global log_indent_count
    log_indent_count -= log_spacing

def setup_logger(LOG_TO_FILE=True):
    global log_file
    log_file = open("compilation.log", "w", encoding="utf-8")

def exit_logger():
    global log_file
    log_file.flush()
    log_file.close()

def log(level, text, nts=False, **kwargs):
    global log_file
    if level >= DBG.get():
        level_colors = {
            LOG_BASE: "\033[90m",
            LOG_VERB: "\033[35m",
            LOG_DEBG: "\033[2;33m",
            LOG_INFO: "\033[0m",
            LOG_WARN: "\033[1;33m",
            LOG_FAIL: "\033[41m"
        }
        level_texts = {
            LOG_BASE: "BASE",
            LOG_VERB: "VERB",
            LOG_DEBG: "DEBG",
            LOG_INFO: "INFO",
            LOG_WARN: "WARN",
            LOG_FAIL: "FAIL"
        }
        if nts: # No time stamp (no prefix)
            print(f"{level_colors[level]}{text}\033[0m", **kwargs)
            return
        t = ts()
        pre = f"[\033[36m{SW_NAME}\033[0m::" \
            + f"\033[32m{t}\033[0m::" \
            + f"{level_colors[level]+level_texts[level]}\033[0m]"
        final_text = f"{pre} {' '*log_indent_count} \
{level_colors[level]}{text}\033[0m"
        uncolored_pref = f"[{SW_NAME}::{t}::{level_texts[level]}]"
        uncolored_text = f"{uncolored_pref}{' '*log_indent_count}{text}"
        print(final_text, **kwargs)
        log_file.write(uncolored_text+"\n")

def logAutoIndent(function):
    @wraps(function)
    def inner(*args, **kwargs):
        log_indent()
        try:
            r = function(*args, **kwargs)
        except Exception as e:
            log_dedent()
            raise e
        else:
            log_dedent()
            return r
    return inner