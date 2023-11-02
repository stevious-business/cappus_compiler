from time import perf_counter

from locals import *

launch = perf_counter()

log_indent_count = 0

log_spacing = 4

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

def log(level, text, nts=False, **kwargs):
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
        pre = f"[\033[36m{SW_NAME}\033[0m::" \
            + f"\033[32m{ts()}\033[0m::" \
            + f"{level_colors[level]+level_texts[level]}\033[0m]"
        print(f"{pre} {' '*log_indent_count} \
{level_colors[level]}{text}\033[0m", **kwargs)