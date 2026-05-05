#!/usr/bin/env python3

import argparse
import random
import subprocess
import sys


def disorder(arr):
    n = len(arr)
    if n <= 1:
        return 0.0
    inversions = sum(1 for i in range(n) for j in range(i + 1, n) if arr[i] > arr[j])
    total = n * (n - 1) // 2
    return inversions / total


def generate_from_sorted(n, lo, hi):
    arr = list(range(n))
    for _ in range(10000):
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, min(i + max(n // 5, 2), n - 1))
        arr[i], arr[j] = arr[j], arr[i]
        d = disorder(arr)
        if lo <= d <= hi:
            return arr, d
        if d > hi:
            arr[i], arr[j] = arr[j], arr[i]
    return None, None


def generate_from_reverse(n, lo, hi):
    arr = list(range(n - 1, -1, -1))
    for _ in range(10000):
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, min(i + max(n // 5, 2), n - 1))
        arr[i], arr[j] = arr[j], arr[i]
        d = disorder(arr)
        if lo <= d <= hi:
            return arr, d
        if d > hi:
            arr[i], arr[j] = arr[j], arr[i]
    return None, None


def generate_shuffled(n, lo, hi):
    for _ in range(1000):
        arr = list(range(n))
        random.shuffle(arr)
        d = disorder(arr)
        if lo <= d <= hi:
            return arr, d
    return None, None


def generate_input(n, lo, hi):
    if hi <= 0.20:
        return generate_from_sorted(n, lo, hi)
    elif lo >= 0.80:
        return generate_from_reverse(n, lo, hi)
    else:
        return generate_shuffled(n, lo, hi)


def run_push_swap(arr):
    args = ' '.join(str(x) for x in arr)
    result = subprocess.run(
        ['./push_swap', args],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    if not result.stdout.strip():
        return 0
    return len(result.stdout.strip().split('\n'))


def main():
    parser = argparse.ArgumentParser(description='Benchmark push_swap by disorder window')
    parser.add_argument('-n', type=int, default=500, help='Input size (default: 500)')
    parser.add_argument('-i', type=int, default=30, help='Iterations per window (default: 30)')
    parser.add_argument('-d', type=str, default=None, help='Disorder range LO-HI, e.g. "0.05-0.10"')
    args = parser.parse_args()

    if args.d:
        parts = args.d.split('-', 1)
        try:
            lo = float(parts[0])
            hi = float(parts[1])
        except (ValueError, IndexError):
            print(f"Error: invalid disorder range '{args.d}', use format LO-HI", file=sys.stderr)
            sys.exit(1)
        windows = [(lo, hi)]
    else:
        windows = [(i * 0.05, (i + 1) * 0.05) for i in range(20)]

    for lo, hi in windows:
        for _ in range(args.i):
            arr, d = generate_input(args.n, lo, hi)
            if arr is None:
                print(f"disorder=FAILED  ops=N/A  (window {lo:.2f}-{hi:.2f})", file=sys.stderr)
                continue
            ops = run_push_swap(arr)
            if ops is None:
                print(f"disorder={d:.4f}  ops=ERROR", file=sys.stderr)
                continue
            print(f"disorder={d:.4f}  ops={ops}")


if __name__ == '__main__':
    main()
