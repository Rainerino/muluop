import sys
import subprocess
import shlex
from concurrent.futures import ThreadPoolExecutor
import os 
import argparse
import tempfile  # <--- Added this

# Configuration
REQ_FILE = "third_party/python/requirements.txt"
MAX_WORKERS = int(os.cpu_count() or 8)  # Safer default if cpu_count is None

def parse_requirements(filepath):
    """
    Parses uv-generated requirements.txt into a list of individual
    requirement strings (preserving hashes) and global options.
    """
    requirements = []
    global_options = []
    
    current_line = []
    
    with open(filepath, 'r') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Handle line continuations (backslashes) that uv uses for hashes
            if line.endswith("\\"):
                current_line.append(line[:-1].strip())
                continue
            else:
                current_line.append(line)
                
            # Reconstruct the full logical line
            full_line = " ".join(current_line)
            current_line = [] # Reset buffer
            
            # Separate global flags (indexes) from packages
            if full_line.startswith("--extra-index-url") or \
               full_line.startswith("--index-url") or \
               full_line.startswith("--find-links") or \
               full_line.startswith("--trusted-host"):
                global_options.extend(shlex.split(full_line))
            else:
                requirements.append(full_line)
                
    return requirements, global_options

def download_package(args):
    """Worker function to download a single package using a temp file."""
    req_str, base_cmd = args
    
    # 1. Create a temporary requirements file for this single package
    # We do this because CLI args don't support --hash, but files do.
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as tmp:
        tmp.write(req_str)
        tmp_path = tmp.name

    try:
        # 2. Tell pip to download using this temp file
        cmd = base_cmd + ["-r", tmp_path]
        
        # Run pip quietly
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        
        # Clean print of the package name (stripping version/hash for readability)
        pkg_name = req_str.split('==')[0].split(' ')[0]
        print(f"  ✅ {pkg_name}")
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ FAILED: {req_str[:30]}...\n{e.output.decode()}")
        # Don't exit here, let other threads finish, but you might want to track failures
        sys.exit(1)
    finally:
        # 3. Clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-dir", required=True, help="Directory containing .whl files")
    args = parser.parse_args()

    wheel_dir = os.path.abspath(args.target_dir)
    
    if not os.path.exists(REQ_FILE):
        print(f"Error: Requirements file not found at {REQ_FILE}")
        sys.exit(1)

    reqs, global_opts = parse_requirements(REQ_FILE)
    
    # The base command for every worker
    base_cmd = [
        sys.executable, "-m", "pip", "download",
        "--dest", wheel_dir,
        "--no-deps",
        "--require-hashes" 
    ] + global_opts

    print(f"  🚀 Spawning {MAX_WORKERS} workers for {len(reqs)} packages...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all jobs
        args_list = [(req, base_cmd) for req in reqs]
        
        # Wait for all to complete
        list(executor.map(download_package, args_list))

if __name__ == "__main__":
    main()