load("@rules_python//python:defs.bzl", "py_binary")
load("@pip_compute//:requirements.bzl", "all_requirements")

def jupyter_lab(name, deps = [], **kwargs):
    """
    Creates a JupyterLab target with all pip dependencies included.
    """
    
    # We force the wrapper script to be the one we defined above
    wrapper_location = "//tools/jupyter:wrapper.py"
    
    py_binary(
        name = name,
        srcs = [wrapper_location],
        main = wrapper_location,
        deps = deps + all_requirements, # <--- AUTOMATION HERE
        **kwargs
    )
