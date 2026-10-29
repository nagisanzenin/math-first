# Structures: common problems and the math they already are

Most engineering problems have been named, studied and bounded. Name yours (question 2, Model) and the known result
comes with it (question 3, Bound). Check the result's hypotheses against your assumptions before you lean on it: a
cited theorem is **proved** only for the hypotheses it states.

## The map

| Problem | The object | Known result | Citation | The check in code |
|---|---|---|---|---|
| Assign tasks to workers at least cost | weighted bipartite matching | polynomial; Hungarian method, O(n³) versions are standard | Kuhn 1955; Munkres 1957 | differential test against brute force for n ≤ 8 |
| Match two sides that both have preferences | stable matching | always exists; Gale–Shapley finds the proposer-optimal one | Gale and Shapley 1962 | property: no blocking pair |
| Jobs on m machines | makespan scheduling | NP-hard; greedy ≤ (2 − 1/m)·OPT; LPT ≤ (4/3 − 1/(3m))·OPT | Graham 1966, 1969 | ratio to the lower bound max(total/m, longest job) |
| Cache eviction | online paging | LRU is k-competitive and no deterministic policy beats k; offline OPT evicts the farthest next use | Sleator and Tarjan 1985; Belady 1966 | replay a real trace against LRU, the candidate and OPT |
| Concurrency, latency, capacity | queue | `L = λW`; M/M/1 `W = 1/(μ − λ)`; Kingman for G/G/1 | Little 1961; Kingman 1961 | measure L, λ, W separately and check `L ≈ λW` |
| Rate limiting | token bucket, arrival curve | at most `b + r·t` admitted in any window of length t | Cruz 1991 | property: no window over `b + r·t` |
| Random IDs, content hashes | birthday problem | P(collision) ≈ `n²/2^(b+1)` | standard; e.g. Mitzenmacher and Upfal, *Probability and Computing* | compute it before choosing b |
| Membership with allowed errors | Bloom filter | FP ≈ `(1 − e^(−kn/m))^k`, best `k = (m/n)·ln 2`; floor `log2(1/ε)` bits per element | Bloom 1970; Carter et al. 1978 | count hits on keys known absent; `mf.py binom` |
| Spread keys over nodes | consistent hashing; balls into bins | about 1/N of keys move per node change; two choices cut max load to about `ln ln n / ln 2` | Karger et al. 1997; Azar et al. 1999 | count keys moved when a node is added |
| Rank items from pairwise results | Bradley–Terry model | MLE by MM; Elo is SGD on it; at least `log2(n!)` comparisons without noise | Bradley and Terry 1952; Hunter 2004 | simulate known strengths, measure recovery |
| Replicas that must agree | quorum systems, consensus | `R + W > N`; FLP impossibility; Byzantine needs `n ≥ 3f + 1` | Gifford 1979; Fischer, Lynch and Paterson 1985; Pease, Shostak and Lamport 1980 | exhaustive quorum check; model checking at R3 |
| Rollback, merge, state that only advances | lattice, join-semilattice, CRDT | a commutative, associative, idempotent merge of growing states converges | Shapiro et al. 2011 | property tests of the three laws and of monotonicity |
| A rate from few events | binomial, concentration | exact Clopper–Pearson; 0 in n gives about 3/n; Hoeffding | Clopper and Pearson 1934; Hanley and Lippman-Hand 1983; Hoeffding 1963 | coverage simulation; `mf.py binom`, `needed` |
| A/B tests, monitors, alarms | hypothesis tests, sequential tests | fixed n; group-sequential spending; anytime-valid sequences | Armitage et al. 1969; Pocock 1977; Lan and DeMets 1983; Howard et al. 2021 | null simulation through the real decision code |
| Parallel speedup, adding nodes | Amdahl, Gustafson, Universal Scalability Law | speedup ≤ `1/(1 − f)`; USL peaks at `N* = √((1 − σ)/κ)` | Amdahl 1967; Gustafson 1988; Gunther 2007 | fit on measured points, predict one more, measure it |
| Fan-out latency | order statistics | `P(at least one slow) = 1 − (1 − p)^n` | Dean and Barroso 2013 | measure the leaf tail and the fan-out p99 |
| Retries under failure | positive feedback | load can grow by `(r + 1)^d`; metastable failures | Metcalfe and Boggs 1976; Bronson et al. 2021 | inject errors, count attempts per request |
| Ordering events across machines | partial order, logical clocks | `a → b ⇒ C(a) < C(b)`; vector clocks capture concurrency exactly | Lamport 1978; Fidge 1988; Mattern 1989 | property: happens-before implies clock order |

