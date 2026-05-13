#!/bin/bash

# =============================================================================
# gerar_trafego_benigno.sh
# =============================================================================
#
# PROPÓSITO:
#   Gerar tráfego de rede benigno e realista a partir de uma máquina VIM 4,
#   para ser capturado via tcpdump e usado como dado de treinamento em um
#   sistema de detecção de intrusão (IDS) baseado em Machine Learning.
#
# MOTIVAÇÃO:
#   Durante o desenvolvimento de um IDS, foi identificado um problema crítico:
#   o modelo classificava como malicioso todo tráfego gerado na VIM 4, mesmo
#   ações completamente normais como acessar o Google ou baixar arquivos comuns.
#
#   A causa raiz é o chamado "distribution shift" (ou concept drift):
#   os datasets públicos usados no treinamento (ex: CICIDS2017, NSL-KDD)
#   foram gerados em ambientes controlados com perfis de uso muito diferentes
#   do ambiente real da VIM 4. Por isso, o tráfego legítimo local não se
#   parecia com o tráfego "benigno" que o modelo aprendeu — e acabava sendo
#   classificado como ameaça.
#
#   A solução adotada foi capturar tráfego benigno real diretamente da VIM 4
#   (navegação, DNS, ping, downloads, streaming), rotulá-lo como BENIGN,
#   e mesclar com o dataset original para re-treinar o modelo. Isso faz com
#   que o IDS aprenda o que é "normal" especificamente neste ambiente.
#
# COMO USAR:
#   1. Execute o script como root (necessário para o tcpdump):
#        chmod +x gerar_trafego_benigno.sh
#        sudo ./gerar_trafego_benigno.sh
#
#   2. O tcpdump será iniciado automaticamente em background e o
#      arquivo .pcap será salvo em: /tmp/benigno_vim4_<timestamp>.pcap
#
#   3. Deixe rodar por pelo menos 30-60 minutos para volume suficiente.
#
#   4. Ao pressionar Ctrl+C, o tcpdump é encerrado automaticamente
#      e o caminho do .pcap é exibido.
#
#   5. Extraia as features do .pcap com CICFlowMeter ou nDPI,
#      usando as mesmas features do dataset original.
#
#   6. Rotule os dados extraídos como "BENIGN" e mescle com o dataset
#      original antes de re-treinar o modelo.
#
# OBSERVAÇÕES:
#   - O script detecta automaticamente a interface de rede ativa.
#   - O sleep aleatório entre requisições é intencional: timing entre
#     pacotes é uma feature relevante para modelos de IDS, e intervalos
#     regulares demais podem parecer tráfego automatizado/suspeito.
#   - Varie os horários de captura (manhã, tarde, noite) para cobrir
#     diferentes padrões de uso.
#   - O User-Agent realista ajuda a simular navegação de browser de verdade.
#
# =============================================================================

SITES=(
  # Buscadores / geral
  "https://www.google.com"
  "https://www.bing.com"
  "https://www.wikipedia.org"

  # Redes sociais
  "https://www.facebook.com"
  "https://www.instagram.com"
  "https://www.twitter.com"
  "https://www.linkedin.com"
  "https://www.reddit.com"
  "https://www.tiktok.com"
  "https://www.pinterest.com"

  # Streaming / entretenimento
  "https://www.youtube.com"
  "https://www.netflix.com"
  "https://www.twitch.tv"
  "https://open.spotify.com"

  # Tecnologia
  "https://www.github.com"
  "https://stackoverflow.com"
  "https://developer.mozilla.org"
  "https://www.cloudflare.com"

  # E-commerce
  "https://www.amazon.com"
  "https://www.shopee.com.br"
  "https://www.americanas.com.br"
  "https://www.mercadolivre.com.br"

  # Notícias BR
  "https://g1.globo.com"
  "https://www.uol.com.br"
  "https://www.r7.com"
  "https://www.globo.com"
  "https://www.terra.com.br"

  # Bancos / Finanças BR
  "https://www.nubank.com.br"
  "https://www.bb.com.br"
  "https://www.itau.com.br"
  "https://www.bradesco.com.br"
)

PING_HOSTS=("8.8.8.8" "1.1.1.1" "8.8.4.4" "9.9.9.9" "208.67.222.222")

UA_LIST=(
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0 Safari/537.36"
  "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
  "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"
  "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/113.0 Firefox/113.0"
)

