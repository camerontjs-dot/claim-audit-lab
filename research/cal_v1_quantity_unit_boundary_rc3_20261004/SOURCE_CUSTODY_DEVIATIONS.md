# RC3 source-custody deviations

## First publication attempt

All eight preselected sources were fetched exactly once and frozen before semantic implementation.

The first Git commit attempt failed because repository whitespace hygiene treated verbatim HTTP headers and textual HTML wire bytes as source code and reported trailing whitespace/CRLF. No fetched source byte was edited.

Successor publication handling:
- exact raw response bodies remain byte-identical to their recorded SHA-256 values;
- raw source .bin files are marked binary for Git diff purposes only;
- raw response headers and curl stdout/stderr receipts remain local and are excluded from Git because some responses contain ephemeral Set-Cookie values not required for the scientific source identity;
- all required custody facts are retained in SOURCE_FREEZE.json;
- no source was re-fetched or replaced.

This is a publication/apparatus deviation, not a semantic result.
