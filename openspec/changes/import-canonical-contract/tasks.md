# Tasks

## 1. Import

- [x] 1.1 Copy `event-contract.{xml,json,md}` + `schemas/*.schema.json` from `dotfiles-v3/contracts/`. Verify: `diff -r contracts/schemas dotfiles-v3/contracts/schemas` → no output, and `diff` each file. ✅ (all byte-identical)
- [x] 1.2 Record the cut commit SHA on the ticket. Verify: `git -C dotfiles-v3 rev-parse HEAD`. ✅ (`ce3fd4a4`)

## 2. Publish

- [ ] 2.1 Commit + push the repo. Verify: `git log --oneline -1`; `git push`. (Commit done; push pending — user's call.)
