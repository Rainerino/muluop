import os
import glob
import argparse

# --- CRITICAL FIX: Load from rules.bzl ---
BUCK_HEADER = """# @generated
load("@prelude//rules.bzl", "prebuilt_python_library")
"""

def sanitize_name(name):
    # e.g., "PyYAML" -> "pyyaml"
    return name.lower().replace("-", "_").replace(".", "_")

def generate():
    # 1. Parse arguments from the shell script
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-dir", required=True, help="Directory containing .whl files")
    args = parser.parse_args()

    # Ensure we use the absolute path provided by the caller
    wheel_dir = os.path.abspath(args.target_dir)
    output_file = os.path.join(wheel_dir, "BUCK")
    
    print(f"⚙️  Scanning directory: {wheel_dir}")

    all_target_names = []
    # 2. Find wheels
    whl_files = glob.glob(os.path.join(wheel_dir, "*.whl"))
    rules = []
    
    for file_path in whl_files:
        filename = os.path.basename(file_path)
        
        # Parse "package-version-..." -> "package"
        # Example: torch-2.1.2+cu121... -> torch
        dist_name = filename.split("-")[0]
        target_name = sanitize_name(dist_name)
        
        all_target_names.append(f":{target_name}")
        # 3. Generate the rule
        # Note: binary_src just needs the filename because the BUCK file 
        # is being written to the SAME directory as the wheels.
        rules.append(f"""
prebuilt_python_library(
    name = "{target_name}",
    binary_src = "{filename}",
    visibility = ["PUBLIC"],
)""")

# 5. Generate the "all_deps" Bundle Target
    #    This is the specific part you asked for!
    bundle_rule = f"""
python_library(
    name = "all_deps",
    deps = [
{chr(10).join(f'        "{name}",' for name in all_target_names)}
    ],
    visibility = ["PUBLIC"],
)
"""
    rules.append(bundle_rule)

    # 4. Write the BUCK file
    with open(output_file, "w") as f:
        f.write(BUCK_HEADER)
        f.write("\n".join(rules))
    
    print(f"✅ Generated {len(rules)} targets in {output_file}")

if __name__ == "__main__":
    generate()