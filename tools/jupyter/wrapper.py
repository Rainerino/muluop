import sys
import os
import json
import tempfile
import jupyterlab
from jupyter_client.kernelspec import KernelSpecManager
from jupyterlab.labapp import main

def register_bazel_kernel():
    """
    Registers the current Bazel Python environment as a Jupyter Kernel.
    """
    kernel_name = "bazel_kernel"
    
    with tempfile.TemporaryDirectory() as td:
        os.chmod(td, 0o755) 
        
        kernel_json = {
            "argv": [
                sys.executable,
                "-m", "ipykernel",
                "-f", "{connection_file}"
            ],
            "display_name": "Bazel Python (Current)",
            "language": "python",
        }

        with open(os.path.join(td, "kernel.json"), "w") as f:
            json.dump(kernel_json, f)

        try:
            KernelSpecManager().install_kernel_spec(
                source_dir=td,
                kernel_name=kernel_name,
                user=True,
                # replace_existing=True
            )
            print(f"[BazelWrapper] Registered kernel '{kernel_name}'")
        except Exception as e:
            print(f"[BazelWrapper] Failed to register kernel: {e}")
            
if __name__ == "__main__":
    
    register_bazel_kernel()
    # 1. Dynamically find where Bazel put the assets
    #    (This finds the directory relative to the python package)
    jlab_dir = os.path.join(os.path.dirname(jupyterlab.__file__),)
    
    # Check if the standard 'share' folder exists instead (common in pip installs)
    # Walk up from site-packages to find share/jupyter/lab
    current = os.path.dirname(jupyterlab.__file__)
    for _ in range(4): # Check 4 levels up
        candidate = os.path.join(current, 'share', 'jupyter', 'lab')
        if os.path.exists(os.path.join(candidate, 'static', 'index.html')):
            jlab_dir = candidate
            break
        current = os.path.dirname(current)

    print(f"[BazelWrapper] Setting app-dir to: {jlab_dir}")

    # 2. Inject the argument programmatically
    #    This is equivalent to running "jupyter lab --app-dir=..."
    sys.argv.append(f"--app-dir={jlab_dir}")

    sys.exit(main())