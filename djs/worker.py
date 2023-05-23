import time
from environs import Env

env = Env()
env.read_env()

hostname = env.str("HOSTNAME", "-")

print(f"[{hostname}] Doing some work...")
time.sleep(600)
print(f"[{hostname}] Finished the work.")
