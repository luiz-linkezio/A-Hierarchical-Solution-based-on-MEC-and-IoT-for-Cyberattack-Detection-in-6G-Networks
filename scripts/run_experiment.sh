#!/usr/bin/env bash
# run_experiment.sh — Revalidação ao vivo do IDS hierárquico no VIM 4.
# Roda no PC (atacante). Orquestra a VIM 4 (alvo) por SSH. NÃO contém segredos:
# a senha de sudo da VIM 4 vem de $VIM4_PASS. Login na VIM 4 por chave SSH.
#
# Uso:
#   export VIM4_PASS=...            # senha de sudo da VIM 4 (não versionar)
#   sudo -v                          # cacheia a senha de sudo do PC (ataques precisam de root)
#   ./scripts/run_experiment.sh
#
# Flags: --duration N (60) | --baseline N (60) | --skip-calibration | --capture
#        --target IP | --gateway IP | --iface-pc IF | --dry-run
set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
TARGET=192.168.100.5
GATEWAY=192.168.100.1
IFACE_PC=eno1
DURATION=60
BASELINE=60
GAP=120          # ocioso entre ataques: drena o lag de flood (~80s) antes da próxima janela
SLACK=90         # idle_slack da análise: absorve o dreno do flood na janela do próprio flood
SKIP_CALIB=0
CAPTURE=0
DRYRUN=0
SUDO_KEEPALIVE_PID=""
VIM_USER=luiz_henrique
VIM_DIR=/home/${VIM_USER}/Projects/network_ids
SSH_KEY="${HOME}/.ssh/id_ed25519"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

while [ $# -gt 0 ]; do case "$1" in
  --duration) DURATION="$2"; shift 2;;
  --baseline) BASELINE="$2"; shift 2;;
  --gap) GAP="$2"; shift 2;;
  --slack) SLACK="$2"; shift 2;;
  --skip-calibration) SKIP_CALIB=1; shift;;
  --capture) CAPTURE=1; shift;;
  --target) TARGET="$2"; shift 2;;
  --gateway) GATEWAY="$2"; shift 2;;
  --iface-pc) IFACE_PC="$2"; shift 2;;
  --dry-run) DRYRUN=1; shift;;
  *) echo "flag desconhecida: $1"; exit 2;;
esac; done

: "${VIM4_PASS:?Defina VIM4_PASS no ambiente (export VIM4_PASS=...)}"
SSH="ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${VIM_USER}@${TARGET}"
SCP="scp -i ${SSH_KEY} -o StrictHostKeyChecking=no"
# sudo na VIM 4 sem deixar a senha no argv: chega via stdin.
vsudo() {
  if [ "$DRYRUN" = 1 ]; then echo "[DRY] vsudo: $1"; return 0; fi
  $SSH "sudo -S -p '' bash -c \"$1\"" <<<"$VIM4_PASS"
}
TS="$(date +%Y%m%d_%H%M%S)"
say() { echo -e "\n\033[1;36m== $* ==\033[0m"; }

run() { if [ "$DRYRUN" = 1 ]; then echo "[DRY] $*"; else eval "$*"; fi; }

# Liveness via `ps -p` (um login não-root não consegue `kill -0` um processo root).
ids_alive() { $SSH "ps -p $1 >/dev/null 2>&1 && echo ALIVE || echo DEAD"; }

# Encerra o IDS de forma confiável: SIGINT (gracioso → grava [SUMMARY]); se
# resistir, escala para SIGTERM e por fim SIGKILL. Lê o PID para uma variável
# local (evita substituição de comando aninhada no SSH).
stop_ids() {
  local name="$1" ids="$2" pid
  if [ "$DRYRUN" = 1 ]; then echo "[DRY] stop_ids ${name}"; return 0; fi
  pid=$($SSH "cat /tmp/${name}_ids.pid 2>/dev/null" | tr -d '[:space:]')
  [ -z "$pid" ] && pid=$($SSH "pgrep -f ${ids} | head -1" | tr -d '[:space:]')
  if [ -z "$pid" ]; then echo "[!] sem PID do IDS ${name} (já parado?)"; return 0; fi
  echo "encerrando IDS ${name} (PID ${pid}) com SIGINT..."
  vsudo "kill -INT ${pid} 2>/dev/null || true"
  for _ in $(seq 1 15); do
    [ "$(ids_alive "$pid")" = DEAD ] && { echo "IDS ${name} parou graciosamente."; return 0; }
    sleep 1
  done
  echo "[!] IDS ${name} resistiu ao SIGINT — escalando TERM/KILL"
  vsudo "kill -TERM ${pid} 2>/dev/null || true"; sleep 5
  if [ "$(ids_alive "$pid")" = ALIVE ]; then
    vsudo "kill -KILL ${pid} 2>/dev/null; pkill -KILL -f ${ids} 2>/dev/null || true"; sleep 2
  fi
}

