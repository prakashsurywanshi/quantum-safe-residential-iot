# ProVerif results table — QHSG formal verification

Raw, machine-produced results for every query in the QHSG ProVerif suite.
Each row is backed verbatim by the corresponding `results_*.txt` transcript in
this directory (produced by `./run_all.sh /tmp/proverif/bin/proverif`).

- **Tool:** ProVerif 2.05, typed applied-pi calculus.
- **Adversary:** Dolev–Yao, controls the public channel `c` (eavesdrop, drop,
  delay, reorder, duplicate, replay, inject).
- **Command (one model):** `/tmp/proverif/bin/proverif proverif/<model>.pv`
- **Command (all models):** `bash proverif/run_all.sh /tmp/proverif/bin/proverif`

Legend: **true** = property holds (no attack); **false** = property violated
(attack trace produced); **unknown** = not decided.

## New models added in this revision

| # | Model file | Manuscript basis | Query (as printed) | Result | Transcript | Interpretation |
|---|------------|------------------|--------------------|--------|-----------|----------------|
| 1 | `gateway_compromise_fs.pv` | Eqs. 1–2, 4 | `not attacker(secretPayload[])` | **true** | `results_gateway_fs.txt` | Past data-plane payloads stay secret even after the long-term gateway master secrets `kmS` and `kq` are fully disclosed. |
| 2 | `gateway_compromise_fs.pv` | Eqs. 1–2 | `not attacker(keyChallenge[])` | **true** | `results_gateway_fs.txt` | Past session keys `Ks` (probed via a fresh plaintext under `Ks`) stay secret under the same post-hoc gateway compromise. |
| 3 | `key_independence.pv` | Eqs. 2–3 | `not attacker(dataA2[])` | **true** | `results_key_independence.txt` | Cross-session: disclosure of session key `KsA1` does not reveal the next session's data on the same device. |
| 4 | `key_independence.pv` | Eqs. 2–3 | `not attacker(dataB1[])` | **true** | `results_key_independence.txt` | Cross-device: disclosure of `KsA1` does not reveal device B's data. |
| 5 | `key_independence.pv` | Eqs. 2–3 | `not attacker(probeA2[])` | **true** | `results_key_independence.txt` | Session key `KsA2` (same device, different SeqNum) remains secret given `KsA1`. |
| 6 | `key_independence.pv` | Eqs. 2–3 | `not attacker(probeB1[])` | **true** | `results_key_independence.txt` | Session key `KsB1` (different device) remains secret given `KsA1`. |
| 7 | `key_independence.pv` | Eq. 1 | `not attacker(kmS[])` / `not attacker(kq[])` | **true** | `results_key_independence.txt` | Long-term root material is never exposed in this scenario. |
| 8 | `replay_packetloss_bound.pv` | Eq. 3, 10 | `inj-event(ticketConsumed(x)) ==> inj-event(ticketIssued(x))` | **true** | `results_replay_bound.txt` | With SeqNum challenge binding, each issued context is consumed at most once under arbitrary loss/delay/reorder/replay. |
| 9 | `replay_packetloss_bound.pv` | Eq. 3 | `not attacker(endpKey[])` | **true** | `results_replay_bound.txt` | The ticket key stays private. |
| 10 | `replay_packetloss_stateless.pv` | Eq. 3, 10 | `inj-event(ticketConsumed(x)) ==> inj-event(ticketIssued(x))` | **false** | `results_replay_stateless.txt` | Stateless endpoint: a captured/delayed ticket is replayed and one issued context is consumed twice (stale-session re-entry). |
| 11 | `replay_packetloss_stateless.pv` | Eq. 3 | `not attacker(endpKey[])` | **true** | `results_replay_stateless.txt` | The ticket key stays private; the failure is freshness, not key secrecy. |
| 12 | `replay_reorder_window.pv` | Eq. 3 | `inj-event(ticketConsumed(x)) ==> inj-event(ticketIssued(x))` | **true** | `results_replay_reorder.txt` | Strict monotone sequence window: an old `seqOne` ticket reordered into the `seqTwo` slot is rejected; no double-consumption. |
| 13 | `replay_reorder_window.pv` | Eq. 3 | `not attacker(endpKey[])` | **true** | `results_replay_reorder.txt` | The ticket key stays private. |
| 14 | `impersonation_auth.pv` | Eqs. 3–4 | `event(endSession(x)) ==> event(beginSession(x))` | **true** | `results_impersonation_auth.txt` | Authenticated endpoint: forged tickets `mk_ticket(attackerKey,·)` are rejected; every accepted session originated at the gateway. |
| 15 | `impersonation_auth.pv` | Eq. 4 | `not attacker(secretPayload[])` | **true** | `results_impersonation_auth.txt` | Active injection cannot decrypt the data plane. |
| 16 | `impersonation_auth.pv` | Eq. 3 | `not attacker(endpKey[])` | **true** | `results_impersonation_auth.txt` | The authenticating ticket key stays private. |
| 17 | `impersonation_noauth.pv` | Eqs. 3–4 | `event(endSession(x)) ==> event(beginSession(x))` | **false** | `results_impersonation_noauth.txt` | Unauthenticated endpoint: the adversary forges `mk_ticket(forgedCtx)` and impersonates the gateway on the local link. |
| 18 | `impersonation_noauth.pv` | Eq. 3 | `not attacker(endpKey[])` | **true** | `results_impersonation_noauth.txt` | The key itself stays private; the failure is the missing authentication check. |

