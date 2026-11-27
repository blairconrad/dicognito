# 2. Version releases by the effort of upgrading (EffVer), with an output-stability policy

Status: Accepted (decided 2026-11-23)

Date: 2026-11-27

## Context

dicognito has three contracts with its users:

| Contract | Who depends on it | What a change looks like |
|---|---|---|
| Python API | Code that builds an `Anonymizer`, adds element handlers or subclasses `ElementAnonymizer` | Renamed or removed classes and methods, changed handler order |
| Command line | Scripts and pipelines that call `dicognito` | Renamed or removed options, changed defaults, changed exit codes |
| Output | Everyone who keeps, compares or links anonymized data | A different value written for the same input, seed and options |

Semantic Versioning was designed around the first two. The third matters most to users, and its changes do not fit "bug fix, feature, breaking change". Newly anonymizing an attribute that used to pass through is a privacy fix for one user and a breaking change for another who routes on that value. The release notes already show this: similar output changes have been listed under New, Fixed and Changed.

The cost of an output change depends on who is upgrading. Someone who builds test data incrementally, anonymizing new batches with a fixed seed and adding them to data already in a PACS, is hurt most when identifiers, UIDs, patient names or dates change: the new batch no longer links to the old one, and the only remedy is to re-anonymize everything. Someone who anonymizes once for a trial or a share is not affected, and wants privacy improvements as early as possible. No version number can describe both.

## Options considered

1. **Semantic Versioning with a declared output contract.** Familiar, and tools such as Dependabot and Renovate assume it. It only works once the output contract is written down, and the contract then decides every hard case. Either privacy improvements wait for a major release, or the contract carves them out and minor releases stop being safe to take. Strictly applied, it produces frequent major releases while coverage grows, which weakens the signal a major release is meant to send.
2. **Intended Effort Versioning (EffVer), Macro.Meso.Micro.** The same three numbers, bumped by the effort an existing user is expected to spend to adopt the release. It asks the question that matters for anonymized output, "what must I do to upgrade?", instead of one that has no good answer, "is a newly pseudonymized attribute a fix or a feature?". Meso releases are cheap, so privacy improvements can ship promptly. The format is identical to SemVer, so it can be reversed later by changing only how the next number is chosen. Less widely known, and effort is a judgement, so the policy has to be written down.
The Black formatter faces the same problem, since its output is its contract. It uses calendar versions and a stability policy: output changes only in the first release of a year, upcoming changes are available earlier behind a preview flag, and crash fixes are unrestricted. Neither of the two schemes above copies that, but the lessons apply to both: write the output policy down, batch output changes, and treat input that previously failed as free to change.

## Decision

Use EffVer, with a written output-stability policy. The first release under it is 0.20.0. While dicognito is below 1.0, versions read as `0.Macro.Micro`, so a change that would be meso also bumps the middle number until 1.0.

For a given input, seed and set of options, and a pydicom version within the supported range:

- **Micro** releases do not change output, except for input that previously failed to anonymize. They may add support for newer Python or pydicom versions.
- **Meso** releases may modify attributes that were previously passed through, change the values generated for attributes that are not used to link objects, and drop support for old Python or pydicom versions. They do not change identifiers, UIDs, patient names or dates.
- **Macro** releases may change any output, including the values that link objects across runs. The whole-day date shift of ADR-0001 is an example.

The policy protects the user who builds test data incrementally: linking values change only in macro releases. When in doubt, bump higher; EffVer allows over-bumping, and the cost is only that users are more careful than necessary. Macro output changes are batched, and the notes of the release before a planned macro release say what is coming. 0.20.0, the first release under this policy, could not be announced that way, so its own notes explain the change. Meso releases are not held back to collect changes. Each release's notes list every output change by attribute under an "Output changes" heading. A change that affects output is listed there and not under New, Changed or Fixed, except that a change to the Python API or the command line that also affects output appears under both.

## Consequences

- Users who need identical output pin to micro releases (`dicognito~=X.Y.Z`). Users who want newer privacy coverage but linked output across runs pin to meso and micro releases within one macro number. Dependabot and Renovate read the middle number as a SemVer minor release, so users in the first group must not let them merge meso updates automatically. The README says this.
- A bump is a judgement. A table of change types and their bumps is kept with the policy and extended in the pull request that first needs a new row, and each pull request is labelled `micro`, `meso` or `macro` so the release number can be read off the merged pull requests.
- Output that changes only because pydicom changes is outside the contract, which is limited to the supported pydicom range. Such a change found by CI gets a release-note entry and, where possible, a release that restores the old output.
- A release that turns out to change linking values under a micro number is corrected by a new micro release that reverts the change, with the change re-released as a meso or macro version. The mis-numbered release is yanked from PyPI if it could damage data.
- A 1.0.0 release marks the start of the stability promise. If it changes the public API it is a macro release, but it should change no output relative to the last 0.x release.
- The README gains a "Versioning and output stability" section, and the release notes gain an "Output changes" heading. A preview flag for upcoming macro changes, as Black has, is not needed while macro changes are rare and batched, and can be revisited after 1.0.