# ── Teardown garantido ──────────────────────────────────────────────────────
cleanup() {
  say "TEARDOWN"
  [ -n "$SUDO_KEEPALIVE_PID" ] && kill "$SUDO_KEEPALIVE_PID" 2>/dev/null || true
  if [ "$DRYRUN" = 1 ]; then echo "[DRY] teardown (no-op)"; return 0; fi
  vsudo "kill \$(cat /tmp/http_server.pid 2>/dev/null) 2>/dev/null" || true
  vsudo "pkill -f network_ids.py; pkill -f network_binary_ids.py; pkill -f http.server" || true
  sudo pkill -f 'arpspoof|hping3|medusa|nikto|gobuster|masscan' 2>/dev/null || true
  sudo sysctl -w net.ipv4.ip_forward=0 >/dev/null 2>&1 || true
}
trap cleanup EXIT

# ── 0. sudo do PC (ataques precisam de root) + keep-alive p/ sessão longa ────
if [ "$DRYRUN" = 0 ]; then
  sudo -v || { echo "[!] sudo do PC necessário para os ataques"; exit 1; }
  ( while true; do sudo -n true 2>/dev/null || exit; sleep 50; done ) &
  SUDO_KEEPALIVE_PID=$!
fi

# ── 1. Pré-checagem ─────────────────────────────────────────────────────────
say "PRÉ-CHECAGEM"
if [ "$DRYRUN" = 0 ]; then
  $SSH "echo VIM4_OK" | grep -q VIM4_OK
  vsudo "whoami" | grep -q root
fi
for t in nmap masscan hping3 medusa nikto gobuster curl arpspoof nc; do
  command -v "$t" >/dev/null || { echo "[!] faltando no PC: $t"; exit 1; }
done

# ── 2. Deploy dos scripts/modelos/constants para a VIM 4 ────────────────────
say "DEPLOY → VIM 4"
run "$SCP \"$ROOT/scripts/network_ids.py\" \"$ROOT/scripts/network_binary_ids.py\" \"$ROOT/scripts/calibrate_power.py\" ${VIM_USER}@${TARGET}:${VIM_DIR}/"
run "$SCP -r \"$ROOT/constants\" ${VIM_USER}@${TARGET}:${VIM_DIR}/"
run "$SCP \"$ROOT/models/binary_classifier_20260601_001154.pkl\" \"$ROOT/models/multiclass_classifier_20260601_001154.pkl\" ${VIM_USER}@${TARGET}:${VIM_DIR}/models/"

# ── 3. Calibração de energia (1x) ───────────────────────────────────────────
if [ "$SKIP_CALIB" = 0 ]; then
  say "CALIBRAÇÃO DE ENERGIA (VIM 4)"
  run "$SSH \"cd ${VIM_DIR} && venv/bin/python3 calibrate_power.py --out constants/power_model_vim4.json --seconds 60\""
  run "$SCP ${VIM_USER}@${TARGET}:${VIM_DIR}/constants/power_model_vim4.json \"$ROOT/constants/power_model_vim4.json\""
fi

# ── 4. Servidor HTTP real (suporte ao ataque web) ───────────────────────────
say "SETUP http.server :80 na VIM 4"
vsudo "nohup python3 -m http.server 80 >/tmp/http_server.log 2>&1 & echo \\\$! >/tmp/http_server.pid"
if [ "$DRYRUN" = 0 ]; then
  sleep 1
  curl -s -o /dev/null -w "http.server → %{http_code}\n" "http://${TARGET}/" || true