## Pre-existing models (re-run for reproducibility)

| # | Model file | Manuscript basis | Query (as printed) | Result | Transcript |
|---|------------|------------------|--------------------|--------|-----------|
| A1 | `qhsg_key_lifecycle.pv` | Eqs. 1–4 | `not attacker(secretPayload[])` | **true** | `results_lifecycle.txt` |
| A2 | `qhsg_key_lifecycle.pv` | Eqs. 1–2 | `not attacker(kq[])` | **true** | `results_lifecycle.txt` |
| A3 | `qhsg_key_lifecycle.pv` | Eqs. 1–2 | `not attacker(kp[])` | **true** | `results_lifecycle.txt` |
| A4 | `qhsg_key_lifecycle.pv` | §4.4 | `event(endSession(s)) ==> event(beginSession(s))` | **true** | `results_lifecycle.txt` |
| A5 | `refresh_policy_stateless.pv` | Eq. 10 | `inj-event(nonceConsumed(s)) ==> inj-event(nonceIssued(s))` | **false** | `results_stateless.txt` |
| A6 | `refresh_policy_stateless.pv` | Eqs. 1–2 | `not attacker(kq[])` / `not attacker(kp[])` / `not attacker(endpKey[])` | **true** | `results_stateless.txt` |
| A7 | `refresh_policy_eq10.pv` | Eq. 10 | `inj-event(nonceConsumed(s)) ==> inj-event(nonceIssued(s))` | **true** | `results_eq10.txt` |
| A8 | `refresh_policy_eq10.pv` | Eqs. 1–2 | `not attacker(kq[])` / `not attacker(kp[])` / `not attacker(endpKey[])` | **true** | `results_eq10.txt` |
| A9 | `endpoint_isolation.pv` | Eq. 3 | `not attacker(secretB[])` | **true** | `results_isolation.txt` |
| A10 | `endpoint_isolation.pv` | Eqs. 1–2 | `not attacker(kq[])` / `not attacker(kp[])` | **true** | `results_isolation.txt` |
| A11 | `forward_secrecy.pv` | Eqs. 1–2, 10 | `not attacker(secretData[])` | **true** | `results_forward.txt` |

## Notes on the two "false" results

- **#10 `replay_packetloss_stateless`** — expected negative control. ProVerif
  prints `goal reachable: ... inj-event(ticketConsumed(ctx_1),@occ8_1) &&
  inj-event(ticketConsumed(ctx_1),@occ8_2)` against a single
  `ticketIssued(ctx_1)`. This is the stale-session replay that the Eq. 3/10
  SeqNum binding (model #8/#12) removes.
- **#17 `impersonation_noauth`** — expected negative control. ProVerif prints
  the trace `out(c, ~M) with ~M = mk_ticket(forgedCtx)` → `in(c, mk_ticket(a))`
  → `event endSession(a)` with no matching `beginSession`. This is the active
  local-link impersonation that the `endpKey` ticket authentication
  (model #14) removes.

No query returned **unknown**.
