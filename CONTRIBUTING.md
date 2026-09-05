# Contributing to sortgs

This document is the contributor and release guide. End-user install and CLI usage stay in the [README](README.md).

## Repository layout

- Default integration branch: `dev`
- Production / PyPI line: `main`
- Package code: `src/sortgs/`
- Tests: `tests/` (offline by default; network tests are marked `live`)
- Lockfile: `uv.lock` (commit it)
- Interpreter pin: `.python-version` (3.12 for local work)

Do not add `Co-authored-by` trailers. Use a personal git identity, not a work email, on this repository.

## Tooling: uv, not conda

Development uses [uv](https://docs.astral.sh/uv/). There is no `conda_environment.yml` or `requirements.txt`.

`uv sync --group dev` is **not** “sync the `dev` git branch”. `--group dev` installs the optional **dependency group** named `dev` in `pyproject.toml` (pytest, ruff) on top of the runtime dependencies. You can run it on any branch, including `main`.

| Command | Who it is for |
|---|---|
| `uv sync --group dev` | Local development and CI (package + pytest + ruff) |
| `uv sync --no-dev` | Runtime-only environment |
| `pip install sortgs` | End users, after a PyPI release. They do **not** get the `dev` group |

### First-time setup

```bash
# From the repository root
uv sync --group dev
source .venv/bin/activate   # optional; uv run … is enough
uv run sortgs --help
```

Python floor is **3.10**. Local pin is **3.12**. CI runs 3.10, 3.12, and 3.13 against `uv.lock` (`--frozen`).

If you change `[project].dependencies` or `[dependency-groups]`, run `uv lock` and commit `uv.lock`.

## Tests

```bash
uv run pytest
```

That is the default suite: units and offline integrations. It must not hit Google Scholar or the Web Archive. It is what GitHub Actions runs on pull requests.

Network / Archive tests live in `tests/test_sortgs.py` and are marked `live`. They are excluded unless you ask for them:

```bash
RUN_LIVE_TESTS=1 uv run pytest -m live
```

Do not use `os.system` in new tests. Prefer calling functions, or `main()` with a mocked `sys.argv`. Mark anything that needs the internet as `live`.

### Checking the direct Scholar path locally

The default `requests` session sends a browser User-Agent. A successful local run looks like this — two “Loading next …” lines and **no** Selenium warning:

```bash
uv run sortgs "generative ai" --nresults 20
```

If you see `Robot check detected, using Selenium fallback`, the UA was not enough (CAPTCHA / blocked IP). If both paths fail, the process exits with status 1 and does not write an empty CSV.

Google Colab shared IPs are often blocked even with the UA. Prefer a local run to validate retrieval.

## Pull requests

1. Branch from current `origin/dev` (or `main` only if you are doing a hotfix on the published line):

   ```bash
   git fetch origin
   git checkout -b wittmann/short-slug origin/dev
   ```

2. Keep the change focused. Do not mix SearchApi work, scraper rewrites, and release metadata unless that is the agreed scope.

3. `uv run pytest` must pass.

4. Open a PR **into `dev`**. Describe what changed and how you tested it.

5. Do not force-push `dev` or `main`.

## Version numbers

The single source of truth is `[project].version` in `pyproject.toml`. After changing it:

```bash
uv lock
```

Commit both `pyproject.toml` and `uv.lock`. Do **not** use `.bumpversion.cfg` / bump2version (removed; it pointed at a deleted `setup.py`).

PyPI rejects a second upload of the same version. If `1.0.8` is already published, bump again (`1.0.9`, …) before another release.

## Release: merge to `main` and publish 1.0.8

Do this only when the release candidate (for example PR #69) is green and you intend users to `pip install` the new build.

### 1. Confirm the version on the branch you will merge

```bash
grep '^version' pyproject.toml    # expect 1.0.8
uv run pytest
```

### 2. Merge into `dev`, then into `main`

GitHub UI or:

```bash
git checkout dev
git pull origin dev
git merge --ff-only wittmann/direct-ua-and-tooling   # or merge the PR via gh
git push origin dev

git checkout main
git pull origin main
git merge origin/dev
git push origin main
```

Prefer merging the PR on GitHub so CI and review stay attached. Fast-forward when you can; do not force-push `main`.

### 3. Tag the release commit on `main`

```bash
git checkout main
git pull origin main
git tag -a v1.0.8 -m "sortgs 1.0.8"
git push origin v1.0.8
```

The tag must point at the commit that contains `version = "1.0.8"`.

### 4. Publish to PyPI

The workflow [Publish Python Package to PyPI](.github/workflows/deploy-to-pypi.yml) is **manual** (`workflow_dispatch`). It builds with `python -m build` and uploads with Twine using `secrets.PYPI_API_TOKEN`. On GitHub: **Actions** → that workflow → **Run workflow**.

1. Confirm the secret `PYPI_API_TOKEN` exists on the GitHub repo (a PyPI API token; Twine username is `__token__`).
2. GitHub → **Actions** → **Publish Python Package to PyPI** → **Run workflow**.
3. Run it from the `main` branch (the commit you just tagged).

Optional local publish (same token; do not commit it):

```bash
uv build
# inspect dist/sortgs-1.0.8-py3-none-any.whl and the sdist
uvx twine check dist/*
uvx twine upload dist/*
```

### 5. Verify

- [ ] https://pypi.org/project/sortgs/1.0.8/
- [ ] In a clean environment: `pip install sortgs==1.0.8 && sortgs --help`
- [ ] Optional: GitHub → **Releases** → draft from tag `v1.0.8` (UA fix, uv/offline tests, empty-CSV-on-block). Leave SearchApi (#67) out of the notes unless that PR is also in `main`.

### What this release is (1.0.8)

- Direct path sends a browser User-Agent; blocked + failed Selenium no longer writes a fake empty CSV.
- Dev install is uv; default tests are offline.
- **Not** included unless separately merged: SearchApi `--provider`, affiliate README, citation-count work.

## What not to put in a PR

- `.env`, API keys, `.context/`, local plan notes, inspect dumps under `.venv/`
- Generated `*.csv` from smoke runs
- `Co-authored-by` trailers or work-email author/committer
- Unrelated Docker/PyPI workflow rewrites unless that is the PR
