load("@rules_python//python:defs.bzl", "py_binary")
load("@pip_compute//:requirements.bzl", "all_requirements", "requirement")

def jupyter_lab(name, deps = [], **kwargs):
    kernel_name = name + "_kernel"
    
    # 1. Build the Kernel Binary
    py_binary(
        name = kernel_name,
        srcs = ["//tools/jupyter:kernel_wrapper.py"],
        main = "//tools/jupyter:kernel_wrapper.py",
        deps = deps + all_requirements,
        visibility = ["//visibility:private"],
    )

    # 2. Build the Lab
    #    We assume the package is reachable via "//package_name"
    #    native.package_name() gets the current package (e.g. "tools")
    full_kernel_label = "//{}:{}".format(native.package_name(), kernel_name)

    py_binary(
        name = name,
        srcs = ["//tools/jupyter:wrapper.py"],
        main = "//tools/jupyter:wrapper.py",
        # We pass the LABEL (string) so the wrapper knows what to 'bazel run'
        args = ["--kernel_target", full_kernel_label],
        deps = [requirement("jupyterlab")],
        **kwargs
    )