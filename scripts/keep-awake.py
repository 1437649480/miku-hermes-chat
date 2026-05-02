"""
Hermes Keep-Awake Service
Keeps Windows awake while WSL Hermes services are running.
The display can still turn off (power saving), but the system won't sleep.
"""
import ctypes
import time
import sys

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

kernel32 = ctypes.windll.kernel32


def prevent_sleep():
    kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def allow_sleep():
    kernel32.SetThreadExecutionState(ES_CONTINUOUS)


def main():
    print("[keep-awake] Preventing Windows from sleeping...")
    print("[keep-awake] Display will still turn off normally.")
    print("[keep-awake] Press Ctrl+C to allow sleep again.")
    try:
        while True:
            prevent_sleep()
            time.sleep(30)
    except KeyboardInterrupt:
        allow_sleep()
        print("\n[keep-awake] Sleep re-enabled. Bye!")


if __name__ == "__main__":
    main()
