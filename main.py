from os.path import exists
from sys import exit, argv
from re import search
from io import StringIO
from json import loads, dumps

from unit_tests import (
    test_all,
    test_one,
    pretty_serialized_item,
    CONF_FILE_PATH
)
from compiler import compile, compile_unit_test
from locals import *
from cfclogger import log, timer, setup_logger, exit_logger

SINGULAR_UNIT_NAME = "funcdef"
DEFAULT_FILE_PATH = "code/tests/funcdef.cpl"
DEFAULT_UNIT_NAME = "funcdef"
DEFAULT_EXPECTATIONS = "i"

if __name__ == "__main__":

    setup_logger(True)

    print(argv)

    progname, *args = argv
    mode = None
    if len(args):
        mode = args[0].lower()

    if mode not in ("help", "--help"):
        print()
        log(LOG_INFO, "Launching Compiler For C.A.P.P.U.S.!")
        print()

    return_code = 0

    exc = None

    timer.reset()

    ALLOWED_MODES = (None, "create-unit-test", "perform-unit-tests",
                     "file-preset", "single-unit-test", "help", "--help")

    try:
        if mode not in ALLOWED_MODES:
            log(LOG_FAIL, f"Unknown mode {mode}!")
            log(LOG_FAIL, f"Run with --help for help.")
            exit(1)
        elif mode == "create-unit-test":
            if len(args) > 3:
                # create-unit-test base-file test-name expectations
                mode_, base_file, test_name, expectations, *extra_ = args
            else:
                base_file = DEFAULT_FILE_PATH
                test_name = DEFAULT_UNIT_NAME
                expectations = DEFAULT_EXPECTATIONS
            if not exists(base_file):
                log(LOG_FAIL, f"Base file {base_file} does not exist.")
                raise FileNotFoundError
            with open(base_file) as f:
                results = {}
                code_str = "".join(f.readlines())
                for key, item in compile_unit_test(StringIO(code_str)):
                    results[key] = item
            with open("unit_tests/tests/"+test_name+".unit_test", "w") as wf:
                log(LOG_VERB, "Writing meta block!")
                wf.write(META_BLOCK % test_name)
                log(LOG_VERB, "Writing code block!")
                wf.write(CODE_BLOCK % code_str)
                for expectation in expectations:
                    log(LOG_VERB,
                        f"Writing {EXPECTATIONS_TABLE[expectation]} block!")
                    wf.write(EXPECTATION_BLOCK % (
                        EXPECTATIONS_TABLE[expectation],
                        pretty_serialized_item(
                            results[EXPECTATIONS_TABLE[expectation]],
                            do_indent=False
                        )
                    ))
            with open(CONF_FILE_PATH) as f:
                configuration = loads("".join(f.readlines()))
            if test_name not in configuration["test_files"]:
                configuration["test_files"].append(test_name)
            with open(CONF_FILE_PATH, "w") as f:
                f.writelines(dumps(configuration, indent=4))
        elif mode == "perform-unit-tests":
            # Test_all() will return 0 on success
            num_fails = test_all()
            success = num_fails == 0
            if not success:
                if "--ignore-unit-fails" not in args:
                    log(
                        LOG_FAIL,
                        f"{num_fails} unit tests have failed."
                        + " To suppress these errors and continue, run with"
                        + " --ignore-unit-fails."
                    )
                    raise RuntimeError("Unit tests have failed")
        elif mode == "single-unit-test":
            if len(args) > 1:
                unit_name = args[1]
            else:
                unit_name = SINGULAR_UNIT_NAME
            is_fail = test_one(unit_name)
            if is_fail:
                log(LOG_FAIL, "Failed")
                raise RuntimeError("Unit test failed")
        elif mode is None or mode == "file-preset":
            if mode == "file-preset":
                if len(args) > 1:
                    fp = args[1]
                else:
                    fp = DEFAULT_FILE_PATH
            else:
                fp = input("File path: ")
            while not exists(fp):
                log(LOG_WARN, "File does not exist!")
                fp = input("File path: ")

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
        elif mode in ("help", "--help"):
            DBG.set_silent(True)
            print(SW_HELP_STRING)

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
