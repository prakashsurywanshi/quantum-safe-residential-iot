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
| `gateway_compromise_fs.pv` | Eqs. 1–2, 4 | Gateway forward secrecy: after post-hoc disclosure of the long-term gateway master secrets `kmS` **and** `kq`, past payloads (`secretPayload`) and past session keys (`keyChallenge`) stay secret | **true** |
| `key_independence.pv` | Eqs. 2–3 | Cross-session / cross-device key independence: full disclosure of session key `KsA1` does not disclose `KsA2` (same device) or `KsB1` (other device), nor their data | **true** |
| `replay_packetloss_bound.pv` | Eqs. 3, 10 | Ticket replay under loss/delay/reorder with SeqNum challenge binding: `inj-event(ticketConsumed) ==> inj-event(ticketIssued)` | **true** |
| `replay_packetloss_stateless.pv` | Eq. 10 | Same invariant, stateless endpoint: replay of a delayed ticket consumes one context twice | **false** (replay found) |
| `replay_reorder_window.pv` | Eq. 3 | Strict monotone sequence window: a reordered old `seqOne` ticket is rejected in the `seqTwo` slot | **true** |
| `impersonation_auth.pv` | Eqs. 3–4 | Active local-link impersonation: `event(endSession) ==> event(beginSession)` for the authenticated endpoint; forged tickets under `attackerKey` are rejected | **true** |
| `impersonation_noauth.pv` | Eqs. 3–4 | Same query for an unauthenticated endpoint: a forged `mk_ticket(forgedCtx)` is accepted | **false** (impersonation found) |

A per-query breakdown with interpretations is in [`results_table.md`](results_table.md).

## Replaying the proof

1. Obtain ProVerif 2.05 (https://bblanche.gitlabpages.inria.fr/proverif/).
   A prebuilt binary is *not* committed to this repository. The suite was
   verified with a native binary built from the source package; it needs only
   the OCaml compiler (no ocamlfind/lablgtk):
   ```
   mkdir -p /tmp/proverif && cd /tmp/proverif
   curl -O https://bblanche.gitlabpages.inria.fr/proverif/proverif2.05.tar.gz
   tar xzf proverif2.05.tar.gz
   docker run --rm -v /tmp/proverif:/p ubuntu:24.04 bash -lc \
     "apt-get update -qq && apt-get install -y -qq ocaml && \
      cd /p/proverif2.05 && ./build -nointeract native && \
      mkdir -p /p/bin && install -m755 proverif /p/bin/proverif"
   ```
2. Verify each model (or run everything with
   `./proverif/run_all.sh /path/to/proverif`, which runs all 12 models and
   refreshes the raw transcripts):
   ```
   proverif proverif/qhsg_key_lifecycle.pv
   proverif proverif/refresh_policy_stateless.pv
   proverif proverif/refresh_policy_eq10.pv
   proverif proverif/endpoint_isolation.pv
   proverif proverif/forward_secrecy.pv
   proverif proverif/gateway_compromise_fs.pv
   proverif proverif/key_independence.pv
   proverif proverif/replay_packetloss_bound.pv
   proverif proverif/replay_packetloss_stateless.pv
   proverif proverif/replay_reorder_window.pv
   proverif proverif/impersonation_auth.pv
   proverif proverif/impersonation_noauth.pv
   ```

Verified outputs are captured verbatim in `results_*.txt`; see
[`results_table.md`](results_table.md) for the per-query result table.

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

## Extended evidence (this revision)

The pre-existing suite is complemented by seven new models covering gateway
compromise, key independence, replay under packet loss, and active local-link
impersonation. All are run by `run_all.sh` and tabulated in `results_table.md`.

### Gateway compromise and forward secrecy (`gateway_compromise_fs.pv`)

Each session mixes the long-term gateway secrets `kmS` (HSM-resident master),
`kq` (QKD root) with a **one-time** ML-KEM agreement `kp`
(`PRK = HKDF-Extract(HKDF-Extract(kmS,kq), kp)`, Eqs. 1–2). The model discloses
`kmS` and `kq` outright, concurrently with the sessions (a strictly stronger
adversary than "later disclosure"). ProVerif proves
`not attacker(secretPayload)` **true** and `not attacker(keyChallenge)` **true**:
past data and past session keys stay confidential because `kp` is never stored.
The live-session half of gateway compromise (the current `kp` resident in RAM
during an active session) remains the acknowledged single-point-of-failure
limitation in the manuscript.

### Cross-session / cross-device key independence (`key_independence.pv`)

With one session key `KsA1` fully disclosed, ProVerif proves the next session
on the same device (`KsA2`), a session on another device (`KsB1`), and their
data-plane payloads all remain secret (**true**). Key secrecy is certified by a
fresh probe plaintext carried under each key: by perfect-AEAD soundness,
recovering the probe is equivalent to recovering the key. Independence follows
from one-way HKDF expansion on the distinct public context strings `C`
(Eq. 3).

### Ticket replay under packet loss / delay / reordering

`replay_packetloss_bound.pv` runs the endpoint in a retry loop carrying a fresh
SeqNum challenge `z` per attempt, with the gateway issuing tickets bound to `z`.
Over the lossy, reordering Dolev–Yao link the invariant
`inj-event(ticketConsumed) ==> inj-event(ticketIssued)` is **true**: a stale
ticket carries the wrong `z` and is rejected. Its negative control
`replay_packetloss_stateless.pv` (no SeqNum state) is **false**, with ProVerif
exhibiting two `ticketConsumed` events for one `ticketIssued`.
`replay_reorder_window.pv` additionally models a strict monotone
`seqOne -> seqTwo` window and proves that an old `seqOne` ticket reordered into
the `seqTwo` slot is rejected (**true**).

### Active impersonation on the local link

`impersonation_auth.pv` authenticates admissions by opening the ticket with the
pre-shared private key `endpKey`; forged tickets `mk_ticket(attackerKey, …)`
and forged data `aead_enc(attackerKey, …)` are rejected, so
`event(endSession) ==> event(beginSession)` is **true** and the data plane stays
confidential. Its negative control `impersonation_noauth.pv` uses a public,
unauthenticated ticket format; the adversary forges `mk_ticket(forgedCtx)` and
the correspondence is **false**, demonstrating the impersonation the
authentication closes.

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
- `gateway_compromise_fs.pv` likewise discloses the long-term gateway secrets
  `kmS` and `kq` concurrently with the sessions. Compromise of the *live*
  session ephemeral `kp` (active memory) is out of scope, consistent with the
  manuscript's stated single-point-of-failure limitation.
- Key secrecy in `key_independence.pv` is certified through a fresh probe
  plaintext encrypted under the key (perfect-AEAD / IND-CPA proxy); this is
  equivalent, in the symbolic model, to the adversary deriving the key.
- `replay_reorder_window.pv` is a bounded two-slot window; the general
  unbounded result is given by `replay_packetloss_bound.pv`.

## Files

- `*.pv` — formal models (types, constructors, processes, queries).
- `results_*.txt` — raw ProVerif output captured at verification time.
- `results_table.md` — every query, model file, verified result, and interpretation.
- `run_all.sh` — convenience driver that runs all 12 models, refreshes the raw
  transcripts, and prints the verification summaries.