import time
import sys
import os
import psutil
from itertools import repeat
from multiprocessing import Pool, cpu_count
from threading import Thread
import tempfile

def stress_disk(x):
    cnt = 0
    while True:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'Stress Disk' * 8000)  # Appending 1 MB of data
            tmp_file.flush()  # Flush the file buffer
        cnt += 1

def stress_cpu_ram(x, sleeptime=0, busycycles=100000):
    cnt = 0

    while True:
        if sleeptime and cnt % busycycles == 0:
            time.sleep(sleeptime)

        # Stress CPU
        for _ in range(50000):
            x * x

        # Stress RAM (allocate and deallocate memory)
        memory_chunk = bytearray(1024 * 1024 * 10)  # Allocate 10 MB
        del memory_chunk

        cnt += 1

def f(x, sleeptime=0, busycycles=100000):
    pid = os.getpid()
    process = psutil.Process(pid)

    # Start the disk stress thread
    disk_thread = Thread(target=stress_disk, args=(x,))
    disk_thread.start()

    # Run CPU and RAM stress in the main thread
    stress_cpu_ram(x, sleeptime, busycycles)

    # Wait for the disk stress thread to finish
    disk_thread.join()

if __name__ == '__main__':
    sleeptime = 0.0 if len(sys.argv) <= 1 else float(sys.argv[1])
    busycycles = 100000 if len(sys.argv) <= 2 else int(sys.argv[2])
    processes = cpu_count() if len(sys.argv) <= 3 else int(sys.argv[3]) if 0 < int(sys.argv[3]) <= cpu_count() else cpu_count()

    print(f'Running with sleep time of {sleeptime}s per {busycycles} cycles utilizing {processes} cores. Press Ctrl+C to stop.')

    with Pool(processes) as pool:
        pool.starmap(f, zip(range(processes), repeat(sleeptime), repeat(busycycles)))
