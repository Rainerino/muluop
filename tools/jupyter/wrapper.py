import sys
import os
import json
import tempfile
import argparse
import jupyterlab
from jupyter_client.kernelspec import KernelSpecManager
from jupyterlab.labapp import main

def register_bazel_kernel(kernel_target):
    """
    Creates a kernel.json that invokes 'bazel run //path/to:kernel'
    """
    print(f"[BazelWrapper] Registering kernel target: {kernel_target}")

    with tempfile.TemporaryDirectory() as td:
        os.chmod(td, 0o755)
        
        # --- THIS IS THE KEY PART YOU ASKED FOR ---
        # We write a physical kernel.json file to disk
        kernel_json = {
            "argv": [
                "bazel", "run", kernel_target, 
                "--", 
                "-f", "{connection_file}"
            ],
            "display_name": "Bazel Kernel (Hot Reload)",
            "language": "python",
        }
        # ------------------------------------------

        with open(os.path.join(td, "kernel.json"), "w") as f:
            json.dump(kernel_json, f)

        # Install the kernel spec from the directory we just made
        KernelSpecManager().install_kernel_spec(
            source_dir=td,
            kernel_name="bazel_kernel",
            user=True,
            # replace_existing=True
        )

def get_bazel_app_dir():
    current_path = os.path.dirname(jupyterlab.__file__)
    return current_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel_target", help="The Bazel label (//pkg:target)")
    args, unknown_args = parser.parse_known_args()
    # Remove our custom flag so Jupyter doesn't see it
    sys.argv = [sys.argv[0]] + unknown_args
    
    workspace_dir = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    
    if workspace_dir:
        print(f"[BazelWrapper] Setting notebook root to: {workspace_dir}")
        sys.argv.append(f"--notebook-dir={workspace_dir}")
    else:
        # 2. Fallback: If variable is missing, warn the user
        print("-----------------------------------------------------------")
        print("[BazelWrapper] WARNING: BUILD_WORKSPACE_DIRECTORY is not set!")
        print("  - Are you running this with 'bazel run'?")
        print("  - If you run ./bazel-bin/... directly, this var is missing.")
        print("  - DEFAULTING TO SANDBOX ROOT. Your files may be LOST after build.")
        print("-----------------------------------------------------------")
        # Default to wherever the script is running (usually the sandbox root)
        sys.argv.append(f"--notebook-dir={os.getcwd()}")



    if args.kernel_target:
        register_bazel_kernel(args.kernel_target)
    
    app_dir = get_bazel_app_dir()
    if app_dir:
        sys.argv.append(f"--app-dir={app_dir}")

    # Prevent config pollution
    os.environ["JUPYTER_CONFIG_DIR"] = os.path.join(os.getcwd(), ".jupyter_config")
    
    sys.exit(main())