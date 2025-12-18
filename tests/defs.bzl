# tests/defs.bzl

def pytest_suite(name, srcs, deps = [], **kwargs):
    """
    Generates a python_test target for EACH file in srcs,
    plus a test_suite named 'name' that groups them all.
    """
    test_targets = []

    print(srcs)
    for src in srcs:
        # Generate a clean name: "python/test_dummy.py" -> "test_dummy"
        test_name = src.split("/")[-1].replace(".py", "")

        native.python_test(
            name = test_name,
            # bundle the specific test file AND the universal runner
            srcs = [src, "python/pytest_main.py"],
            # Tell python to execute the runner, not the test file directly
            main_module = "tests.python.pytest_main",
            deps = deps,
            **kwargs
        )
        test_targets.append(":" + test_name)

    print(test_targets)
    # Define the suite that groups them all together
    native.test_suite(
        name = name,
        tests = test_targets,
    )
