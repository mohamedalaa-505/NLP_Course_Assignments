# Replacement record

One entry per replacement. Compare old and new on the same split, with the same
shared parts, before you change sanad.toml.

## Level _ : <part> <old version> -> <new version>

- Split and n: dev, 20 tickets (5 per variety)
- Shared parts (normalize, tokenize): v0_identity, v0_whitespace
- Parts measured: router v0_majority, search v0_exact

```
split=dev  n=20  normalize=v0_identity  tokenize=v0_whitespace

router              acc   ±95%  macroF1 declined  arabizi     egy      en     msa
v0_majority      0.200 0.179    0.067        0    0.200   0.200   0.200   0.200

search              P@3    MRR  empty  arabizi     egy      en     msa   (MRR by variety)
v0_exact         0.200 0.567      7    0.200   0.267   0.800   1.000
```

- Router: always answers `access`, which is 4 of the 20 dev tickets (1 of 5 in
  each variety). Accuracy 0.200 ± 0.179, so the margin is almost as large as the
  score. Macro-F1 is 0.067 because only `access` is ever predicted.
- Search: the correct passage is in the top 3 for 5/5 msa, 4/5 en, 2/5 egy and
  1/5 arabizi questions. 7 of 20 questions returned an empty list.
- With 5 tickets per variety, one ticket moves a variety's score a lot, so I do
  not claim real differences between varieties from these numbers.
- Decision: these are the baselines every later version must beat on the same
  20 dev tickets.

- Arabizi search gap: Arabizi questions almost never find their passage because they write Arabic words in Latin letters and digits with no fixed spelling.


