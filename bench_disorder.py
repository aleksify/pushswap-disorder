#!/usr/bin/env python3

import argparse
import os
import random
import subprocess
import sys


def count_inversions(arr):
    n = len(arr)
    return sum(1 for i in range(n) for j in range(i + 1, n) if arr[i] > arr[j])


def swap_delta(arr, i, j):
    """Compute change in inversion count if arr[i] and arr[j] are swapped. O(n)."""
    n = len(arr)
    delta = 0
    a, b = arr[i], arr[j]
    # The (i,j) pair itself flips
    if a > b:
        delta -= 1
    else:
        delta += 1
    # Check all other positions against i and j
    for k in range(n):
        if k == i or k == j:
            continue
        v = arr[k]
        # Old contribution of position i (value a) vs k
        if k < i:
            if v > a:
                delta -= 1  # was inversion, won't be after (b goes here)
            if v > b:
                delta += 1  # wasn't inversion with a, will be with b
        elif k > i:
            if a > v:
                delta -= 1
            if b > v:
                delta += 1
        # Old contribution of position j (value b) vs k
        if k < j:
            if v > b:
                delta -= 1
            if v > a:
                delta += 1
        elif k > j:
            if b > v:
                delta -= 1
            if a > v:
                delta += 1
    return delta


def generate_from_sorted(n, lo, hi):
    arr = list(range(n))
    total_pairs = n * (n - 1) // 2
    inversions = 0
    for _ in range(10000):
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, min(i + max(n // 5, 2), n - 1))
        delta = swap_delta(arr, i, j)
        new_inv = inversions + delta
        d = new_inv / total_pairs
        if lo <= d <= hi:
            arr[i], arr[j] = arr[j], arr[i]
            return arr, d
        if d <= hi:  # accept swap (still below target, keep going)
            arr[i], arr[j] = arr[j], arr[i]
            inversions = new_inv
        # else: skip swap (would overshoot)
    return None, None


def generate_from_reverse(n, lo, hi):
    arr = list(range(n - 1, -1, -1))
    total_pairs = n * (n - 1) // 2
    inversions = total_pairs  # fully reversed = all pairs inverted
    for _ in range(10000):
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, min(i + max(n // 5, 2), n - 1))
        delta = swap_delta(arr, i, j)
        new_inv = inversions + delta
        d = new_inv / total_pairs
        if lo <= d <= hi:
            arr[i], arr[j] = arr[j], arr[i]
            return arr, d
        if d >= lo:  # accept swap (still above target, keep going)
            arr[i], arr[j] = arr[j], arr[i]
            inversions = new_inv
        # else: skip swap (would undershoot)
    return None, None


def generate_from_shuffled(n, lo, hi):
    arr = list(range(n))
    random.shuffle(arr)
    total_pairs = n * (n - 1) // 2
    inversions = count_inversions(arr)
    d = inversions / total_pairs
    if lo <= d <= hi:
        return arr, d
    going_down = d > hi
    for _ in range(10000):
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, min(i + max(n // 5, 2), n - 1))
        delta = swap_delta(arr, i, j)
        new_inv = inversions + delta
        new_d = new_inv / total_pairs
        if lo <= new_d <= hi:
            arr[i], arr[j] = arr[j], arr[i]
            return arr, new_d
        # Accept if moving toward target
        if going_down and new_d < d:
            arr[i], arr[j] = arr[j], arr[i]
            inversions = new_inv
            d = new_d
        elif not going_down and new_d > d:
            arr[i], arr[j] = arr[j], arr[i]
            inversions = new_inv
            d = new_d
    return None, None


def generate_input(n, lo, hi):
    mid = (lo + hi) / 2
    if mid <= 0.2:
        return generate_from_sorted(n, lo, hi)
    elif mid >= 0.8:
        return generate_from_reverse(n, lo, hi)
    else:
        return generate_from_shuffled(n, lo, hi)


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


def check_binary():
    if not os.path.isfile('./push_swap'):
        print("Error: ./push_swap binary not found. Build it first (make).", file=sys.stderr)
        sys.exit(1)
    if not os.access('./push_swap', os.X_OK):
        print("Error: ./push_swap exists but is not executable.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Benchmark push_swap by disorder window')
    parser.add_argument('-n', type=int, default=500, help='Input size (default: 500)')
    parser.add_argument('-i', type=int, default=30, help='Iterations per window (default: 30)')
    parser.add_argument('-d', type=str, default=None, help='Disorder range LO-HI, e.g. "0.05-0.10"')
    parser.add_argument('--log', action='store_true', help='Save generated args to logs/ files')
    args = parser.parse_args()
    check_binary()

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

    if args.log:
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

    run_idx = 0
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
            if args.log:
                logfile = os.path.join(log_dir, f"{run_idx:04d}_d{d:.4f}_ops{ops}.txt")
                with open(logfile, 'w') as f:
                    f.write(' '.join(str(x) for x in arr) + '\n')
                run_idx += 1


if __name__ == '__main__':
    main()
