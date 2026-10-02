# God Code Benchmark Results

Recorded by running the documented method on this machine:

```bash
python3 bench/bench.py
```

Date: 2026-10-02. Commit: `ac55ae9` (main). Machine: AMD EPYC 9D25
126-Core Processor. Python 3.12.3 on
Linux-7.0.0-39-generic-x86_64-with-glibc2.39.

Mode: full. Seed 20260925. 2 warmup + 5 timed runs per benchmark.
The reported number is the median of the timed runs.

```
benchmark | median_ms | min_ms | max_ms | runs | detail
lex_parse | 226.4 | 213.0 | 228.6 | 5 | 8284 lines, 319.5 KB generated scroll
fib_recursion | 864.8 | 840.8 | 976.6 | 5 | fib(22) by naive double recursion
while_loop | 140.1 | 139.3 | 161.2 | 5 | counting loop of 20000 iterations
string_interp | 28.5 | 27.7 | 28.6 | 5 | 2000 REVEALs with breathed-in expressions
list_ops | 88.3 | 88.0 | 90.5 | 5 | PUSH 5000 items, then FOR-sum them
json_stdlib | 113.7 | 113.1 | 114.1 | 5 | 50 JSON_ENCODE/JSON_DECODE round trips through the registry json-tools scroll
anchor_chain | 8.2 | 7.9 | 9.6 | 5 | 50 ANCHOR seals on a fresh simulated chain
```

Reading the numbers: the tree-walking interpreter executes roughly
143k simple loop iterations per second (`while_loop`), interpolates
about 70k strings per second, and lexes/parses about 1.4 MB of God Code
per second. `fib(22)` is the heaviest workload at 0.86 s, dominated by
rite call overhead. `ANCHOR` sealing is cheap per seal (about 0.16 ms)
on the local simulated chain.

These numbers replace the first recording from 2026-09-25, which was
taken on a feature branch before the isiZulu tongue, the commons
builtins, and a week of further engine work. Rerun on the same machine
to compare: medians land within a few percent run to run. Numbers from
other machines are not directly comparable; see `bench/README.md` for
the method and the machine info captured with each run (`--json`
output).
