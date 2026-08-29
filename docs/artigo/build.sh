#!/usr/bin/env sh
# build.sh — Compila um .tex desta pasta com latexmk, deixando TODOS os artefatos
# (.aux, .log, .bbl, .blg, .pdf, ...) em build/, que é ignorado pelo git.
#
# Uso:
#   docs/artigo/build.sh              # -> docs/artigo/build/main.pdf
#   docs/artigo/build.sh main_short   # -> docs/artigo/build/main_short.pdf
#
# Usa o latexmk local se existir; caso contrário roda a imagem Docker
# texlive/texlive:latest (sobrescreva com TEXLIVE_IMAGE=...). Os arquivos
# gerados pertencem ao usuário atual, não ao root.
set -eu

cd "$(dirname "$0")"
target="${1:-main}"
target="${target%.tex}"
image="${TEXLIVE_IMAGE:-texlive/texlive:latest}"

[ -f "$target.tex" ] || { echo "erro: $target.tex não existe em $PWD" >&2; exit 1; }
mkdir -p build

if command -v latexmk >/dev/null 2>&1; then
    latexmk -pdf -interaction=nonstopmode -outdir=build "$target.tex"
else
    docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
        -v "$PWD":/work -w /work "$image" \
        latexmk -pdf -interaction=nonstopmode -outdir=build "$target.tex"
fi

echo "OK: $PWD/build/$target.pdf"
