#!/bin/bash

# =============================================================================
# capturar_trafego_pessoal.sh
# =============================================================================
#
# PROPÓSITO:
#   Capturar o tráfego de rede gerado pelo uso pessoal e real do computador
#   (navegação, streaming, downloads, redes sociais, etc.) e salvá-lo em um
#   arquivo .pcap para ser usado como dado benigno no treinamento de um IDS.
#
# MOTIVAÇÃO:
#   Em vez de simular tráfego benigno com scripts, este script captura o
#   tráfego 100% humano e real do usuário. Isso produz amostras muito mais
#   fidedignas do comportamento legítimo, resolvendo o problema de
#   "distribution shift" identificado no IDS: o modelo não reconhecia como
#   benigno o tráfego gerado na VIM 4 porque os datasets públicos
#   (CICIDS2017, NSL-KDD, etc.) não refletem o perfil de uso real do ambiente.
#
# SISTEMA OPERACIONAL: Arch Linux
#
# DEPENDÊNCIAS:
#   - tcpdump  → sudo pacman -S tcpdump
#   - iproute2 → sudo pacman -S iproute2  (já incluso na maioria dos sistemas)
#
# COMO USAR:
#   1. Instale as dependências se necessário:
#        sudo pacman -S tcpdump
#
#   2. Execute o script como root:
#        chmod +x capturar_trafego_pessoal.sh
#        sudo ./capturar_trafego_pessoal.sh
#
#   3. Use o computador normalmente: navegue, assista vídeos, baixe arquivos,
#      acesse redes sociais, etc. Tudo será capturado automaticamente.
#
#   4. Pressione Ctrl+C para encerrar. O caminho do .pcap será exibido.
#
#   5. Transfira o .pcap para a VIM 4 e extraia as features com
#      CICFlowMeter ou nDPI, usando as mesmas features do dataset original.
#
#   6. Rotule os dados como "BENIGN" e mescle com o dataset original
#      antes de re-treinar o modelo do IDS.
#
# OBSERVAÇÕES:
#   - Cada sessão gera um arquivo separado com timestamp no nome,
#     então você pode acumular várias sessões ao longo dos dias.
#   - Tente variar o tipo de uso durante a captura: navegação, YouTube,
#     Spotify, downloads, GitHub, etc. Quanto mais variado, melhor.
#   - Evite fazer coisas incomuns durante a captura (VPN, tor, port scan,
#     etc.) para não contaminar os dados benignos.
#   - Para transferir o .pcap para a VIM 4:
#        scp /tmp/pessoal_<timestamp>.pcap usuario@<ip-vim4>:/destino/
#
# =============================================================================

# =============================================================================
# VERIFICAÇÕES INICIAIS
# =============================================================================

# Verifica root
if [[ $EUID -ne 0 ]]; then
  echo "[!] Execute como root: sudo ./capturar_trafego_pessoal.sh"
  exit 1
fi

# Verifica dependência do tcpdump
if ! command -v tcpdump &>/dev/null; then
  echo "[!] tcpdump não encontrado. Instale com: sudo pacman -S tcpdump"
  exit 1
fi

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# Detecta interface de rede ativa automaticamente
IFACE=$(ip route get 8.8.8.8 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="dev") print $(i+1)}' | head -1)
if [[ -z "$IFACE" ]]; then
  echo "[!] Não foi possível detectar a interface de rede ativa."
  echo "[!] Defina manualmente editando: IFACE=eth0"
  exit 1
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PCAP_FILE="/tmp/pessoal_${TIMESTAMP}.pcap"
LOG_FILE="/tmp/pessoal_${TIMESTAMP}.log"
INICIO=$(date +%s)

# =============================================================================
# CAPTURA
# =============================================================================

# Encerramento limpo ao Ctrl+C
cleanup() {
  local fim=$(date +%s)
  local duracao=$((fim - INICIO))
  local minutos=$((duracao / 60))
  local segundos=$((duracao % 60))

  echo ""
  echo "┌─────────────────────────────────────────┐"
  echo "│          CAPTURA ENCERRADA               │"
  echo "├─────────────────────────────────────────┤"
  printf  "│ Duração   : %dm %ds                      \n" $minutos $segundos
  echo   "│ PCAP      : $PCAP_FILE"
  echo   "│ Log       : $LOG_FILE"
  echo   "│ Interface : $IFACE"
  echo "├─────────────────────────────────────────┤"
  echo "│ Próximos passos:                         │"
  echo "│  1. Extrair features com CICFlowMeter    │"
  echo "│  2. Rotular como BENIGN                  │"
  echo "│  3. Mesclar com dataset original         │"
  echo "│  4. Re-treinar o modelo do IDS           │"
  echo "└─────────────────────────────────────────┘"

  kill "$TCPDUMP_PID" 2>/dev/null
  wait "$TCPDUMP_PID" 2>/dev/null
  exit 0
}
trap cleanup SIGINT SIGTERM

# Inicia tcpdump em background
# Flags:
#   -i $IFACE     → interface detectada
#   -w $PCAP_FILE → salva em arquivo .pcap
#   -n            → não resolve nomes (mais rápido, menos ruído)
#   -s 0          → captura pacote inteiro (sem truncar)
#   -q            → saída quieta no terminal
tcpdump -i "$IFACE" -w "$PCAP_FILE" -n -s 0 -q 2>/dev/null &
TCPDUMP_PID=$!

# Registra metadados da sessão no log
{
  echo "Sessão iniciada  : $(date)"
  echo "Interface        : $IFACE"
  echo "Arquivo PCAP     : $PCAP_FILE"
  echo "PID tcpdump      : $TCPDUMP_PID"
  echo "Usuário real     : ${SUDO_USER:-root}"
  echo "Hostname         : $(hostname)"
  echo "IP local         : $(ip -4 addr show "$IFACE" | awk '/inet / {print $2}' | head -1)"
} > "$LOG_FILE"

# =============================================================================
# FEEDBACK VISUAL — atualiza estatísticas a cada 10s enquanto captura
# =============================================================================

echo ""
echo "[✓] Captura iniciada na interface: $IFACE"
echo "[✓] Salvando em: $PCAP_FILE"
echo "[*] Use o computador normalmente. Pressione Ctrl+C para encerrar."
echo ""

while kill -0 "$TCPDUMP_PID" 2>/dev/null; do
  local_time=$(date +"%H:%M:%S")
  duracao_atual=$(( $(date +%s) - INICIO ))
  min=$((duracao_atual / 60))
  seg=$((duracao_atual % 60))

  # Tamanho atual do pcap
  pcap_size=$(du -sh "$PCAP_FILE" 2>/dev/null | cut -f1)

  printf "\r[%s] ⏱ %02dm %02ds | 📦 %s capturados   " \
    "$local_time" "$min" "$seg" "$pcap_size"

  sleep 10
done