from os.path import exists
from sys import exit
from re import search

from compiler import compile
from locals import *
from cfclogger import log, timer

if __name__ == "__main__":

    print()
    log(LOG_INFO, "Launching CFC compiler!")
    print()

    try:

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
    except Exception as e:
        log(LOG_FAIL, f"Critical Error! {str(e)}")
        exit(1)
    else:
        t = round(timer.time_since_launch(), 2)
        log(LOG_INFO, f"Job done in {t}s!")
        exit(0)
