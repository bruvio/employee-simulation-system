# PRP: Consolidate Results Paths & Enforce Population Size

## Context
- `results/` shows only **empty folders** (no files).
- Artifacts (JSON) are written to `./artifacts/`.
- Charts (PNG) are written **outside the project** to `~/bruvio-tools/images/`.
- Config targets **500** employees, but logs report: **Analyzed 1,000 employees**.

**Log excerpts provided**
```
POPULATION: artifacts/employee_population_20250815_045900.json
SIMULATION: artifacts/simulation_results_20250815_045900.json
VISUALIZATIONS:
  population_overview: /Users/brunoviola/bruvio-tools/images/employee_simulation_population_overview_20250815_045901.png
  gender_analysis:     /Users/brunoviola/bruvio-tools/images/employee_simulation_gender_pay_gap_analysis_20250815_045901.png
  performance_analysis:/Users/brunoviola/bruvio-tools/images/employee_simulation_performance_analysis_20250815_045902.png
  salary_distributions:/Users/brunoviola/bruvio-tools/images/employee_simulation_salary_distributions_20250815_045903.png
  inequality_reduction:/Users/brunoviola/bruvio-tools/images/employee_simulation_inequality_reduction_analysis_20250815_045904.png
  review_cycles:       /Users/brunoviola/bruvio-tools/images/employee_simulation_review_cycle_progression_20250815_045905.png
**Analysis Scope**: Analyzed 1,000 employees
```

---

## Problem
1. **Output sprawl**: Writers save to hard-coded locations (`~/bruvio-tools/images`, `./artifacts`) instead of the run’s `results/` tree.
2. **Empty `results/`**: Orchestrator prepares directories, but saving routines ignore them.
3. **Population mismatch**: The effective population size silently defaults to **1,000** if the config key isn’t recognized or is missing.

---

## Goals
- **Single source of truth** for output paths inside the repository.
- **Deterministic run folder** that contains *all* artifacts, tables, and charts.
- **Strict, logged enforcement** of population size from configuration (or CLI)—no silent defaults.

---

## Proposed Fix (Implementation Plan)

### 1) One Path Authority (inside the repo)
Add `app_paths.py` that sets and creates a per-run directory:
```
<repo>/results/run_YYYYMMDD_HHMMSS/
  ├─ artifacts/         # JSON & derived static data
  └─ assets/
     ├─ charts/         # PNG/SVG
     └─ tables/         # CSV exports if any
```
- Base override: CLI `--out` or env `SIM_OUTPUT_DIR`.
- Early directory creation at orchestrator start.

**Sketch**
```python
# app_paths.py
from pathlib import Path
from datetime import datetime
import os

def repo_root(p: Path | None = None) -> Path:
    p = (p or Path(__file__)).resolve()
    for parent in [p] + list(p.parents):
        if (parent/".git").exists() or (parent/"pyproject.toml").exists() or (parent/"requirements.txt").exists():
            return parent
    return Path.cwd().resolve()

REPO_ROOT   = repo_root()
BASE_OUTPUT = Path(os.environ.get("SIM_OUTPUT_DIR") or (REPO_ROOT / "results")).resolve()
RUN_STAMP   = os.environ.get("SIM_RUN_STAMP") or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
RUN_DIR     = BASE_OUTPUT / f"run_{RUN_STAMP}"
ARTIFACTS_DIR = RUN_DIR / "artifacts"
CHARTS_DIR    = RUN_DIR / "assets" / "charts"
TABLES_DIR    = RUN_DIR / "assets" / "tables"

def ensure_dirs():
    for d in (ARTIFACTS_DIR, CHARTS_DIR, TABLES_DIR):
        d.mkdir(parents=True, exist_ok=True)
```

### 2) Route All Writers to Project Paths
- Replace any use of `~/bruvio-tools/images` and `./artifacts`.
- Save JSON → `ARTIFACTS_DIR`, charts → `CHARTS_DIR`, CSV → `TABLES_DIR`.

**Example**
```python
# artifacts
out = ARTIFACTS_DIR / f"employee_population_{stamp}.json"
out.write_text(json.dumps(population, indent=2))
logger.info("POPULATION: %s", out)

# charts
chart_path = CHARTS_DIR / f"employee_simulation_population_overview_{stamp}.png"
fig.savefig(chart_path, dpi=160, bbox_inches="tight")
logger.info("VISUALIZATIONS: population_overview: %s", chart_path)
```

### 3) Enforce & Log Population Size
- Normalize config keys: accept `population_size` (preferred) or `n_employees`.
- If both exist and differ → **fail** with a useful message.
- If none provided → **fail** (do not default to 1,000).
- Log the **effective value** and **its source**.

**Example**
```python
def get_population_size(cfg: dict, cli_value: int | None = None) -> tuple[int, str]:
    if cli_value is not None:
        return int(cli_value), "--population-size"
    keys = [k for k in ("population_size","n_employees") if k in cfg]
    if not keys:
        raise KeyError("Set 'population_size' (preferred) or 'n_employees' in config")
    if len(keys) == 2 and int(cfg["population_size"]) != int(cfg["n_employees"]):
        raise ValueError("Conflicting sizes: population_size!=n_employees")
    key = keys[0]
    return int(cfg[key]), f"config.{key}"
```

Construct the generator with the returned value and log:
```
INFO Effective population size: 500 (source: config.population_size)
```

### 4) Clean Empty `results/` Folders (safe)
- The current empty directories under `results/` can be **deleted** safely (no files).

**Command**
```bash
find results -type d -empty -print -delete
```

---

## Acceptance Criteria
- A run produces a single run directory under `results/` containing **all** outputs:
  - `results/run_YYYYMMDD_HHMMSS/artifacts/*.json`
  - `results/run_YYYYMMDD_HHMMSS/assets/charts/*.png`
  - `results/run_YYYYMMDD_HHMMSS/assets/tables/*.csv` (if produced)
- Logs reference only **project-internal** paths (no `~/bruvio-tools/images`).
- Logs display the **effective population size** with its **source** (e.g., `config.population_size`), and it matches the config (e.g., 500).
- Missing or conflicting config results in a clear error; there is **no** silent fallback to 1,000.

---

## Branch & Changes
- **Branch**: `fix/results-paths-and-scope`
- **Changes**:
  - `app_paths.py` (new)
  - Orchestrator: call `ensure_dirs()`, use `ARTIFACTS_DIR/CHARTS_DIR/TABLES_DIR`
  - Writers/plotters: stop using external paths; save under run dir
  - Config parsing: normalize/enforce population size
- **Post-merge task**: delete empty `results/` folders (one-off clean).

---

## Risk & Rollback
- **Risk**: legacy scripts expecting `./artifacts` will need path updates (or a one-release symlink).
- **Rollback**: revert branch; previous behavior restored.
