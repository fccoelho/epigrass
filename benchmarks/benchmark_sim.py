
import time
import numpy as np
from Epigrass.manager import Simulate
from Epigrass.simobj import graph
import os
import redis

# Connect to Redis
redis_client = redis.StrictRedis()

def run_benchmark(parallel=False, steps=100):
    print(f"Running benchmark (parallel={parallel}, steps={steps})...")
    redis_client.flushall()
    
    # Create a simple simulation
    # Using flu.epg from demos if possible
    epg_path = 'demos/flu.epg'
    if not os.path.exists(epg_path):
        print(f"Error: {epg_path} not found.")
        return
        
    S = Simulate(fname=epg_path)
    S.parallel = parallel
    
    start_time = time.time()
    S.runGraph(S.g, iterations=steps)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"Completed in {duration:.4f} seconds.")
    return duration

if __name__ == "__main__":
    # Ensure we are in the root
    if not os.path.exists('demos'):
        os.chdir('..')
        
    print("--- Performance Benchmark ---")
    
    # Run sequential
    dur_seq = run_benchmark(parallel=False, steps=50)
    
    # Run parallel
    dur_par = run_benchmark(parallel=True, steps=50)
    
    print("\nResults:")
    print(f"Sequential: {dur_seq:.4f}s")
    print(f"Parallel:   {dur_par:.4f}s")
