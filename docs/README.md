# `docs/`

Paper source, experiment write-ups and generated reports of the project. Nothing
here is needed to run the code — see the root [`README.md`](../README.md) for the
pipeline, scripts and setup.

| Path | What it holds |
|------|---------------|
| [`artigo/`](artigo/) | LaTeX source of the paper (SBC template): `main.tex`, `artigo.bib`, `sbc.bst`, `sbc-template.sty` and the `build.sh` compile script. |
| [`relatorio_ic/`](relatorio_ic/) | LaTeX source of the PIBIC/UFPE final report (Propesqi model): `relatorio_final_pibic.tex`, `referencias.bib`, `sbc.bst`, the UFPE/Propesqi logo and its own `build.sh`. |
| [`experimentos/`](experimentos/) | Methodology and results of each live testbed session on the VIM 4 (one `YYYY-MM-DD-*.md` per session). |
| [`results/`](results/) | Reports written by `notebooks/training.ipynb` (`training_<timestamp>.md`), IDS session reports, and their figures under `results/images/`. |
| [`dataset/`](dataset/) | Reference lists about the training data: the final feature set (`features_report.txt`, written by `training.ipynb`) and the label taxonomy (`labels_list.txt`). |
| [`testbed/`](testbed/) | Manual command reference to reproduce each attack class against the VIM 4 (`attack_testing.md`). `scripts/attack_generator.py` automates the same attacks. |

## Compiling the paper

```sh
docs/artigo/build.sh              # -> docs/artigo/build/main.pdf
docs/artigo/build.sh main_short   # any other .tex in docs/artigo/
docs/relatorio_ic/build.sh        # -> docs/relatorio_ic/build/relatorio_final_pibic.pdf
```

The script uses a local `latexmk` when available and falls back to the
`texlive/texlive:latest` Docker image otherwise (`TEXLIVE_IMAGE=...` overrides it).
Everything they produce (`.pdf`, `.aux`, `.log`, `.bbl`, …) goes to the
respective `build/` folder (`docs/artigo/build/`, `docs/relatorio_ic/build/`),
which is git-ignored — never commit build output.

## Local-only material

Some things may exist in this folder on a working copy but are ignored by git:
`Template_SBC/` (the original SBC template download), `superpowers/` (design specs
and plans) and `netflower_README.md` (README of the netflower tool, kept for
reference).
