# Disorder Threshold Testing for push_swap

Test your push_swap with specified disorder range.

## The Problem

The current subject requirements for O(n²) sorting algorithms specify a disorder threshold of 0.2, but this threshold is problematic for naive O(n²) implementations.

At `n=500` with disorder values in the range of **0.15–0.19**, simple O(n²) algorithms can explode to **10,000+ operations** in certain cases. This behavior is inherent to any straightforward O(n²) algorithm — the only way to avoid it is to introduce optimizations (LIS-based approaches, cost calculation heuristics, etc.), but at that point the algorithm is no longer truly O(n²). It's a Catch-22.

## Why This Hasn't Been Caught

Testing with specific disorder values is non-trivial, and the subject only demonstrates how to test with random data — which always lands close to a disorder of ~0.5. As a result:

- Most students never test specific disorder ranges at all.
- Those who do often use flawed approaches. E.g. they generate "20% disorder," they concatenate 80% of a sorted array with 20% of a reverse-sorted array. The resulting disorder metric reads as 20%, but the data is trivially sortable by any algorithm and bears no resemblance to real-world random data with 20% disorder.

## What This Tool Does

This repository contains a Python script that generates arrays with **specific, accurate disorder values** — producing data that reflects realistic random distributions at the requested disorder level, not artificially constructed edge cases. It then pipes the generated input into your `push_swap` binary and reports the resulting operation count.

Disorder is measured as the inversion ratio: the number of out-of-order pairs `(i, j)` where `i < j` and `arr[i] > arr[j]`, divided by the total number of pairs `n(n-1)/2`. A fully sorted array has disorder 0.0, a fully reversed array has disorder 1.0, and a uniformly shuffled array averages around 0.5.

To produce data that genuinely matches a target window, the script picks a generation strategy based on the requested range:

- **Low disorder (≤ 0.20)** — start from a sorted array and apply small local swaps until the disorder lands in the window.
- **High disorder (≥ 0.80)** — start from a reversed array and do the same in reverse.
- **Mid range** — repeatedly shuffle and accept the first array whose disorder falls in the window.

This avoids the trap of constructing artificial inputs (like sorted+reversed concatenations) that hit the right inversion count but don't behave like real data.

## The Challenge

> Try your simple O(n²) algorithm against data generated with disorder values in the range **0.15–0.20**, running at least **100 iterations**.

If your algorithm is genuinely O(n²) without hidden optimizations, you will see operation counts explode in some of those cases. If it doesn't, your algorithm is doing more than pure O(n²) work.

## Usage

The script is meant to be run from the root of your `push_swap` project, where your compiled `push_swap` binary lives.

### Option 1: Clone inside your project

```
cd /path/to/push_swap
git clone https://github.com/aleksify/pushswap-disorder
python3 ./pushswap-disorder/bench_disorder.py
```

### Option 2: Curl it

If you'd rather not clone, you can just run the script in your project directory:

```
cd /path/to/push_swap
curl -sL https://raw.githubusercontent.com/aleksify/pushswap-disorder/main/bench_disorder.py | python3 - -d 0.15-0.20 -i 100
```

(Arguments after the `-` are forwarded to the script.)

### Examples

**Sweep all disorder windows** (0.00–0.05, 0.05–0.10, …, 0.95–1.00) with default settings (`n=500`, 30 iterations per window):

```
python3 ./pushswap-disorder/bench_disorder.py
```

**Target a specific disorder window** — the interesting case for stress-testing O(n²) algorithms:

```
python3 ./pushswap-disorder/bench_disorder.py -d 0.15-0.20 -i 100
```

**Custom input size and iteration count:**

```
python3 ./pushswap-disorder/bench_disorder.py -n 500 -i 100 -d 0.15-0.20
```

### Arguments

- `-n` — input size (default: `500`)
- `-i` — iterations per disorder window (default: `30`)
- `-d` — disorder range in `LO-HI` format, e.g. `0.05-0.10`. If omitted, the script sweeps all twenty 5%-wide windows from 0.00 to 1.00.
- `--log` — save generated input for each iteration to a separate file in `logs/`. Files are named `NNNN_dX.XXXX_opsY.txt` (index, disorder, ops) and contain the space-separated arguments passed to `push_swap`, making it easy to reproduce any run.

### Output

Each iteration prints one line to stdout:

```
disorder=0.1734  ops=8421
disorder=0.1812  ops=4127
disorder=0.1655  ops=12903
...
```

Failures (couldn't generate an array in the window, or `push_swap` returned a non-zero exit code) are reported on stderr so they don't pollute results when piping to a file or to `sort`/`awk` for analysis.

### Suggested workflow

To find your worst case in the danger zone:

```
python3 ./pushswap-disorder/bench_disorder.py -d 0.15-0.20 -i 100 | sort -t= -k3 -n | tail
```

This runs 100 iterations in the 0.15–0.20 window and shows you the ten highest operation counts. If any of those exceed the subject's threshold, your O(n²) implementation has a problem the standard test suite won't catch.

## Proposed Solution

One of the following changes should be made to the subject:

1. **Allow students to pick disorder thresholds themselves**, with reasoning, or
2. **Lower the disorder threshold for O(n²) algorithms from 0.2 to 0.1**, which keeps naive O(n²) implementations within a reasonable operation budget.

## Requirements

- Python 3
- A compiled `push_swap` binary in the directory you run the script from