## Scheduling and matching

- **Assignment.** n workers, n tasks, a cost matrix: weighted bipartite matching, solvable exactly by the Hungarian
  method (Kuhn 1955, Naval Research Logistics Quarterly; Munkres 1957, Journal of SIAM). Unweighted maximum matching:
  Hopcroft and Karp 1973 (SIAM Journal on Computing), O(E·√V). Do not ship a greedy and call it optimal.
- **Two-sided preferences** (mentors and mentees, reviewers and papers): a stable matching always exists and
  Gale–Shapley finds it (Gale and Shapley 1962, American Mathematical Monthly). It is optimal for the proposing side,
  and that side cannot gain by lying; the other side sometimes can (Roth 1982, Mathematics of Operations Research).
  Choose which side proposes on purpose.
- **Makespan on m machines** is NP-hard (Garey and Johnson, *Computers and Intractability*, 1979). Greedy list
  scheduling is within `2 − 1/m` of optimal (Graham 1966, Bell System Technical Journal); longest job first is within
  `4/3 − 1/(3m)` (Graham 1969, SIAM Journal on Applied Mathematics). At m = 4: 1.75 and 1.25.
- **A bound you can always compute:** `OPT ≥ max(total job time / m, longest job)`. Report your schedule's ratio to
  it. That ratio is a certificate even when OPT is unknown.

Check: brute force on small instances as the reference (differential test); for stable matching, an O(n²) scan for
blocking pairs; on real workloads, the ratio to the lower bound.

## Caching

- **Online paging** with a cache of k pages: LRU and FIFO are k-competitive, and no deterministic online policy does
  better than k in the worst case (Sleator and Tarjan 1985, Communications of the ACM). Randomized marking achieves
  `2·H_k` (Fiat et al. 1991, Journal of Algorithms).
- **Offline optimum:** evict the page whose next use is farthest away (Belady 1966, IBM Systems Journal). You cannot
  run it live. You can run it on a recorded trace, and there it is the ceiling on hit rate for that cache size.
- **Working set** (Denning 1968, Communications of the ACM): the pages used in the last τ references. When the
  working set outgrows the cache, the hit rate collapses; that is a threshold, not a slope (`lenses.md`, physics).

Worked example: a loop over 4 pages with a 3-page cache, 100 requests. LRU misses all 100; OPT misses 36 (simulated).
A cycle just larger than the cache is LRU's worst case. Real traces are rarely adversarial, so the competitive ratio
is a bound, not a prediction. Measure: replay a production trace through LRU, the candidate and Belady's OPT. The gap
to OPT is all the room there is (principle 4).

## Queues and rate limiting

- **Little's law** `L = λW` (Little 1961, Operations Research) holds for any stable system, any distribution, as a
  long-run average. 2,000 req/s at 150 ms mean latency means 300 requests in flight; a concurrency limit below 300
  will queue or reject.
- **M/M/1** (Poisson arrivals, exponential service, one server; Kleinrock, *Queueing Systems*, Vol. 1, 1975):
  mean time in system `W = 1/(μ − λ) = (1/μ)/(1 − ρ)`. With μ = 100/s: λ = 50 → 20 ms, 80 → 50 ms, 90 → 100 ms,
  99 → 1,000 ms. Going from 50 % to 99 % utilization multiplies latency by 50. That is the knee.
- **Kingman** for G/G/1 (Kingman 1961, Proceedings of the Cambridge Philosophical Society): mean wait in queue
  ≈ `(ρ/(1 − ρ))·((ca² + cs²)/2)·τ`, with ca and cs the coefficients of variation of inter-arrival and service time,
  τ the mean service time. At ρ = 0.8 with Poisson-like arrivals (ca² = 1): exponential service waits 4τ, constant
  service 2τ. Variability costs as much as utilization.
