# Data management plan

## Data classes

| Class | Examples | Access | Release rule |
|---|---|---|---|
| Raw public source | Four XLSX files and two D4 DOCX files | Named project team | Cite/link repository; do not create new row-level redistribution without review. |
| Aggregate derived | Profiles, scenario tables, logic decisions | Project team; publishable after review | May be released with interpretation limits. |
| Source code/config | Python, ASP, JSON, tests | Project team; intended public | Review for secrets and absolute paths. |
| Human-study data | Future expert or CAP-Data responses | Approved study personnel only | Governed by prospective protocol and consent. |
| Administrative | IRB letters, consent logs, compensation records | PI/authorized staff | Never store in the public repository. |

## Storage and access

- Store the working project in institutionally approved storage with account
  authentication and version history.
- Keep an explicit list of people with write access.
- Make raw files available offline before running; avoid partial cloud placeholders.
- Do not store passwords, API tokens, participant contact details, or signed
  consent forms in this repository.

## Integrity and versioning

- Verify raw-file hashes before a publication freeze.
- A legitimate source update receives a new manifest row/version and is never
  silently substituted.
- Record configuration and result hashes for each manuscript submission.
- Tag generated outputs with the same project version as the manuscript.

## Minimization

Only fields required by a documented research question should enter an analysis.
Free text and direct identifiers are excluded from generated documentation
contents. Future human studies should avoid collecting names, emails, or precise
location unless separately justified and approved.

## Retention

Raw public deposits may be retained while the project is active and the licence
permits. Aggregate outputs and code should follow institutional research-record
policy. Future human-study retention periods must be stated in the IRB materials
and consent. At project close, the data steward records what was archived,
deleted, or returned and the authority for that action.

## Sharing

Preferred public package:

- code, tests, ASP rules, configs, documentation, aggregate tables, and synthetic
  fixtures;
- DOI links instead of duplicating raw source files when practical; and
- no free text, record examples, identity keys, or human-study administrative files.

Before release, run a secret scan, path scan, licence review, documentation
coverage check, checksum verification, and an independent privacy review.

## Incident response

If sensitive material is exposed or an unauthorized identity linkage occurs:

1. stop sharing and preserve an incident log;
2. notify the PI and institutional privacy/data office;
3. identify affected files, users, and time window;
4. revoke access or links under institutional direction;
5. document remediation without copying sensitive content into public issues; and
6. resume only after authorization.

