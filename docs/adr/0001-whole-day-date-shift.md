# 1. Shift dates by a whole number of days and leave times of day unchanged

Status: Accepted

Date: 2026-11-26

## Context

dicognito hides when a study took place by moving every date back by a pseudo-random offset derived from the seed. The offset is currently a whole number of hours. A date with an associated time, and every `DT` value, is shifted by exactly that many hours. A date with no time is treated as midnight and shifted by the same number of hours, and only the date is kept, so it can move by a different number of days than the same date with a time.

That produces three problems:

- **One source date, two output dates.** `StudyDate` with a `StudyTime` of 23:00 and a `SeriesDate` with no time can start on the same day and end up on different days, because the first is shifted by hours and can cross midnight and the second cannot. A date-only attribute has no time to pair with, so no amount of better pairing fixes this.
- **Unpaired times are not shifted.** A time with no date of its own (for example `SeriesTime` alone) is left unchanged, while a `StudyTime` that comes with a `StudyDate` is shifted. The two no longer agree with each other.
- **`--keep` does not work for times.** The partner time of a date is found and changed while the date is being handled, so keeping `StudyTime` while anonymizing `StudyDate` still changes it.

## Options considered

1. **Keep the hour-based offset and pair dates and times more carefully.** Fixes the unpaired times and `--keep`, but cannot fix the first problem, for the reason given above.
2. **Shift times separately from dates**, by a different offset, with or without carrying into the date. Any offset that is not a multiple of 24 hours either splits a date from its time or reverses the order of events and distorts durations between values that include a date and a time.
3. **Shift dates by a whole number of days and leave times of day unchanged.** Every date attribute of one source date moves to the same new date, whether or not a time is present. Times stay consistent with each other, and a time is no longer touched when its date is.

## Decision

Option 3. The offset is a whole number of days. Date (`DA`) values and the date part of date-time (`DT`) values shift by it. Time (`TM`) values, and the time part of `DT` values, are not changed.

## Consequences

- Dates shift identically with or without a time, and every time stays consistent with every other time and with its date.
- `--keep` works per attribute, including times.
- The interval between any two dates is preserved exactly, so an age computed from the shifted dates (for example `StudyDate` minus `PatientBirthDate`) still agrees with `PatientAge`, which is not modified.
- The time of day of every acquisition is retained. This relies on the judgment that a time of day on its own does not identify a patient. It should be stated in the user documentation.
- This follows the intent of the PS3.15 option "Retain Longitudinal Temporal Information With Modified Dates" (E.3.6): dates are modified, and gross and fine temporal relationships are kept. It does not follow the letter. E.3.6 says "any dates and times" in the Table E.1-1 attributes shall be modified, and the table marks time attributes such as `StudyTime` as C (clean) under that option. An unchanged time is not a modified one. The manner of date modification must be described in the conformance statement, and so should this departure.
- E.3.6 also notes that time transformations must not disrupt computations such as the PET SUV comparison of injection time with acquisition time. Leaving times unchanged guarantees that.
- Setting `LongitudinalTemporalInformationModified` is a separate decision.
- The pairing logic that guesses a date's partner time from its keyword is no longer needed and can be removed.
- This changes the output for every object that carries a date, so it ships with the next major version. Anonymized output from earlier versions cannot be matched with output from this version.
