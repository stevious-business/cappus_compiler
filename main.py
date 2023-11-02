from os.path import exists
from sys import exit

from compiler import compile
from locals import *
from cfclogger import log

if __name__ == "__main__":

    print()
    log(LOG_INFO, "Launching CFC compiler!")
    print()

    try:

        fp = input("File path: ")
        while not exists(fp):
            log(LOG_WARN, "File does not exist!")
            fp = input("File path: ")
        
        with open(fp) as f:
            if not f.name.endswith(".cpl"):
                # cappus programming language lmao
                log(LOG_WARN, "Your program is not a .cpl file!")
            assembly = compile(f)

    except KeyboardInterrupt:
        print()
        log(LOG_FAIL, "Interrupted! Exiting...")
    except Exception as e:
        log(LOG_FAIL, f"Critical Error! {str(e)}")
        exit(1)
    else:
        log(LOG_INFO, "Job done!")
        exit(0)
