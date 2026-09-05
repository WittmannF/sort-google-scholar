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

Python floor is **3.10** (`requires-python`). Local pin and CI are **3.12**. Older versions are not exercised in Actions.

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

Commit both `pyproject.toml` and `uv.lock`. Do not use bump2version / a leftover `.bumpversion.cfg` (that tool pointed at a deleted `setup.py`).

PyPI rejects a second upload of the same version. Bump before every publish.

Typical bumps:

- **patch** (`x.y.Z`) — bug fix, docs, tooling that users should get via `pip install -U`
- **minor** (`x.Y.0`) — new CLI flag or optional behavior, backward compatible
- **major** (`X.0.0`) — breaking CLI or CSV contract

## Releasing

Day-to-day work lands on `dev`. **`main` is the release line.** A push or merge into `main` runs [Publish Python Package to PyPI](.github/workflows/deploy-to-pypi.yml) and uploads the version in `pyproject.toml`. A merge into `dev` does not publish.

Bump the version **before** that `main` merge. PyPI rejects a second upload of the same number; the workflow uses `--skip-existing`, so a later `main` push without a bump will pass and do nothing.

`workflow_dispatch` remains as a manual retry (Actions → that workflow → Run workflow on `main`).

### 1. Bump and lock (on `dev`)

Set the new version in `pyproject.toml`, then:

```bash
uv lock
uv run pytest
grep '^version' pyproject.toml
```

Commit `pyproject.toml` and `uv.lock` on the feature branch and merge into `dev`. CI on `dev` should be green.

### 2. Merge `dev` into `main`

That push is the publish. Fast-forward when you can. Do not force-push `main`.

```bash
git checkout main
git pull origin main
git merge origin/dev
git push origin main
```

Prefer a GitHub PR `dev` → `main` so the release is reviewable. Confirm `secrets.PYPI_API_TOKEN` exists (Twine username `__token__`).

### 3. Optional tag and GitHub Release

Not required for PyPI. Useful as a label on `main`:

```bash
git checkout main
git pull origin main
git tag -a "vX.Y.Z" -m "sortgs X.Y.Z"
git push origin "vX.Y.Z"
```

### 4. Verify

- [ ] Actions run **Publish Python Package to PyPI** on the `main` push and succeeded
- [ ] `https://pypi.org/project/sortgs/X.Y.Z/`
- [ ] Clean env: `pip install sortgs==X.Y.Z && sortgs --help`

Optional local publish (do not commit the token):

```bash
uv build
uvx twine check dist/*
uvx twine upload dist/*
```

## What not to put in a PR

- `.env`, API keys, `.context/`, local plan notes, inspect dumps under `.venv/`
- Generated `*.csv` from smoke runs
- `Co-authored-by` trailers or work-email author/committer
- Unrelated Docker/PyPI workflow rewrites unless that is the PR
