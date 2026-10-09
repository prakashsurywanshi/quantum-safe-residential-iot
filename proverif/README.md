# ProVerif formal proofs — Quantum-Resilient Residential IoT (QHSG)

This directory contains the formal verification suite that backs the security
claims of Suryawanshi, "A Sustainable Hybrid QKD–PQC Security Architecture for
Quantum-Resilient Residential IoT". All models are written in ProVerif's typed
applied-pi calculus and were verified with **ProVerif 2.05**.

## Scope

The proofs are *symbolic* (Dolev-Yao adversary): cryptographic primitives are
idealized exactly as used in the manuscript — AES-256-GCM is a perfect AEAD,
HKDF-SHA256 is a one-way pseudo-random extractor/expander, ML-KEM-768 is a
secure key-encapsulation mechanism, and QKD module outputs are idealized as
private key material. Under these standard assumptions, the invariants below
are machine-verified; the cycle-level and protocol-level evidence in
[`benchmarks/`](../benchmarks) and [`cooja/`](../cooja) complements these
symbolic results.

## Models and verified properties

| File | Manuscript basis | Property | ProVerif result |
|------|------------------|----------|-----------------|
| `qhsg_key_lifecycle.pv` | Eqs. 1–4 | Data-plane confidentiality (`attacker(secretPayload)`) | **true** |
| `qhsg_key_lifecycle.pv` | Eqs. 1–2 | QKD material `kq` unrecoverable | **true** |
| `qhsg_key_lifecycle.pv` | Eqs. 1–2 | ML-KEM agreement `kp` unrecoverable | **true** |
| `qhsg_key_lifecycle.pv` | §4.4 | Session origin authentication `event(endSession) ==> event(beginSession)` | **true** |
| `refresh_policy_stateless.pv` | Eq. 10 | Single-use nonce invariant `inj-event(nonceConsumed) ==> inj-event(nonceIssued)` — endpoint *without* Eq. 10 freshness state | **false** (replay attack found) |
| `refresh_policy_eq10.pv` | Eq. 10 | Same invariant — endpoint *with* Eq. 10 SeqNum binding | **true** |
| `endpoint_isolation.pv` | Eq. 3 | Lateral movement: compromise of device A's `KsA` does not disclose device B data `secretB` (context binding) | **true** |
| `forward_secrecy.pv` | Eqs. 1–2, 10 | Harvest-now-decrypt-later: past `secretData` stays confidential even when long-term QKD material `kq` is fully disclosed after the session | **true** |

## Replaying the proof

1. Obtain ProVerif 2.05 (https://bblanche.gitlabpages.inria.fr/proverif/).
   A prebuilt binary is *not* committed to this repository; for example, it can
   be built inside an ephemeral Ubuntu 24.04 container:
   ```
   docker run --rm -v /tmp/proverif:/p ubuntu:24.04 bash -lc \
     "apt-get update -qq && apt-get install -y -qq ocaml opam && \
      cd /tmp/proverif/proverif2.05 && ./build.native proverif >/dev/null 2>&1 || true"
   ```
2. Verify each model:
   ```
   proverif proverif/qhsg_key_lifecycle.pv
   proverif proverif/refresh_policy_stateless.pv
   proverif proverif/refresh_policy_eq10.pv
   proverif proverif/endpoint_isolation.pv
   proverif proverif/forward_secrecy.pv
   ```
   or run everything with `./proverif/run_all.sh /path/to/proverif`.

Verified outputs are captured verbatim in `results_*.txt`.

## The Eq. 10 replay attack (why the adaptive refresh is needed)

`refresh_policy_stateless.pv` models an endpoint that admits *any* valid ticket
(relying on the network's implicit timeliness). ProVerif derives a replay
attack in which a ticket `mk_ticket(endpKey, ctx)` issued for session `ctx` is
replayed against a second endpoint instance, so `nonceConsumed(ctx)` fires
twice against a single `nonceIssued(ctx)`:

```
goal reachable: @sid != @sid_1
   && b-inj-event(nonceIssued(ctx_1),@occ5_1)
   -> inj-event(nonceConsumed(ctx_1),@occ10_1)
      && inj-event(nonceConsumed(ctx_1),@occ10_2)
```

This is precisely the stale-session re-entry that the manuscript's adaptive
refresh policy (Eq. 10) is designed to close: the policy bounds session
lifetime by `min(V_max/R_data, T_base·(E_rem/E_initial)/(α·R_d+β·S_c))` and
rotates the session key before timeout. `refresh_policy_eq10.pv` binds every
admission ticket to a per-connection SeqNum challenge; the same query then
verifies (`true`), i.e. each nonce is consumed at most once.

## Assumptions and limitations

- Long-term material used by the gateway (`kq`, `kp` for lifecycle) is private;
  attacker controls all public channels.
- The stateful single-use register was also encoded with `table`/`lock`
  (GSVerif-style FIFO lock). Vanilla ProVerif reports that encoding as
  "cannot be proved" (a well-known over-approximation of its Horn-clause
  resolution for replicated state, cf. Cheval et al., CSF 2018); the
  challenge-bound encoding above is the one ProVerif can certify, and it is
  the SeqNum mechanism actually specified in Eq. 3/10.
- `putbegin`/phase-based "secrecy-after-event" forms are untyped-only in
  ProVerif; `forward_secrecy.pv` therefore models post-hoc compromise by
  fully disclosing `kq` in the same process, which is a strictly stronger
  adversary than harvest-now-decrypt-later.

## Files

- `*.pv` — formal models (types, constructors, processes, queries).
- `results_*.txt` — raw ProVerif output captured at verification time.
- `run_all.sh` — convenience driver printing the verification summaries.