import torch
import ecal.nanobind_core as ecal_core


def main():
    # 1. Test Torch
    print(f"Torch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    # 2. Test eclipse-ecal
    # Initialize eCAL (requires a process name)
    ecal_core.initialize("BazelEcalTest")
    print(f"eCAL initialized: {ecal_core.ok()}")
    
    # ... your logic ...

    ecal_core.finalize()


if __name__ == "__main__":
    main()