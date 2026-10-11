# Post-mortem: Celestia liveness incidents (September–October 2026)

**Operator:** Winter Validator (`winter_validator` on Discord · https://validators.win)
**Published:** 2026-10-11 · **Status:** all incidents resolved, validators active

We publish post-mortems for every jailing event, on any network, testnet included. Between September and October 2026 our Celestia validators were jailed **three times — all liveness faults, zero TIA slashed in any of them** (every log line below shows `slashed=0.000000000000000000`).

## Summary

| # | Network | Jailed | Un-jailed | Root cause | Slashed |
|---|---------|--------|-----------|------------|---------|
| 1 | Mocha-5 (testnet) | ~Sep 21–22, 2026 | Sep 22, 2026 (auto) | Missed-block accumulation during the September storage-pressure period (bridge node sharing the validator host, disk up to 91%) | 0 TIA |
| 2 | Mocha-5 (testnet) | Sep 28, 2026 06:41 local (h=1200289) | Sep 29, 2026 18:29 local | Validator offline during hosting migration (server rebuilt Sep 26–28) | 0 TIA |
| 3 | Celestia mainnet | Oct 2, 2026 (node frozen; sentence ended 2026-10-02 09:51 UTC) | Oct 5, 2026 13:23 local | Node frozen by an app-db corruption crash-loop (`version does not exist` panic) for ~3 days | 0 TIA |

## Incident 1 — Mocha-5, jailed ~Sep 21–22, 2026

**Context.** Through mid-September our Mocha validator shared its host with a Celestia bridge node. The bridge's DAS storage grew faster than anticipated (up to +18 GB/11 h during catch-up) and drove the shared volume to 91% on Sep 16. The validator stayed up but missed-block accumulation ran well above baseline during this storage-pressure period.

**Jail.** A liveness jail with sentence ending Sep 22, 2026. The exact jail log line predates the current retained log window on the (since-rebuilt) host; timeline and context above are from operator runbooks and daily health records.

**Remediation (started here, completed over the following weeks).**
- Storage on the validator host doubled (100 GB → 200 GB; the volume later sat at 4–9% usage).
- Automated block-store cleanup + disk alerts at 85%.
- Decision made to separate the bridge workload from the validator host permanently.

## Incident 2 — Mocha-5, jailed Sep 28, 2026

**Root cause.** The Mocha host was migrated/rebuilt at the hosting provider on Sep 26. The validator came back online but had missed blocks during the migration window; the chain jailed it for liveness.

Evidence (validator consensus address `celestiavalcons1cysh…v3d0`):

```
Sep 28 06:41 INF slashing and jailing validator due to liveness fault height=1200289
             jailed_until=2026-09-28T17:48:55Z slashed=0.000000000000000000
             threshold=10 validator=celestiavalcons1cyshvrk2hy8ty3lwe93tzaxhky3nvgdrf0v3d0
Sep 29 18:29 INF validator un-jailed module=x/staking
             validator=celestiavalcons1cyshvrk2hy8ty3lwe93tzaxhky3nvgdrf0v3d0
```

**Remediation.** Migration runbook written (pre-check missed-block counter, plan unjail tx immediately after sentence expiry — the Sep 29 unjail was delayed ~18 h because nobody was paged; that is now an alerting rule, not a human memory).

## Incident 3 — Celestia mainnet, jailed Oct 2 → un-jailed Oct 5, 2026

**Root cause.** On Oct 2 the mainnet node (active-set validator, vp=163) froze: the app crashed in a loop with a `version does not exist` panic from a corrupted app-db, height pinned at 14,572,324 while the chain advanced ~90k blocks. The liveness jail triggered with sentence ending 2026-10-02T09:51Z — but the node was still down, so nothing self-recovered.

On-chain signing info (queried Oct 11, 2026):

```
address: celestiavalcons16a6xqm4pcfkg696xcgvua25n0wrsqrrcrusuah
jailed_until: 2026-10-02T09:51:07Z
```

**Recovery.** Data directory rebuilt (operator worked with the hosting admin), node re-synced, `unjail` broadcast Oct 5 13:23 local time:

```
Oct 05 13:23:54 INF validator un-jailed module=x/staking
              validator=celestiavalcons16a6xqm4pcfkg696xcgvua25n0wrsqrrcrusuah
```

The validator rejoined the active set the same day and has been signing continuously since (vp=163, verified Oct 11, 2026).

**Remediation.**
- Hardware upgraded for headroom: 32-core / 64 GB RAM / 400 GB NVMe (RAM raised 23→64 GB on Oct 11, 2026).
- New alerting on node stall (frozen height), crash-loop restart count, catch-up state and disk — a frozen node now pages us within minutes, not days.
- Post-restart checklist includes signing-info verification so a jail never sits unnoticed again.

## What all three incidents have in common — and what changed

All three were **liveness faults, none involved double-signing, and none resulted in any slashing**. Two of the three were amplified by late detection rather than by the original fault. The permanent changes:

- **Workload separation:** no bridge/DAS workload on validator hosts anymore (final bridge decommission Oct 11, 2026).
- **Storage headroom + automated cleanup** on every node.
- **Self-hosted Prometheus/Grafana monitoring** with alerts for: node down, stalled height, crash-looping, catch-up, low peers, disk >85%, RAM >90% → Discord + phone; plus daily automated health reports.
- **Runbooks** for migrations, unjail and data-rebuild scenarios.

## Verify on-chain

- Mainnet validator (active set): [Mintscan — celestiavaloper1kdmt8y05xkmqafxjez9qlfljetcatxhse7nh79](https://www.mintscan.io/celestia/validators/celestiavaloper1kdmt8y05xkmqafxjez9qlfljetcatxhse7nh79)
- Mocha-5 validator (active set): [Mintscan testnet — celestiavaloper1s8zqq57a9gqgxfj5huqqvmp8674837dzhw3620](https://www.mintscan.io/celestia-testnet/validators/celestiavaloper1s8zqq57a9gqgxfj5huqqvmp8674837dzhw3620)

— Winter Validator, Oct 11, 2026. Questions: `winter_validator` on Discord.
