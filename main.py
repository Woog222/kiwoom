import time
import sys

def loading_icon():
    chars = ["|", "/", "-", "\\"]
    delay = 0.1

    for _ in range(20):  # Repeat for a certain number of iterations
        for char in chars:
            sys.stdout.write("\rLoading " + char)
            sys.stdout.flush()
            time.sleep(delay)

    sys.stdout.write("\rLoading Complete!\n")

if __name__ == "__main__":
    loading_icon()