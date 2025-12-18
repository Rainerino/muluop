import sys
import subprocess
import shlex
import os
import argparse
import tempfile
import time
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try importing tqdm for progress bar
try:
    from tqdm import tqdm
except ImportError:
    print("Please install tqdm: pip install tqdm")
    sys.exit(1)

# Configuration
REQ_FILE = "third_party/python/requirements.txt"
MAX_WORKERS = int(os.cpu_count() or 8)


def format_bytes(size):
    """Converts bytes to human readable string (KB, MB)."""
    if size is None:
        return "Unknown"
    power = 2**10
    n = size
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    count = 0
    while n > power:
        n /= power
        count += 1
    return f"{n:.2f} {power_labels[count]}B"


def normalize_package_name(name):
    """
    Wheel filenames replace dashes with underscores.
    e.g. 'google-cloud-storage' -> 'google_cloud_storage'
    """
    return name.replace("-", "_")


def parse_package_info(req_str):
    """
    Extracts (name, version) from a requirement string.
    Assumes uv/pip-compile format like 'package==1.2.3 ...'
    """
    # Remove environment markers or hashes for parsing name
    base = req_str.split(" ")[0]

    if "==" in base:
        name, version = base.split("==", 1)
        return name, version
    else:
        # Fallback for unpinned deps (rare in lockfiles)
        return base, "*"


def find_downloaded_file(target_dir, pkg_name, version):
    """
    Finds the actual file on disk matching the package name and version.
    Returns path and size.
    """
    safe_name = normalize_package_name(pkg_name)

    # Pattern to match wheels or sdists
    # Matches: package_name-1.2.3-*.whl OR package-name-1.2.3.tar.gz
    # Note: We use glob to find the specific build tag (e.g. cp39-manylinux...)
    patterns = [
        f"{safe_name}-{version}-*.whl",
        f"{safe_name}-{version}.tar.gz",
        f"{safe_name}-{version}.zip",
        f"{pkg_name}-{version}-*.whl",  # Sometimes names aren't normalized as expected
    ]

    for pattern in patterns:
        matches = glob.glob(os.path.join(target_dir, pattern))
        if matches:
            # Return the most recently modified file if multiple match
            best_match = max(matches, key=os.path.getmtime)
            return best_match, os.path.getsize(best_match)

    return None, 0


def parse_requirements(filepath):
    requirements = []
    global_options = []
    current_line = []

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Requirements file not found at {filepath}")

    with open(filepath, "r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.endswith("\\"):
                current_line.append(line[:-1].strip())
                continue
            else:
                current_line.append(line)

            full_line = " ".join(current_line)
            current_line = []

            if any(
                full_line.startswith(x)
                for x in [
                    "--extra-index-url",
                    "--index-url",
                    "--find-links",
                    "--trusted-host",
                ]
            ):
                global_options.extend(shlex.split(full_line))
            else:
                requirements.append(full_line)

    return requirements, global_options


def download_package(args):
    req_str, base_cmd, target_dir = args
    pkg_name, pkg_version = parse_package_info(req_str)

    start_time = time.time()

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write(req_str)
        tmp_path = tmp.name

    result = {
        "name": pkg_name,
        "version": pkg_version,
        "success": False,
        "size_bytes": 0,
        "size_str": "0 B",
        "time": 0.0,
        "error": None,
    }

    try:
        cmd = base_cmd + ["-r", tmp_path]

        # Run pip quietly; we don't need its stdout anymore
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        elapsed = time.time() - start_time
        result["time"] = elapsed
        result["success"] = True

        # 🔍 Verify file existence and get size directly from disk
        f_path, f_size = find_downloaded_file(target_dir, pkg_name, pkg_version)

        if f_path:
            result["size_bytes"] = f_size
            result["size_str"] = format_bytes(f_size)
        else:
            # If pip succeeded but we can't find the file, it might be a naming edge case
            result["size_str"] = "Cached?"

    except subprocess.CalledProcessError as e:
        result["error"] = e.stderr
    except Exception as e:
        result["error"] = str(e)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target-dir", required=True, help="Directory containing .whl files"
    )
    args = parser.parse_args()

    wheel_dir = os.path.abspath(args.target_dir)
    os.makedirs(wheel_dir, exist_ok=True)

    print(f"📂 Target Directory: {wheel_dir}")
    print(f"📖 Parsing {REQ_FILE}...")

    try:
        reqs, global_opts = parse_requirements(REQ_FILE)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    base_cmd = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--dest",
        wheel_dir,
        "--no-deps",
        "--require-hashes",
        "--quiet",  # Keep pip quiet, we handle UI
    ] + global_opts

    print(f"🚀 Spawning {MAX_WORKERS} workers for {len(reqs)} packages...\n")

    total_download_size = 0
    failures = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        jobs = [
            executor.submit(download_package, (req, base_cmd, wheel_dir))
            for req in reqs
        ]

        with tqdm(total=len(reqs), unit="pkg", desc="Progress", ncols=100) as pbar:
            for future in as_completed(jobs):
                res = future.result()
                pbar.update(1)

                if res["success"]:
                    total_download_size += res["size_bytes"]
                    # Log success cleanly above the progress bar
                    tqdm.write(
                        f"  ✅ {res['name']:<25} {res['version']:<10} | {res['size_str']:>9} | {res['time']:.1f}s"
                    )
                else:
                    failures.append(res)
                    tqdm.write(f"  ❌ FAILED: {res['name']}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"  Total Packages: {len(reqs)}")
    print(f"  Successful:     {len(reqs) - len(failures)}")
    print(f"  Failed:         {len(failures)}")
    print(f"  Total Size:     {format_bytes(total_download_size)}")

    if failures:
        print("\n❌ Failures:")
        for fail in failures:
            err_msg = (
                fail["error"].strip().split("\n")[-1]
                if fail["error"]
                else "Unknown error"
            )
            print(f"  - {fail['name']}: {err_msg[:120]}...")
        sys.exit(1)
    else:
        print("\n✨ Done.")


if __name__ == "__main__":
    main()
