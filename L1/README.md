# Sanad

Sanad is a university help-desk assistant that you build over six levels, one
after each of Chapters 1–6. The Lab Manual sets the tasks for each level.

## Set up

You need Python 3.11 or newer (`python3 --version`).

```sh
cd L1                                                  # the folder this zip extracted to
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -v
python -m sanad report
```

The tests for the current level are held back for grading and show as
skipped. Leave those files unchanged and put your own tests in new files next
to them. The tests for earlier levels run in full.

## Replace a part

1. Implement the new version.
2. Run `python -m sanad report` and compare the old and new versions on the
   same dev split.
3. Write an entry in `REPLACEMENTS.md`. Change `sanad.toml` only if the
   evidence supports it. Keeping the old version is a valid result.

Never delete an old version. The test split stays closed until level 6.

## Data statement

- **Purpose and source.** Constructed teaching tickets that imitate a
  university help desk. They are not real student messages and contain no
  personal data.
- **Varieties.** English (`en`), Modern Standard Arabic (`msa`), Egyptian
  Arabic (`egy`), and Arabizi (`arabizi`), recorded in each ticket's
  `variety` field.
- **Labels.** Five intents (`access`, `assessment`, `registration`, `fees`,
  `other`), plus the slots `course`, `amount`, and `faq`.
- **Splits.** 75 train, 20 dev, 20 test.
- **Limits.** With 20 dev tickets, each variety has only 5. Report counts as
  well as rates, and do not claim a difference between varieties from these
  numbers. Scores here say nothing about real users.
