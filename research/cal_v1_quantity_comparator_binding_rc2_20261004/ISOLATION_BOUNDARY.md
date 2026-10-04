# Source custody and isolation boundary

This note records the checks around the generated `SOURCE_FREEZE.json`. It does not alter published source bytes. `SOURCE_FREEZE.json` is the unmodified `fetch_sources.py` output.

## Retrieval

Each URL in `SOURCE_POOL_SELECTION.json` was retrieved once. The transport command, user-agent, UTC time, status, media type, byte count, and SHA-256 are in `SOURCE_FREEZE.json`. There was no second fetch and no fallback.

Published SHA-256 equals original SHA-256 for every source. `redaction_deviations` is empty. The leak scan found no secret class and no machine user-home path in the published bytes or the freeze receipt.

## Failures preserved

- QRC2-C03: HTTP 403, 1325 bytes. A calibration title check read the page title as "Access Denied". The source was not replaced.
- QRC2-H03: HTTP 403, 1325 bytes. The held-out body was not opened. The source was not replaced.

## Calibration title check

Calibration bodies were opened only far enough to read the HTML title and, for QRC2-C04, the charset declaration.

- QRC2-C01 title matches the selected BEA release.
- QRC2-C02 title matches the selected EIA press release.
- QRC2-C04 title matches the selected Fast Facts page. The wire bytes are not valid UTF-8. The first invalid start byte is at offset 7008. The document declares ISO-8859-1. Published bytes are the unmodified wire bytes. There was no transcoding.

## Held-out bodies

QRC2-H01, QRC2-H02, QRC2-H03, and QRC2-H04 bodies were not opened. The custody checks for those rows are HTTP status, final host equal to the requested host, byte count, and SHA-256. Whether the three HTTP 200 bodies are the selected articles remains unverified until the held-out reveal.

## Unpublished local copies

Response headers and the `sources/original-local/` byte copies stay untracked. Headers can carry cookies or session material. No redaction was applied, so those local copies are duplicates of the published bytes. They are not a hidden pre-redaction identity.

## Isolation boundary

The boundary is procedural.

- There is no separate operating-system user.
- There is no cryptographic seal.
- After this commit, the held-out blobs are reachable from the git object store.
- The candidate implementer uses a separate worktree created from this source-freeze commit.
- That worktree uses sparse checkout so `sources/raw/QRC2-H01.bin`, `QRC2-H02.bin`, `QRC2-H03.bin`, and `QRC2-H04.bin` are absent from the working tree.
- Sparse checkout can be disabled by the same agent. It is not access control.
- The implementer is instructed not to read those raw bins, the matching `sources/original-local/` copies, or later held-out claim and label files, until the comparator candidate, the other judge bytes, the evaluator, and the synthesis policy are frozen.

## Contamination already true

`SOURCE_POOL_SELECTION.json` and `SOURCE_FREEZE.json` name the held-out publishers, titles, and URLs. The custodian read those records. The custodian did not read held-out page bodies. That is identity contamination.

The preparation publication-byte mismatch at `33cc37b1660441344e13152b202d53ec987f0fec`, run `37227438104`, remains a failed preparation. This commit does not reinterpret it.

## Ordering

Comparator judge code is unchanged in this commit.
