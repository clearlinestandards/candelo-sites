# Candelo Sites — phone-native, auto-deploying

This one repo hosts both live sites and **redeploys automatically** every time it's
pushed. No surge. No Netlify. No "paste this at your Mac."

| Site | Lives at (after setup) |
|------|------------------------|
| Hub | `https://clearlinestandards.github.io/candelo-sites/` |
| Maat | `https://clearlinestandards.github.io/candelo-sites/maat/` |
| Frontier package hub | `https://clearlinestandards.github.io/candelo-sites/frontier/` |
| Evidence Trail (driver PWA) | `https://clearlinestandards.github.io/candelo-sites/evidence-trail/` |

## How deploys work going forward

> ⚠️ **CORRECTED 2026-07-26 (CHG-0353 — `_active/CORRECTION_2026-07-26_candelo_sites_auth_sandbox_vs_mac.md`).**
> This section described a deploy Action that **does not exist in the repo.** Verified by
> cloning the live repo: `.github/` is **absent** from `main`, so `deploy.yml` has never
> run. **GitHub Pages is serving branch-based from `main`.** Corrected text below.

~~`.github/workflows/deploy.yml` runs on GitHub's servers on every push.~~ — **not true.**
**Pages is branch-based off `main`.** Push to `main` and Pages republishes; there is no
Action involved. Claude pushes from the sandbox over `github.com` (reachable — verified
2026-07-26, `git ls-remote` exit 0), so a deploy is **Claude running `push.sh`.**

~~Bill can force a deploy from the GitHub iOS app → Actions tab → Run workflow.~~
**That fallback does not exist — there is no workflow to run.** The only way files reach
the repo is a push, and a push needs a credential (see below).

**Deploy history (receipt):** the repo has exactly one commit — `18dda4b`, 2026-07-04,
author `Candelo Deploy <deploy@candelogroup.com>`, the identity hard-coded in `push.sh`
line 28. Proof `push.sh` ran, and therefore proof a token was supplied that day.

## ONE-TIME CONNECT (all phone-doable, ~3 min, never again)
Do this once in Safari or the GitHub iOS app:

1. **Account** — sign in at github.com (or create one). Free.
2. **Repo** — New repository → name it `candelo-sites` → Public → Create. Leave it empty
   (no README).
3. **Token** — Settings → Developer settings → Fine-grained personal access tokens →
   Generate new token. Scope it to **only the `candelo-sites` repo**, with permissions:
   **Contents: Read and write**, **Workflows: Read and write**, **Pages: Read and write**.
   Copy the token (starts `github_pat_…`).
4. **Hand the token to Claude AND STORE IT.** ⚠️ **CORRECTED 2026-07-26 (CHG-0353).**
   A past session (2026-04-19) told Bill *"No. Don't save it."* when he asked
   *"do i need to save this anywhere or in a vault?"* **That instruction is why this keeps
   recurring** — every deploy needs a fresh paste. It is a `_foundations/07` half-loop.
   **Store the token** in a git-ignored `_deploy/candelo-sites/.env` that `push.sh` sources,
   with a long expiry. `push.sh` now refuses to publish if a `.env` or token-shaped string
   reaches the staging dir, so storing it here is safe.
   *(Checked 2026-07-26: there is **no GitHub MCP connector** in the connector registry
   available to these sessions — a stored fine-grained PAT is currently the only path.)*

After step 4, every future deploy is automatic — Claude pushes, Pages rebuilds, Bill
taps nothing. Custom domains (e.g. maat.candelogroup.com) can be mapped later in repo
Settings → Pages.
