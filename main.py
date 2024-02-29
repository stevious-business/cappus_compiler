from os.path import exists
from sys import exit
from re import search

from compiler import compile
from locals import *
from cfclogger import log, timer, setup_logger, exit_logger

DEFAULT_FILE_PATH = "code/tests/expressions/postfix.cpl"
USE_DEFAULT_FILE_PATH = True

if __name__ == "__main__":

    setup_logger(True)

    print()
    log(LOG_INFO, "Launching CFC compiler!")
    print()

    return_code = 0

    exc = None

    try:
        if USE_DEFAULT_FILE_PATH:
            fp = DEFAULT_FILE_PATH
        else:
            fp = input("File path: ")
        while not exists(fp):
            log(LOG_WARN, "File does not exist!")
            fp = input("File path: ")

        timer.reset()

        with open(fp) as f:
            ending = search(r"\.[a-zA-Z]+$", f.name).group()
            file_pref = fp.removesuffix(ending)
            if not ending == ".cpl":
                # cappus programming language lmao
                log(LOG_WARN, "Your program is not a .cpl file!")
                log(LOG_WARN, f"Expected .cpl file, got {ending}")
            assembly = compile(f)
        with open(file_pref+".cal", "w") as f:
            assembly.export(f)

    except KeyboardInterrupt:
        print()
        log(LOG_FAIL, "Interrupted! Exiting...")
        return_code = 0
    except Exception as e:
        exc = e
        log(LOG_FAIL, f"Critical Error! Exiting...")
        return_code = 1
    else:
        t = round(timer.time_since_launch(), 2)
        log(LOG_INFO, f"Job done in {t}s!")
    finally:
        exit_logger()
        if exc:
            raise exc
        exit(return_code)
