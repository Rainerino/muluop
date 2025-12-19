
import time
import sys

# Import eCAL core (low-level bindings)
import ecal.nanobind_core as ecal_core
import torch

# Import High-level Publisher/Subscriber classes
# Note: ecal.core is deprecated in favor of ecal.nanobind_core for core functions,
# but high-level Publisher/Subscriber classes are still in ecal.core for now.
from ecal.core.publisher import StringPublisher
from ecal.core.subscriber import StringSubscriber

def torch_matmul_task(device):
    """
    Creates two random tensors and performs matrix multiplication.
    Returns a summary string of the result.
    """
    # 1. Create Data (Size 1000x1000)
    size = 1000
    tensor_a = torch.randn(size, size, device=device)
    tensor_b = torch.randn(size, size, device=device)

    # 2. Perform MatMul
    start_time = time.time()
    result = torch.matmul(tensor_a, tensor_b)
    duration = (time.time() - start_time) * 1000  # ms

    # 3. Calculate mean to have a simple value to print
    mean_val = result.mean().item()
    
    return f"Device: {device} | Matrix Size: {size}x{size} | Mean: {mean_val:.4f} | Time: {duration:.2f}ms"

def on_receive(topic_name, msg, time):
    """
    Callback function triggered when the Subscriber receives data.
    """
    print(f"[Subscriber] Received on '{topic_name}': {msg}")

def main():
    # --- 1. Setup PyTorch ---
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"CUDA Version: {torch.version.cuda}")

    print(f"--- Torch Configuration ---")
    print(f"Torch Version: {torch.__version__}")
    print(f"Target Device: {device}")
    print("---------------------------")

    # --- 2. Initialize eCAL ---
    # Initialize core with a process name
    ecal_core.initialize("TorchEcalMatmulNode")
    
    if not ecal_core.ok():
        print("eCAL initialization failed!")
        return

    # Create a Publisher (Topic Name: "MatmulResults")
    # We use StringPublisher for simplicity. In production, use Protobuf.
    pub = StringPublisher("MatmulResults")
    
    # Create a Subscriber (Topic Name: "MatmulResults")
    # This allows the script to listen to its own messages for demonstration.
    sub = StringSubscriber("MatmulResults")
    sub.set_callback(on_receive)

    print(f"eCAL Initialized. Publishing and Subscribing to 'MatmulResults'...")

    # --- 3. Main Loop ---
    counter = 0
    try:
        while ecal_core.ok() and counter < 100:
            # A. Do the Math
            msg_content = torch_matmul_task(device)
            
            # B. Prepare Message
            full_message = f"Msg #{counter} -> {msg_content}"
            
            # C. Publish (Noucing/Sending)
            pub.send(full_message)
            print(f"[Publisher] Sent: {full_message}")

            # D. Sleep briefly to simulate a cycle (e.g., 10Hz)
            time.sleep(0.1) 
            counter += 1
            
    except KeyboardInterrupt:
        print("\nStopping...")

    # --- 4. Cleanup ---
    ecal_core.finalize()
    print("eCAL Finalized. Exiting.")

if __name__ == "__main__":
    main()