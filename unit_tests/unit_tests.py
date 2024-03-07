from json import loads, JSONDecodeError

from os.path import exists

from io import StringIO

from compiler.compiler import compile_unit_test
from compiler.codegen.asm import Assembly

from cfclogger import log, LOG_FAIL, LOG_WARN, LOG_INFO, LOG_DEBG, LOG_VERB

from .object_serializer import (
    assert_object_equal_dict,
    pretty_compare_serials,
    serialize_item
)

CONF_FILE_PATH = "unit_tests/test_configuration.json"


class Module:
    def __init__(self):
        self.module_type = ""
        self.lines: list[str] = []
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent

    def set_module_type(self, mtype):
        self.module_type = mtype

    def add_lines(self, lines):
        self.lines += lines

    def reinit(self):
        # Effectively load this module.
        if self.module_type == "META":
            for line in self.lines:
                if line.startswith("NAME"):
                    name = line.removeprefix("NAME ")
                    self.parent.name = name.removesuffix("\n")
                elif line.startswith("DESCRIPTION"):
                    desc = line.removeprefix("DESCRIPTION ")
                    self.parent.description = desc.removesuffix("\n")
                elif len(line.split()) == 0:
                    log(LOG_WARN, f"Empty line in unit test meta "
                        + f"(Test name {self.parent.test_name})")
                else:
                    log(LOG_WARN, f"Invalid argument for unit test meta: "
                        + line.split()[0])
        elif self.module_type == "TEST_CODE":
            self.parent.code = "".join(self.lines)
        elif self.module_type.startswith("EXPECTED_"):
            try:
                self.parent.expectations[
                    self.module_type.removeprefix("EXPECTED_")
                ] = loads("".join(self.lines))
            except JSONDecodeError:
                log(LOG_FAIL, f"Unable to parse {self.module_type} "
                    + f"(Unit test {self.parent.name})")
                raise SyntaxError("Bad unit test syntax!")


class UnitTest:
    def __init__(self, test_name, filename=""):
        self.modules: list[Module] = []
        self.test_name = test_name
        self.filename = filename
        self.name = ""
        self.description = ""
        self.code = ""
        self.expectations = {}

    def module_by_type(self, type_):
        for module in self.modules:
            if module.module_type == type_:
                return module
        return None

    def add_module(self, module: Module):   # TODO: max. 1 module of each type
        self.modules.append(module)
        module.set_parent(self)

    def init_modules(self):
        for module in self.modules:
            module.reinit()

    def execute(self, silent=True):
        log(LOG_DEBG, f"Starting unit test {self.name}...")
        try:
            available_criteria = {}
            log(LOG_VERB, f"Compileable code:\n{self.code}")
            for name, obj in compile_unit_test(StringIO(self.code)):
                available_criteria[name] = obj
        except Exception:
            log(LOG_FAIL, f"Compilation failed for test {self.name}.")
            log(LOG_FAIL, f"To repeat this test, compile {self.test_name}.")
            if silent:
                return -1
            raise
        n_fails = 0
        for expectation_name in self.expectations:
            log(LOG_DEBG, f"-> Comparing expectation {expectation_name}...")
            expectation_module = self.expectations[expectation_name]
            if (returned_object := available_criteria.get(
                    expectation_name, None)) is not None:
                if not assert_object_equal_dict(returned_object,
                                                expectation_module):
                    n_fails += 1
                    log(LOG_FAIL, f"Differing criteria: {expectation_name}")
                    pretty_compare_serials(
                        expectation_module,
                        serialize_item(returned_object, [])
                    )
            else:
                log(LOG_DEBG, f"Compilation failed at an earlier stage; "
                    + f"{expectation_name} was not yielded.")
                n_fails += 1
        return n_fails


def obtain_configuration():
    log(LOG_DEBG, f"Loading configuration from {CONF_FILE_PATH}...")
    try:
        with open(CONF_FILE_PATH) as f:
            data = "".join(f.readlines())
        configuration = loads(data)
        return configuration
    except JSONDecodeError:
        log(LOG_FAIL, "JSON error while loading unit test configuration")
        raise


def obtain_test_from_name(name, conf) -> UnitTest | None:
    log(LOG_VERB, f"Building unit test {name}...")
    for filename_format in conf["filename_patterns"]:
        potential_filename = filename_format.replace(r"%NAME%", name)
        if exists(potential_filename):
            with open(potential_filename) as f:
                lines = f.readlines()
                final_filename = potential_filename
                break
    else:
        log(LOG_FAIL, f"Found no file for test '{name}'")
        return None
    test_obj = UnitTest(name, filename=final_filename)
    m = None
    temp_line_list = []
    for line in lines:
        if line.startswith("--- START"):
            module_name = line.removeprefix("--- START ").removesuffix(
                " ---\n"
            )
            m = Module()
            m.set_module_type(module_name)
            temp_line_list = []
        elif line == "--- END ---\n":
            # strip \n from last actual line
            temp_line_list[-2] = temp_line_list[-2].removesuffix("\n")
            # ignore first and last object; they are newlines
            m.add_lines(temp_line_list[1:-1])
            test_obj.add_module(m)
        else:
            temp_line_list.append(line)
    test_obj.init_modules()
    return test_obj


def test_one(name):
    conf = obtain_configuration()
    test: UnitTest = obtain_test_from_name(name, conf)
    if test is None:
        raise FileNotFoundError
    result = test.execute(silent=False)
    return result


def test_all() -> int:
    conf = obtain_configuration()

    test_filenames = conf["test_files"]
    num_tests = len(test_filenames)

    log(LOG_DEBG, f"Detected {num_tests} unit tests!")

    succeeded_tests = []
    failed_tests = []

    for test_filename in test_filenames:
        test: UnitTest = obtain_test_from_name(test_filename, conf)
        if test is None:
            continue
        result = test.execute()
        if result == 0:
            # 0 = success
            succeeded_tests.append(test_filename)
            log(LOG_INFO, f"\033[42mSuccess for test {test_filename}!")
        else:
            failed_tests.append(test_filename)
            log(LOG_INFO, f"\033[41mFailure for test {test_filename}!")
        log(LOG_INFO, "", True)

    log(LOG_INFO,
        f"{len(succeeded_tests)}/{num_tests} unit tests have succeeded.")

    if len(failed_tests):
        log(LOG_WARN, "Some unit tests have failed. Consider debugging.")

    log(LOG_INFO, "", True)

    return len(failed_tests)