fi

# ── Função de sessão ────────────────────────────────────────────────────────
# $1 = nome da sessão (a|b) ; $2 = script IDS ; $3 = glob do log
run_session() {
  local name="$1" ids="$2" logglob="$3"
  local outdir="logs/session_${name}_${TS}"
  say "SESSÃO ${name^^} — ${ids}"
  run "mkdir -p \"$ROOT/${outdir}\""
  # inicia o IDS na VIM 4 (sudo, background, venv)
  vsudo "cd ${VIM_DIR} && rm -f logs/${logglob} 2>/dev/null; nohup venv/bin/python3 ${ids} >/tmp/${name}_stdout.log 2>&1 & echo \\\$! >/tmp/${name}_ids.pid"
  if [ "$DRYRUN" = 0 ]; then
    sleep 3
    $SSH "ps -p \$(cat /tmp/${name}_ids.pid) -o pid= >/dev/null && echo IDS_UP" | grep -q IDS_UP
  fi
  echo "baseline idle ${BASELINE}s..."; [ "$DRYRUN" = 0 ] && sleep "$BASELINE"
  local capflag=""; [ "$CAPTURE" = 1 ] && capflag="--capture"
  run "sudo VIM4_PASS=\"$VIM4_PASS\" python3 -u \"$ROOT/scripts/attack_generator.py\" \
        --target ${TARGET} --iface ${IFACE_PC} --duration ${DURATION} --gap ${GAP} --gateway ${GATEWAY} \
        --vim-ssh \"ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${VIM_USER}@${TARGET}\" \
        --output \"$ROOT/${outdir}/\" ${capflag}"
  echo "baseline idle ${BASELINE}s..."; [ "$DRYRUN" = 0 ] && sleep "$BASELINE"
  # encerra o IDS de forma confiável (gracioso → grava [SUMMARY]; escala se preciso)
  stop_ids "$name" "$ids"
  run "$SCP \"${VIM_USER}@${TARGET}:${VIM_DIR}/logs/${logglob}\" \"$ROOT/${outdir}/\""
}

# ── 5/6. Sessões (outdir é determinístico: logs/session_<name>_<TS>) ─────────
DIR_A="logs/session_a_${TS}"
DIR_B="logs/session_b_${TS}"
run_session a network_binary_ids.py 'binary_ids_run_*.log'
run_session b network_ids.py 'ids_run_*.log'

# ── 7. Teardown explícito (o trap também roda) ──────────────────────────────
cleanup; trap - EXIT

# ── 8. Análise ──────────────────────────────────────────────────────────────
say "ANÁLISE"
mkdir -p "$ROOT/results"
if [ "$DRYRUN" = 1 ]; then
  A_LOG="$ROOT/${DIR_A}/binary_ids_run_<ts>.log"; A_REP="$ROOT/${DIR_A}/report_<ts>.json"
  B_LOG="$ROOT/${DIR_B}/ids_run_<ts>.log";        B_REP="$ROOT/${DIR_B}/report_<ts>.json"
else
  A_LOG=$(ls -t "$ROOT/${DIR_A}"/binary_ids_run_*.log | head -1)
  A_REP=$(ls -t "$ROOT/${DIR_A}"/report_*.json | head -1)
  B_LOG=$(ls -t "$ROOT/${DIR_B}"/ids_run_*.log | head -1)
  B_REP=$(ls -t "$ROOT/${DIR_B}"/report_*.json | head -1)
fi
run "python3 \"$ROOT/scripts/ids_metrics.py\" --ids \"$A_LOG\" --report \"$A_REP\" --mode binary --label-map ddos=dos --idle-slack ${SLACK} --output \"$ROOT/results/session_a_metrics_${TS}.json\""
run "python3 \"$ROOT/scripts/ids_metrics.py\" --ids \"$B_LOG\" --report \"$B_REP\" --mode multiclass --label-map ddos=dos --idle-slack ${SLACK} --output \"$ROOT/results/session_b_metrics_${TS}.json\""

say "FEITO — resultados em results/session_{a,b}_metrics_${TS}.json"