# Sleep com distribuição mais humana (base + jitter fracionado)
human_sleep() {
  local base=$((RANDOM % 8 + 2))
  local jitter=$(awk "BEGIN {printf \"%.1f\", ($RANDOM / 32767) * 4}")
  sleep $(awk "BEGIN {printf \"%.1f\", $base + $jitter}")
}

# 10% de chance de pausa longa (usuário foi tomar café, atender chamada, etc.)
maybe_long_pause() {
  if (( RANDOM % 10 == 0 )); then
    local pausa=$((RANDOM % 120 + 30))
    echo "[~] Pausa longa de ${pausa}s (simula inatividade)"
    sleep $pausa
  fi
}

acesso_web() {
  local site=${SITES[$RANDOM % ${#SITES[@]}]}
  local ua=${UA_LIST[$RANDOM % ${#UA_LIST[@]}]}
  local n_requests=$((RANDOM % 4 + 1))  # 1–4 requests (simula múltiplas abas/recursos)
  echo "[+] Web: $site ($n_requests req)"
  for _ in $(seq 1 $n_requests); do
    curl -s -A "$ua" --max-time 10 -L "$site" > /dev/null
    sleep $(awk "BEGIN {printf \"%.1f\", ($RANDOM / 32767) * 2}")
  done
}

consulta_dns() {
  local site=${SITES[$RANDOM % ${#SITES[@]}]}
  local dominio=${site#https://}
  local dominio=${dominio#http://}
  echo "[+] DNS: $dominio"
  dig "$dominio" > /dev/null 2>&1
}

fazer_ping() {
  local host=${PING_HOSTS[$RANDOM % ${#PING_HOSTS[@]}]}
  local count=$((RANDOM % 5 + 2))
  echo "[+] Ping $host ($count pacotes)"
  ping -c $count "$host" > /dev/null 2>&1
}

download_pequeno() {
  echo "[+] Download pequeno"
  curl -s --max-time 15 \
    "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg" \
    -o /tmp/benigno_dl_$$.tmp && rm -f /tmp/benigno_dl_$$.tmp
}

# Pesos: web é bem mais frequente que as demais ações
ACOES=("web" "web" "web" "web" "dns" "dns" "ping" "download")

# =============================================================================
# TCPDUMP — captura automática em background
# =============================================================================

# Verifica se está rodando como root
if [[ $EUID -ne 0 ]]; then
  echo "[!] Execute como root: sudo ./gerar_trafego_benigno.sh"
  exit 1
fi

# Detecta interface de rede ativa automaticamente
IFACE=$(ip route get 8.8.8.8 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="dev") print $(i+1)}' | head -1)
if [[ -z "$IFACE" ]]; then
  echo "[!] Não foi possível detectar a interface de rede. Defina manualmente: IFACE=eth0"
  exit 1
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PCAP_FILE="/tmp/benigno_vim4_${TIMESTAMP}.pcap"

# Inicia tcpdump em background
tcpdump -i "$IFACE" -w "$PCAP_FILE" -q 2>/dev/null &
TCPDUMP_PID=$!

echo "[*] Interface detectada: $IFACE"
echo "[*] Capturando para: $PCAP_FILE (PID tcpdump: $TCPDUMP_PID)"

# Garante que o tcpdump é encerrado ao sair (Ctrl+C ou erro)
cleanup() {
  echo ""
  echo "[*] Encerrando captura..."
  kill "$TCPDUMP_PID" 2>/dev/null
  wait "$TCPDUMP_PID" 2>/dev/null
  echo "[✓] PCAP salvo em: $PCAP_FILE"
  echo "[*] Próximo passo: extraia as features com CICFlowMeter ou nDPI."
  exit 0
}
trap cleanup SIGINT SIGTERM

# =============================================================================

echo "[*] Iniciando geração de tráfego benigno ($(date))..."
echo "[*] Total de sites na lista: ${#SITES[@]}"
echo "[*] Pressione Ctrl+C para encerrar."
echo ""

while true; do
  ACAO=${ACOES[$RANDOM % ${#ACOES[@]}]}
  case $ACAO in
    "web")      acesso_web ;;
    "dns")      consulta_dns ;;
    "ping")     fazer_ping ;;
    "download") download_pequeno ;;
  esac
  human_sleep
  maybe_long_pause
done