- **Token bucket** with rate r and burst b admits at most `b + r·t` in any window of length t: the (σ, ρ) arrival
  curve of network calculus (Cruz 1991, IEEE Transactions on Information Theory).

Pitfalls: averages hide the tail; M/M/1 assumes exponential service, so measure the coefficient of variation first; a
closed-loop load generator with fixed concurrency cannot push past saturation and hides the knee. Check: measure L,
λ and W independently and confirm `L ≈ λW` (if not, the instrumentation is wrong); a property test that random
arrival sequences never exceed `b + r·t` in any window; a load test at ρ = 0.5, 0.7, 0.8, 0.9 against the predicted
curve.

## Hashing, dedupe and Bloom filters

- **Birthday bound.** n random b-bit values collide with probability `1 − e^(−n(n−1)/2^(b+1))`, about `n²/2^(b+1)`
  when small. A billion 64-bit hashes: 2.7 %. To keep a billion random IDs below 10⁻⁶ you need b ≥ 79 (80 bits gives
  4.1·10⁻⁷). Dedupe by a 64-bit hash at that scale merges distinct items, silently.
- **Bloom filter** with m bits, k hashes, n elements (Bloom 1970, Communications of the ACM): false-positive rate
  ≈ `(1 − e^(−kn/m))^k`, minimized at `k = (m/n)·ln 2`, which needs `m/n = log2(1/ε)/ln 2 ≈ 1.44·log2(1/ε)` bits per
  element. The floor for any such structure is `log2(1/ε)` (`lenses.md`, information theory). The formula assumes
  independent uniform hashes and n at or below the design size; past it, the rate climbs fast. Bloom filters cannot
  delete; cuckoo filters can (Fan, Andersen, Kaminsky and Mitzenmacher 2014, CoNEXT).
- **Consistent hashing** (Karger et al. 1997, STOC): adding or removing one of N nodes moves about 1/N of the keys,
  where `hash mod N` moves nearly all of them. **Balls into bins:** n keys on n bins at random give a maximum load of
  about `ln n / ln ln n`; putting each key in the less loaded of two random bins drops it to about `ln ln n / ln 2`
  (Azar, Broder, Karlin and Upfal 1999, SIAM Journal on Computing).

Check: compute the collision probability before choosing b (one line); count false positives on keys known to be
absent and put an interval on it with `mf.py binom`; count the keys that move when one node is added (expect about
1/(N + 1)).

## Ranking from pairwise comparisons

- **Bradley–Terry** (Bradley and Terry 1952, Biometrika): `P(i beats j) = s_i/(s_i + s_j)`, a logistic in
  `θ_i − θ_j` with `θ = log s`. Fit by the MM algorithm (Hunter 2004, Annals of Statistics). The maximum-likelihood
  estimate exists only when the comparison graph is connected strongly enough; an item that won every game has
  infinite strength. Hunter 2004 states the condition.
- **Elo** (Elo, *The Rating of Chessplayers, Past and Present*, 1978) is one step of stochastic gradient ascent on
  the Bradley–Terry log-likelihood per game: `θ_i ← θ_i + K·(o − σ(θ_i − θ_j))`, up to Elo's base-10, 400-point
  scaling. The derivative of `log σ(θ_i − θ_j)` in `θ_i` is `1 − σ(θ_i − θ_j)`, which gives the update. So K is a
  learning rate: too large is noisy, too small lags.
- **Counting bound:** sorting without noise needs at least `log2(n!)` comparisons: 525 for n = 100, 8,530 for
  n = 1,000. Noisy comparisons need many more; spectral ranking has stated sample-complexity guarantees (Negahban, Oh
  and Shah 2017, Operations Research).

