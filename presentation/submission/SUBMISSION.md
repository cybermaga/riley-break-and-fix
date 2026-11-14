# Entropy submission — exact values

The form has three visible fields and **no turn-ID field**, so the evidence rides in the PDF.

| Form field | What to enter |
|---|---|
| **GitHub repo link (must be public)** | ⚠️ **No valid URL yet.** `github.com/neogyk/hacker` and PR #1 both return **404 to anonymous visitors** (the repo is private). Needs one owner action — see below. |
| **Other links** | (optional) the PR URL *after* the repo is made public |
| **File upload (≤10 MB)** | **`Riley-Break-and-Fix.pdf`** (≈0.4 MB) |

## The one owner action
Publish a public repo so the required field has a working link. Two options:

1. **Flip the team repo public** — the teammate (repo owner `neogyk`) makes `neogyk/hacker`
   public. Then the repo + PR #1 links work for judges.
2. **Publish just the defense package** from this folder (`public-repo/`) under Margarita's
   account. Example (run by the owner, verify before pushing):
   ```bash
   cd public-repo
   git init && git add . && git commit -m "Riley break & fix — defense + evidence"
   gh repo create riley-break-and-fix --public --source=. --push
   ```
   Then paste that repo URL into the "GitHub repo link" field.

Nothing else blocks submission — the PDF carries the full narrative and evidence (Appendix A
has the full turn IDs).

## Pre-send checklist
- [ ] Owner publishes a repo → paste its public URL (test it in a logged-out browser first).
- [ ] Upload `Riley-Break-and-Fix.pdf`.
- [ ] (optional) Add the PR URL under "Other links".
