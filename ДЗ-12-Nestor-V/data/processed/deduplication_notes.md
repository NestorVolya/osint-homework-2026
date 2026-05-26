# Deduplication Notes

Conservative cleanup based on near-duplicate labels/usernames.

- Input nodes: 70
- Output nodes: 60
- Input edges: 68
- Output edges: 58

## Aliases merged

- `"MoldovaPolitcis"` -> `"MoldovaPolitics"` (manual typo alias)
- `"MoldovaPolitcs"` -> `"MoldovaPolitics"` (manual typo alias)
- `"ModovaPolitics"` -> `"MoldovaPolitics"` (manual typo alias)
- `"MoldovaPolitisc"` -> `"MoldovaPolitics"` (manual typo alias)
- `"MolodovaPolitics"` -> `"MoldovaPolitics"` (manual typo alias)
- `"MoldovaPolotics"` -> `"MoldovaPolitics"` (manual typo alias)
- `"MoldovaPoitics"` -> `"MoldovaPolitics"` (manual typo alias)
- `"primulinm"` -> `"primulinmd"` (manual typo alias)
- `"MoldovaPoolitics"` -> `"MoldovaPolitics"` (manual typo alias)
- `"MoldovaPoltics"` -> `"MoldovaPolitics"` (manual typo alias)

## Noise policy

Technical bot/CTA nodes are retained in the clean graph but should be marked in role analysis instead of silently deleted.