Check: simulate comparisons from known strengths through your ranking code and measure rank agreement (Kendall's τ)
at your real n; randomize presentation order so position bias cannot masquerade as strength.

## Consensus and quorums

- **Quorum intersection.** N replicas, writes to W, reads from R: every read sees the latest write when
  `R + W > N` (Gifford 1979, SOSP). N = 5: R = W = 3 works; R = 1 needs W = 5. Sloppy quorums give this up.
- **FLP.** No deterministic protocol guarantees consensus in an asynchronous system with even one crash (Fischer,
  Lynch and Paterson 1985, Journal of the ACM). Paxos (Lamport 1998, ACM Transactions on Computer Systems) and Raft
  (Ongaro and Ousterhout 2014, USENIX ATC) keep safety always and get liveness under partial synchrony (Dwork, Lynch
  and Stockmeyer 1988, Journal of the ACM).
- **CAP.** Under a partition, a service gives up consistency or availability (Brewer's conjecture, 2000; proved by
  Gilbert and Lynch 2002, SIGACT News).
- **Byzantine faults.** Tolerating f arbitrary faults needs `n ≥ 3f + 1` (Pease, Shostak and Lamport 1980, Journal
  of the ACM; Lamport, Shostak and Pease 1982, ACM TOPLAS). f = 1 needs 4 nodes, f = 2 needs 7.

Check: an exhaustive test that every read quorum meets every write quorum (2^N subsets, cheap up to N ≈ 20); a model
check of the protocol at small N (TLA+ or Quint; `rigor-ladder.md`, R3); fault injection with partitions and
clock skew.

## Rollback, merge, and pointers that only move forward

- **Join-semilattice:** a set with a merge `⊔` that is commutative, associative and idempotent. If every replica's
  state only grows in the order and merge is the join, replicas that saw the same updates converge, whatever the
  delivery order or duplication (Shapiro, Preguiça, Baquero and Zawirski 2011, SSS). Textbook: Davey and Priestley,
  *Introduction to Lattices and Order*, 2nd ed., Cambridge University Press, 2002.
- **Monotone pointer:** a last-known-good, a high-water mark, a version counter. The invariant is
  `p_{t+1} ⊒ p_t`: the pointer only moves forward. A design that keeps it: record a rollback as a new forward entry
  whose content equals an older state. The pointer stays monotone and the history stays append-only and auditable.
- **Idempotence:** `f(f(x)) = f(x)`. At-least-once delivery plus an idempotent apply gives the effect of
  exactly-once.

Check: property tests on random states for `merge(a, b) = merge(b, a)`, `merge(a, merge(b, c)) =
merge(merge(a, b), c)` and `merge(a, a) = a`; random operation sequences and interleavings never move the pointer
backward; replaying a log twice yields the same state.

## Estimation and confidence bounds

- **Exact binomial** (Clopper and Pearson 1934, Biometrika): invert the binomial tail; coverage is never below
  nominal. 6 events in 30 gives a one-sided 95 % upper bound of 35.7 % (`mf.py binom -k 6 -n 30`).
- **Rule of three:** 0 events in n gives a 95 % upper bound of about 3/n (Hanley and Lippman-Hand 1983, JAMA);
  exactly `1 − 0.05^(1/n)`, 0.99 % at n = 300. "No failures in 300 runs" means "below 1 %", not "never".
- **To certify a rate below X**, run `mf.py needed`: below 10 % at 95 % takes 29 trials with 0 events, 46 with 1.
- **Hoeffding** (Hoeffding 1963, Journal of the American Statistical Association): the mean of n independent values
  in [0, 1] is within ±ε with probability at least 1 − δ when `n ≥ ln(2/δ)/(2ε²)`; ±1 % at 95 % takes 18,445. It is
  distribution-free and so loose; variance-aware bounds (empirical Bernstein: Maurer and Pontil 2009, COLT) are
  tighter when the variance is small.

All of these assume independent trials. Sessions, users and machines cluster; clustered data has fewer effective
samples (`statistics.md`). Check: a coverage simulation over a grid of true rates, counting how often your interval
contains the truth.

## A/B and sequential testing

- **Fixed n:** decide n before the data (`mf.py samplesize`). 10 % against 12 % conversion, α = 0.05 two-sided,
  power 0.8: about 3,841 per group by the normal approximation.
- **Peeking:** testing at α = 0.05 after each of 5 equal batches and stopping at the first hit gives about 14 % false
  positives (Armitage, McPherson and Rowe 1969, Journal of the Royal Statistical Society A; our simulation: 14.2 %,
  200,000 runs).
- **Group-sequential:** plan K looks and spend α across them (Pocock 1977, Biometrika; O'Brien and Fleming 1979,
  Biometrics; spending functions: Lan and DeMets 1983, Biometrika).
- **Anytime-valid:** confidence sequences and e-values let you look after every observation and stop whenever
  (Howard, Ramdas, McAuliffe and Sekhon 2021, Annals of Statistics; Ramdas, Grünwald, Vovk and Shafer 2023,
  Statistical Science). The price is width at any fixed n. `mf.py cs-bernoulli`.
- **Many metrics:** Bonferroni or Holm (Holm 1979, Scandinavian Journal of Statistics; `mf.py multi`).

Detail and the traps: `statistics.md`. Check: an A/A run through the real decision code, counting false positives.

## Load and scale laws

- **Amdahl** (1967): with a parallel fraction f, speedup ≤ `1/(1 − f)`. At f = 0.95: 9.14× on 16 cores, 15.4× on
  64, never 20×.
- **Gustafson** (Gustafson 1988, Communications of the ACM): when the problem grows with the machine, scaled speedup
  is `N − (1 − f)(N − 1)`: 15.25 on 16 cores at 5 % serial. Know which question you are asking: a fixed problem, or
  a fixed time.
- **Universal Scalability Law** (Gunther, *Guerrilla Capacity Planning*, Springer, 2007):
  `X(N) = N / (1 + σ(N − 1) + κN(N − 1))` relative to one unit, σ for contention, κ for coherency cost. With κ > 0,
  throughput peaks at `N* = √((1 − σ)/κ)` and then falls. σ = 0.05, κ = 0.001: the peak is near N = 31 at 9.0×;
  64 nodes give 7.8×. Past the peak, more nodes make it slower.
- **Tail at scale** (Dean and Barroso 2013, Communications of the ACM): a request that fans out to n leaves waits
  for the slowest. If each leaf is slow with probability p, `P(at least one slow) = 1 − (1 − p)^n`: 63 % at p = 1 %,
  n = 100; 9.5 % at p = 0.1 %, n = 100. This assumes independent leaves. The same paper's fixes: hedged and tied
  requests.

Check: measure throughput at N = 1, 2, 4, 8, 16, fit σ and κ, predict a point the fit has not seen, and measure it.
Measure the leaf tail and compare the predicted fan-out p99 with the measured one.

## Retries and backoff

- **Amplification:** r retries at each of d layers can multiply load on the bottom layer by up to `(r + 1)^d`; 3
  retries over 3 layers is 64× during an outage. Retry at one layer, or cap retries as a fraction of requests (a
  retry budget) set from the headroom you measured.
- **Backoff:** binary exponential backoff comes from Ethernet (Metcalfe and Boggs 1976, Communications of the ACM).
  Without randomization, clients retry in synchronized waves; add jitter.
- **Positive feedback:** retries load an overloaded server, it fails more, clients retry more. The system can stay in
  that state after the trigger is gone: a metastable failure (Bronson, Aghayev, Charapko and Zhu 2021, HotOS; Huang
  et al. 2022, OSDI). In control terms (`lenses.md`), the loop gain is above 1.

Check: a load test with errors injected at the bottom layer, counting attempts per original request; then remove the
trigger and assert the system recovers within a stated time.

## Time and order

- **Happens-before** is a partial order (Lamport 1978, Communications of the ACM). Lamport clocks give
  `a → b ⇒ C(a) < C(b)`, not the converse. Vector clocks (Fidge 1988; Mattern 1989) give both directions:
  `a → b ⇔ V(a) < V(b)`, and incomparable vectors mean concurrent events.
- **Wall clocks are not an order.** Clocks skew, so "last write wins" by timestamp drops writes without a trace.
  Hybrid logical clocks combine physical time with Lamport's rule (Kulkarni, Demirbas, Madappa, Avva and Leone 2014,
  OPODIS).

Check: a property test over random message histories: if `a → b` then `C(a) < C(b)` and `V(a) < V(b)`, and
concurrent events get incomparable vectors.

## Adding a structure

A new structure gets a row in the map with its citation and its check. Add a detail section only when it has a
pitfall worth a paragraph. A structure without a check in code is a reading tip, not part of the spec.
