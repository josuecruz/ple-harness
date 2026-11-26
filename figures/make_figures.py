# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Write the three required figures and the cover from eval/run.py results.

Usage: python3 figures/make_figures.py runs/<run-a> [label=path ...]
Every number plotted comes from a results.json produced by eval/run.py.
"""

from __future__ import annotations

import json
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Assumed USD per 1M tokens (input, cache read, output) for the declared model.
# Update these to the published prices when writing up the cost plot.
PRICES = {
    "claude-opus-5-5": (5.0, 0.5, 25.0),
    "gemini-3.8-flash": (0.3, 0.03, 2.5),
    "gemini-4-argon": (2.0, 0.2, 10.0),
}

OUT = pathlib.Path(__file__).resolve().parent


def load(arg: str) -> tuple[str, dict]:
  """Loads one results.json; `label=path` overrides the directory label."""
  label, _, path = arg.rpartition("=") if "=" in arg else (pathlib.Path(arg).name, "", arg)
  data = json.loads((pathlib.Path(path) / "results.json").read_text())
  return label, data


def cost_per_task(data: dict) -> float:
  """Mean estimated USD per task from the token usage recorded by the runner."""
  model = str(data.get("model", ""))
  price = PRICES.get(model, (0.0, 0.0, 0.0))
  costs = []
  for row in data.get("tasks", []):
    tok = row.get("tokens") or {}
    costs.append(
        (
            tok.get("input", 0) * price[0]
            + tok.get("cache_read", 0) * price[1]
            + tok.get("output", 0) * price[2]
        )
        / 1_000_000
    )
  return sum(costs) / len(costs) if costs else 0.0


def architecture() -> None:
  """Draws the harness architecture diagram."""
  fig, ax = plt.subplots(figsize=(11, 6))
  ax.axis("off")
  boxes = [
      (0.04, 0.62, 0.28, 0.22, "Prompt + project files\n(task container)"),
      (0.36, 0.62, 0.28, 0.22, "PLE evaluator\nWebSocket protocol"),
      (0.68, 0.62, 0.28, 0.22, "Google-sponsored model\n(tool calls)"),
      (0.04, 0.22, 0.28, 0.22, "bash / read / write\n+ MCP tools"),
      (0.36, 0.22, 0.28, 0.22, "Evidence checklist\nunits, clauses, ledger"),
      (0.68, 0.22, 0.28, 0.22, "Deliverables\n+ final summary"),
  ]
  for x, y, w, h, text in boxes:
    ax.add_patch(plt.Rectangle((x, y), w, h, fill=True, fc="#e8f1f8", ec="#245b8a", lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11)
  for x1, x2 in ((0.32, 0.36), (0.64, 0.68)):
    ax.annotate("", xy=(x2, 0.73), xytext=(x1, 0.73),
                arrowprops=dict(arrowstyle="->", color="#245b8a", lw=2))
  for x in (0.18, 0.5, 0.82):
    ax.annotate("", xy=(x, 0.44), xytext=(x, 0.62),
                arrowprops=dict(arrowstyle="->", color="#245b8a", lw=2))
  ax.text(0.5, 0.96, "eng-evidence-ledger: task evidence flows through verification before delivery",
          ha="center", fontsize=14, weight="bold")
  fig.savefig(OUT / "architecture.png", dpi=160, bbox_inches="tight")
  plt.close(fig)


def score_cost(runs: list[tuple[str, dict]]) -> None:
  """Scatter of dev score against estimated cost per task."""
  fig, ax = plt.subplots(figsize=(8, 5))
  for label, data in runs:
    x, y = cost_per_task(data), 100 * float(data.get("score", 0))
    ax.scatter(x, y, s=110, label=label)
    ax.annotate(label, (x, y), xytext=(6, 6), textcoords="offset points", fontsize=9)
  ax.set(xlabel="Estimated mean cost per task (USD)", ylabel="Dev score (%)",
         title="Score vs cost on the 29 dev tasks")
  ax.grid(alpha=0.3)
  if len(runs) > 1:
    ax.legend(fontsize=8)
  fig.tight_layout()
  fig.savefig(OUT / "score_vs_cost.png", dpi=160)
  plt.close(fig)


def failures(data: dict) -> None:
  """Breakdown of dev-task outcomes taken verbatim from results.json."""
  rows = data.get("tasks", [])
  cats: dict[str, int] = {}
  for row in rows:
    kind = row.get("kind", "unknown")
    if kind == "ok" and 0 < float(row.get("score", 0)) < 1:
      kind = "partial score"
    elif kind == "ok" and float(row.get("score", 0)) == 0:
      kind = "zero score"
    cats[kind] = cats.get(kind, 0) + 1
  fig, ax = plt.subplots(figsize=(8, 5))
  names = sorted(cats, key=cats.get, reverse=True)
  ax.barh(names[::-1], [cats[k] for k in names[::-1]], color="#c25b48")
  for i, name in enumerate(names[::-1]):
    ax.text(cats[name] + 0.1, i, str(cats[name]), va="center")
  ax.set(xlabel="Dev tasks", title=f"Failure breakdown ({len(rows)} dev tasks)")
  ax.grid(axis="x", alpha=0.3)
  fig.tight_layout()
  fig.savefig(OUT / "failure_breakdown.png", dpi=160)
  plt.close(fig)


def cover(data: dict) -> None:
  """Media Gallery cover image: headline result from the committed run."""
  fig, ax = plt.subplots(figsize=(12, 6.3))
  ax.axis("off")
  fig.patch.set_facecolor("#10263b")
  ax.text(0.5, 0.74, "PLE: Engineering Agents That Show Their Work",
          ha="center", fontsize=26, weight="bold", color="white",
          transform=ax.transAxes)
  ax.text(0.5, 0.52,
          f"{100 * float(data.get('score', 0)):.1f}% dev score  |  "
          f"{len(data.get('tasks', []))} public tasks  |  4 disciplines",
          ha="center", fontsize=15, color="#8ed6ff", transform=ax.transAxes)
  ax.text(0.5, 0.28,
          "Evidence-grounded verification loops for long-horizon engineering work",
          ha="center", fontsize=13, color="#d7e6f2", transform=ax.transAxes)
  fig.savefig(OUT / "cover.png", dpi=160, facecolor=fig.get_facecolor())
  plt.close(fig)


def main() -> None:
  """Builds all figures from the run directories supplied on the command line."""
  if len(sys.argv) < 2:
    raise SystemExit("usage: make_figures.py runs/<run> [label=path ...]")
  runs = [load(arg) for arg in sys.argv[1:]]
  architecture()
  score_cost(runs)
  failures(runs[0][1])
  cover(runs[0][1])
  print(f"wrote {sorted(p.name for p in OUT.glob('*.png'))}")


if __name__ == "__main__":
  main()
