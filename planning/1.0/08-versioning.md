# Versioning: SemVer or EffVer

This document weighs [Semantic Versioning](https://semver.org/) (SemVer) against [Intended Effort Versioning](https://jacobtomlinson.dev/effver/) (EffVer) for dicognito, and proposes the policy that either scheme needs. It feeds decision Q10 in [07-roadmap.md](07-roadmap.md#decisions-needed).

## The problem

Dicognito has three contracts with its users:

| Contract | Who depends on it | What a change looks like |
|---|---|---|
| Python API | Code that builds an `Anonymizer`, adds element handlers, or subclasses `ElementAnonymizer` | Renamed or removed classes and methods, changed handler order |
| Command line | Scripts and pipelines that call `dicognito` | Renamed or removed options, changed defaults, changed exit codes |
| Output | Everyone who keeps, compares or links anonymized data | A different value written for the same input, seed and options |

SemVer was designed around the first two. The third is the one users care about most, and its changes do not fit "bug fix, feature, breaking change". The release notes already show this. The unreleased section lists "Anonymize AdmissionID and ServiceEpisodeID" under **New** and "Anonymize InstitutionAddress when there is no InstitutionName" under **Fixed**. Both change the output for every file that contains those attributes, in the same way. 0.14.0 listed "Anonymized UI values are now consistent between runs" under **Changed**.

The cost of an output change depends on who is upgrading, not on what kind of change it is:

| Audience | How they use dicognito | Cost of a change to an attribute dicognito already modifies | Cost of a newly modified attribute |
|---|---|---|---|
| Incremental test-data builder | Anonymizes new batches with a fixed seed and adds them to data already in a PACS | High for identifiers, UIDs, patient names and dates: the new batch no longer links to the old one, so patients and studies are duplicated. Re-anonymizing the whole corpus is the only fix | Usually none. The attribute held original values in old objects and pseudonyms in new ones; it matters only if something links on it |
| Regression suite owner | Compares anonymized output with stored expected files | Low to medium: regenerate the expected files | Low to medium: same |
| Workflow tester | Relies on a value surviving anonymization (routing on `StationName`, hanging protocols on `SeriesDescription`) | Low | Medium: the workflow stops matching, and an override (`--keep`) is needed |
| One-shot exporter | Anonymizes once for a trial or a share and never re-runs | None | None, and they want privacy improvements as soon as possible |
| Library extender | Adds or replaces handlers | Low, unless the change touches handler order or the generator it overrides | Medium if their handler now competes with a new built-in one |

No version number can describe all five rows at once. Whatever the scheme, the release notes have to say which attributes changed and how.

## The two schemes

**SemVer** (MAJOR.MINOR.PATCH) asks the project to declare a public API, then bumps MAJOR for incompatible changes, MINOR for backwards-compatible features and PATCH for backwards-compatible fixes. Users and tools read MINOR and PATCH as "safe to take".

**EffVer** (Macro.Meso.Micro) uses the same three numbers but bumps them by the effort an existing user is expected to spend to adopt the release:

- **Micro:** "this change doesn't intend for you to need to do anything".
- **Meso:** "some small effort may be required to make sure this version works for you".
- **Macro:** "you will need to dedicate some significant time to upgrading to this version".

EffVer does not separate fixes from features, allows over-bumping (for example to mark a milestone), and treats `0.x` versions as `0.Macro.Micro`. Because the format is identical, a project can move between SemVer and EffVer just by changing how it chooses the next number; no epoch or tooling change is needed. If a release was bumped too little, EffVer suggests publishing a corrected pair of versions rather than rewriting history.

## How each change type would be versioned

The "SemVer" column assumes dicognito declares the output contract as part of its public API, which SemVer requires for the column to mean anything.

| Change type | Example | EffVer | SemVer with a declared output contract |
|---|---|---|---|
| Crash fix for input that failed before | Unparseable dates no longer raise (C-1) | Micro | Patch |
| New opt-in option, default output unchanged | `--report report.json` | Micro | Minor |
| Newly modified attribute (it was passed through before) | `AdmissionID`, `StationName` cleaned, a new PS3.15 edition adds attributes | Meso | Minor, if the contract says the set of modified attributes may grow; otherwise major |
| Changed generator for an attribute that links objects across runs | Whole-day date shift (Q3), HMAC (Q6), empty IDs stay empty (I-6), issuer handling (I-2) | Macro | Major |
| Changed generator for an attribute that is not used for linking | Physician name independent of context (I-1), address parts (I-11), name normalization (I-12) | Meso | Major |
| Changed default that removes or keeps a category | Private attributes removed by default (Q2) | Macro | Major |
| Status attributes made accurate | `PatientIdentityRemoved` no longer over-claims (I-15) | Meso | Minor or major, depending on whether anyone reads them |
| Python or pydicom support dropped | 0.18.0 dropped Python 3.8 and 3.9 | Meso | Minor by common practice, major by the letter |
| Public API removed or renamed | API cut (Q7) | Macro | Major |
| Deprecation announced, nothing removed | Warning when neither `-i` nor `-o` is given (0.15.0) | Micro | Minor |

The bump decisions mostly coincide. The difference is in the rows where SemVer needs either a carve-out ("minor releases may modify more attributes") or a major release. With a carve-out, SemVer users who treat minor releases as safe are surprised. Without one, every privacy improvement becomes a major release, which teaches users to delay exactly the upgrades they should take.

## SemVer for dicognito

Pluses:

- It is the default expectation. Users, Dependabot and Renovate all assume it, and dicognito already claims it implicitly.
- "Major means breaking" is a strong, simple promise that suits incremental test-data builders, who are the main audience.
- The roadmap's 1.0 definition already assumes it.

Minuses:

- It only works once the output contract is written down, and the contract then decides every hard case. SemVer itself gives no help with them.
- The "is this a fix or a feature" question remains, as the InstitutionAddress example shows, even though the answer does not matter to users.
- Either privacy improvements wait for a major release, or the contract carves them out and minor releases stop being "safe".
- Strictly applied, it produces frequent major releases while coverage grows toward PS3.15, which weakens the signal a major release is meant to send.

## EffVer for dicognito

Pluses:

- It asks the question that matters for anonymized output ("what must I do to upgrade?") instead of one that has no good answer ("is a newly pseudonymized attribute a fix?").
- Newly modified attributes and privacy fixes can ship promptly as meso releases. Meso releases are cheap, so there is no reason to hold them back.
- It is honest that any release can change output for someone, which is true for an anonymizer.
- It is compatible with SemVer tooling and can be reversed later without an epoch.
- Over-bumping lets 1.0 mark the start of the stability promise without inventing a breaking change for it.

Minuses:

- It is less widely known. Tools and readers will interpret a meso bump as a SemVer minor and may merge it automatically. Users who need reproducible output must pin more tightly than they would under SemVer (see "Guidance for users").
- Effort is a judgement. Without a written table, bumps become inconsistent over time.
- Effort differs by audience, as shown above. The number reflects the highest-effort audience a maintainer chooses to care about, so the policy has to name that audience.
- The 1.0 roadmap and the README would need wording changes. That is small.

## Precedent

Black, the Python formatter, faces the same problem: its output is its contract, and every formatting fix changes someone's output. It uses year-based version numbers and a [stability policy](https://black.readthedocs.io/en/stable/the_black_code_style/index.html): code formatted with one release "will remain unchanged when formatted with the same options using any other release in the same calendar year". Stable style changes land only in the first release of a year. Proposed changes are available earlier behind `--preview` and `--unstable`, which "are exempt from this policy". Crash fixes are unrestricted, as are changes that only affect code Black could not format before.

The lessons apply to dicognito under either scheme: write the output policy explicitly, batch output changes, let users try upcoming changes early, and treat "previously failed" input as free to change.

## Recommendation

Adopt EffVer, and write an output-stability policy that defines the effort levels in dicognito's terms. The policy matters more than the scheme: the same table could back SemVer if the maintainer prefers its familiarity. EffVer is recommended because dicognito's main contract is its output, and EffVer lets privacy improvements ship as meso releases without either a misleading "minor" or a disruptive "major".

EffVer can be adopted now, since `0.Macro.Micro` matches how 0.x releases have been numbered: 0.19.0 and the unreleased changes both modify output and both bump the middle number.

## Proposed guidance

### The output contract

Put a "Versioning and output stability" section in the README, along these lines:

> Dicognito uses Intended Effort Versioning (Macro.Meso.Micro). For a given input, seed and set of options, and a pydicom version within the supported range:
>
> - Micro releases do not change output, except for input that previously failed to anonymize.
> - Meso releases may modify attributes that were previously passed through, change values for attributes that are not used to link objects, and drop support for old Python or pydicom versions. They do not change identifiers, UIDs, patient names or dates.
> - Macro releases may change any output, including the values that link objects across runs.
>
> Each release's notes list every output change by attribute.

The policy names the incremental test-data builder as the audience it protects: linking values (identifiers, UIDs, patient names and dates) change only in macro releases.

### Deciding the bump

- Use the table in "How each change type would be versioned" as the rule. Add rows as new cases come up, in the same PR that first needs them.
- When unsure, bump higher: EffVer allows over-bumping, and the cost is only users being more careful than necessary.
- Batch macro output changes (Q5). Each macro release should be planned and announced in the previous release's notes.
- Do not hold meso releases back to collect changes. A newly modified attribute that closes a leak should ship promptly.
- Changes to the generated PS3.15 table follow the same rules: new attributes are meso, changed actions on attributes already handled are meso or macro by the table.
- Mark the effort in each PR (a `micro`, `meso` or `macro` label), so the release bump can be read off the merged PRs.

### Release notes

Add an **Output changes** heading to each release, separate from New, Changed and Fixed. Under it, one line per affected attribute or group, saying whether the attribute is newly modified, generated differently, removed or kept, and why. For example:

> ### Output changes
>
> - `AdmissionID`, `ServiceEpisodeID`: newly anonymized (#192)
> - `InstitutionAddress`: now anonymized when `InstitutionName` is absent (#192)

An incremental test-data builder can then decide from one section whether to re-anonymize. Today the same kind of change appears under three different headings.

### Guidance for users

Add this to the README:

| You need | Pin to |
|---|---|
| Identical output across runs (incremental test data, golden files) | `dicognito~=1.4.0`: micro releases only. Read the "Output changes" section before moving to a new meso release |
| Linked output across runs, but newer privacy coverage is welcome | `dicognito>=1.4,<2`: meso and micro releases. Linking values change only in macro releases |
| The best privacy coverage, output reproducibility not needed | The latest release |

Point out that tools such as Dependabot and Renovate treat the middle number as a SemVer minor release; users who need identical output should configure them to propose meso updates separately rather than merging them automatically.

### pydicom

Output can change because of pydicom alone, for example through its private-tag dictionary (I-8). Dicognito cannot version that. The contract above is limited to the supported pydicom range, and CI should run the golden-output test (T-1) against both the minimum and the latest pydicom. A pydicom-induced output change found that way gets a release-note entry and, if a workaround is possible, a dicognito release that restores the old output.

### Correcting a wrong bump

If a micro release turns out to change linking values, publish a new micro release that reverts the change and re-release the change as a meso or macro version. The version comes from `release_notes.md`, so the revert release is cut from a branch at the last good commit. Yank the mis-numbered release on PyPI if it could damage data, and say so in the release notes.

### Preview of upcoming output changes

A Black-style `--preview` flag, enabling the next macro release's output changes ahead of time, would let incremental users test them. It costs a code path per change and is not needed while macro changes are rare and batched. Revisit after 1.0 if users ask for it. The profile engine's options (0.22) may be a better place for such switches than a separate flag.

## Effect on the rest of the plan

- **"What 1.0 should mean":** "Semantic versioning" becomes "a declared versioning scheme and output-stability policy".
- **0.20:** add the README section, the release-notes heading and the PR labels. This is a small, documentation-only PR, and it lets 0.20 itself be described in the new terms.
- **0.21 output-change batch:** a macro event. In 0.x it is numbered 0.21.0, exactly as planned.
- **1.0.0:** a macro release because of the API cut (Q7), but it should change no output relative to the last 0.x release. It marks the start of the stability promise and the production-stable classifier.
