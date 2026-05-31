# Relatório de Sessão — 2026-05-31

## Visão Geral

Esta sessão executou dois componentes do pipeline de validação do IDS hierárquico de forma simultânea:

| Componente | Máquina | Fuso | Início (local) | Fim (local) |
|---|---|---|---|---|
| `attack_orchestrator.py` | PC atacante | BRT (UTC-3) | 17:44:28 | 17:48:27 |
| `network_ids.py` (Fase 1 + 2) | VIM 4 (192.168.100.5) | UTC | 20:44:25 | 20:49:53 |

A diferença de 3 horas entre os timestamps é o offset BRT→UTC. Convertendo: 17:44:28 BRT = 20:44:28 UTC, confirmando que os dois processos estavam em execução sincronizada.

---

## Parte 1 — Attack Orchestrator (PC atacante → VIM 4)

**Arquivo:** `logs/report_20260531_174827.json` / `logs/report_20260531_174827.log`

### Configuração

| Campo | Valor |
|---|---|
| Alvo | `192.168.100.5` (VIM 4) |
| Interface | `eth0` |
| Ataques solicitados | 8 (todos) |
| Ataques executados | 8 |
| Ataques pulados | 0 |
| Duração total | 233,4 s (~3 min 53 s) |

### Sequência e duração dos ataques

| Ataque | Label | Início (BRT) | Fim (BRT) | Duração | Comandos |
|---|---|---|---|---|---|
| `recon` | Recon | 17:44:28 | 17:45:22 | **54,4 s** | nmap SYN, nmap UDP top-100, masscan, nmap -A |
| `dos` | DoS | 17:45:23 | 17:46:54 | **90,6 s** | hping3 SYN flood p80, UDP flood p53, ICMP flood |
| `ddos` | DDoS | 17:46:54 | 17:47:55 | **60,5 s** | hping3 --rand-source SYN p443, UDP p80 |
| `bruteforce` | Brute Force | 17:47:56 | 17:48:13 | **17,1 s** | medusa SSH root, HTTP admin, Telnet root |
| `web` | Web Attacks | 17:48:14 | 17:48:14 | **0,7 s** | nikto, gobuster, curl flood (100 paralelos) |
| `mitm` | MITM | 17:48:15 | 17:48:16 | **0,5 s** | arpspoof eth0 |
| `spoofing` | Spoofing | 17:48:16 | 17:48:19 | **2,7 s** | hping3 -a 1.2.3.4 p80, -a 9.9.9.9 p53, -a 8.8.8.8 ICMP |
| `malware` | Malware (C2/Mirai sim) | 17:48:20 | 17:48:27 | **7,0 s** | nmap p23,2323, nc beacon p4444 (100×), nmap p22 |

### Problema crítico — Captura PCAP com falha total

**Todos os 8 arquivos `.pcap` têm 0 bytes com aviso `pcap file not found`.**

Isso significa que o `tcpdump` invocado pelo orchestrator não capturou nenhum pacote. As métricas de flows, pacotes e bytes são todas zero para cada ataque:

```
total_packets: 0 | total_bytes: 0 | total_flows: 0
```

**Causa provável:** O `tcpdump` requer privilégios de root ou permissão `CAP_NET_RAW`. O processo iniciou e criou o arquivo `.pcap`, mas imediatamente falhou na abertura da interface, produzindo um arquivo vazio que depois foi removido ou nunca escrito. O orchestrator detectou a ausência do arquivo e registrou `"capture_warning": "pcap file not found"`.

**Impacto:** Os ataques *foram executados* (os comandos rodaram e geraram tráfego real na rede — confirmado pelo IDS detectar o tráfego). Apenas a captura local no PC atacante falhou. Não há `.pcap` disponível para análise forense ou augmentação de dataset desta sessão.

---

## Parte 2 — IDS em Tempo Real (VIM 4)

**Arquivo:** `logs/ids_run_20260531_204425.log`

### Configuração do IDS

| Parâmetro | Valor |
|---|---|
| Interface | `eth0` |
| Modelo Fase 1 | `binary_classifier_20260518_130014.pkl` |
| Modelo Fase 2 | `multiclass_classifier_20260518_130014.pkl` |
| Threshold Fase 1 (`P1_THRESHOLD`) | **0.9** |
| Threshold Fase 2 confiança (`P2_CONFIDENCE_THRESH`) | **0.4** |
| Idle timeout (netflower) | 30,0 s |
| Flow timeout | 120,0 s |
| Features de entrada | 55 |
| Classes Fase 1 | `['attack', 'benign']` |
| Classes Fase 2 | `['benign', 'bruteforce', 'ddos', 'dos', 'malware', 'mitm', 'recon', 'spoofing', 'web']` |

### Resultados Gerais

| Métrica | Valor |
|---|---|
| Duração da sessão | **00:05:27** (327 s) |
| Flows processados | **20.097** |
| Alertas gerados (Fase 1) | **11.907** |
| Taxa de detecção binária | **59,2%** |
| Flows de baixa confiança (→Fase 3) | **34** (0,28% dos alertas) |

### Latências de Inferência

| Fase | Média | Máximo |
|---|---|---|
| Fase 1 (binário) | 3,75 ms | 169,60 ms |
| Fase 2 (multiclasse) | 5,27 ms | 17,36 ms |
| E2E (decisão completa) | 14,41 ms | 175,11 ms |

As latências de Fase 1 e Fase 2 são individualmente baixas (sub-10 ms em média). O pico de 169 ms na Fase 1 provavelmente ocorreu durante os primeiros segundos da sessão, quando os modelos ainda estavam sendo carregados em cache pela CPU. O overhead de E2E inclui a serialização do flow e overhead de I/O do log.

### Métricas de Sistema

| Métrica | Média | Máximo |
|---|---|---|
| CPU | **22,3%** | 35,1% |
| RAM | — | **1.112 MB** |
| Rede recebida | 4.293,79 KB/s | — |
| Rede enviada | 1.507,92 KB/s | — |
| Potência RAPL | Não disponível (sem interface RAPL) |

O consumo de CPU ficou abaixo de 36% mesmo sob tráfego intenso de DDoS com source randomizado, confirmando que o pipeline é leve o suficiente para rodar no VIM 4. RAM próxima de 1 GB é dominada pelos dois modelos LightGBM carregados em memória simultaneamente.

### Distribuição dos Alertas por Fase 2

| Classe detectada | Alertas | % do total |
|---|---|---|
| `dos` | 10.637 | **89,3%** |
| `recon` | 961 | **8,1%** |
| `ddos` | 265 | **2,2%** |
| `bruteforce` | 6 | 0,05% |
| `spoofing` | 3 | 0,03% |
| `mitm` | 1 | 0,01% |
| `LOW_CONF→P3` (best: mitm) | 28 | 0,23% |
| `LOW_CONF→P3` (best: spoofing) | 6 | 0,05% |
| **Total** | **11.907** | 100% |

---

## Parte 3 — Correlação Cruzada: Orchestrator × IDS

### Timeline sincronizada (UTC)

| Intervalo UTC | Ataque real | Duração | Alertas esperados | Alertas detectados (P2) | Observação |
|---|---|---|---|---|---|
| 20:44:28 – 20:45:22 | Recon (nmap/masscan) | 54 s | recon | 961 recon | ✅ Detectado corretamente |
| 20:45:23 – 20:46:54 | DoS (hping3 flood) | 91 s | dos | ~10.637 dos | ✅ Detectado (mas domina P2 inteiro) |
| 20:46:54 – 20:47:55 | DDoS (--rand-source) | 61 s | ddos | 265 ddos + fluxo tardio | ⚠️ Subestimado — maioria classificada como `dos` |
| 20:47:56 – 20:48:13 | Brute Force (medusa) | 17 s | bruteforce | 6 bruteforce | ⚠️ Muito baixo — quase todo tráfego classificado como `dos` |
| 20:48:14 | Web (nikto/gobuster/curl) | 0,7 s | web | 0 web | ❌ FN — ataque muito curto para netflower emitir flow |
| 20:48:15 | MITM (arpspoof) | 0,5 s | mitm | 1 mitm | ❌ FN — idem; 1 alerta provavelmente é artefato |
| 20:48:16 – 20:48:19 | Spoofing (hping3 -a) | 2,7 s | spoofing | 3 spoofing | ❌ FN — ataque curto demais |
| 20:48:20 – 20:48:27 | Malware (nc beacon/nmap) | 7 s | malware | 0 malware | ❌ FN — flows emitidos após janela de detecção |
| 20:48:27 – 20:49:21 | (sem ataque ativo) | 54 s | — | ~ddos tardio | ℹ️ Flows DDoS emitidos pelo idle timeout de 30 s |

### Análise dos Padrões Observados

#### 1. Dominância do `dos` na Fase 2 (problema conhecido)

A classe `dos` capturou 89,3% de todos os alertas, incluindo tráfego de `ddos` (hping3 --rand-source) e `bruteforce` (medusa). Este é o mesmo padrão documentado na avaliação de 2026-05-23.

A causa raiz: a classe `dos` tem o maior volume de amostras no banco de dados de treino. Para flows de alta taxa e alta contagem de pacotes — que é exatamente o perfil de `ddos` e `bruteforce` em features de netflow — o modelo de Fase 2 aprende uma fronteira de decisão enviesada em direção ao `dos`. Sem features que distinguem as três classes (diversidade de source para DDoS, contadores de autenticação falhada para brute force), o modelo não tem como diferenciá-las.

**Fix documentado:** rebalancear os pesos de classe na Fase 2, ou adicionar features de diversidade de source IP e de estado de autenticação.

#### 2. Ataques curtos → Falso Negativo sistemático

`web` (0,7 s), `mitm` (0,5 s), `spoofing` (2,7 s) e `malware` (7 s) geraram zero ou quase zero alertas. O motivo é o `idle_timeout=30s` do netflower: um flow só é emitido quando há 30 s de inatividade ou um TCP FIN/RST. Ataques com duração menor que ~10 s terminam antes que o flow seja emitido, e o flow aparece 30 s depois que o ataque já acabou — fora da janela de avaliação.

Esta é uma limitação de arquitetura, não de modelo. A solução seria reduzir o `idle_timeout` (ex: 5–10 s), ao custo de features menos precisas por flow mais curto.

#### 3. Flows DDoS tardios após o fim dos ataques

O último alerta do IDS ocorreu às 20:49:21, enquanto o último ataque (malware) terminou às 20:48:27 UTC. O excedente de ~54 s corresponde exatamente ao `idle_timeout=30 s` do netflower processando os flows DDoS --rand-source que ainda estavam em aberto quando o ataque terminou. Estes flows chegam com `flow_byts_s=0`, `flow_pkts_s=0` e `flow_duration=0` (os pacotes já foram contados no flow principal), mas o modelo ainda os classifica como `ddos` com 98,8% de confiança de Fase 1 e 48,3% de Fase 2 — acima do threshold de 0.4.

#### 4. Recon detectado corretamente

O nmap SYN scan gerou 961 alertas classificados corretamente como `recon` com alta confiança de Fase 2 (acima de 70–89% na maioria dos flows). Isso confirma que o perfil de recon no treino (alta taxa de pacotes, duração ultracurta, syn sem ACK, bwd próximo de zero) generaliza bem para tráfego real de nmap.

#### 5. Baixa confiança (→Fase 3): 34 flows

34 flows tiveram `max(proba) < 0.4` na Fase 2 e foram marcados como `LOW_CONF→P3`:
- 28 com melhor estimativa `mitm`
- 6 com melhor estimativa `spoofing`

Estes são os únicos flows roteados para a Fase 3 (UMAP + HDBSCAN), mas a Fase 3 em tempo real ainda não está implementada em `network_ids.py`. O volume de 34 flows (0,28% dos alertas) é adequado — indica que a Fase 2 é confiante na grande maioria dos casos.

---

## Parte 4 — Comparação com Sessão Anterior (2026-05-23)

| Métrica | 2026-05-23 | 2026-05-31 | Δ |
|---|---|---|---|
| Flows processados | 11.674 | 20.097 | +72% |
| Alertas | 11.670 | 11.907 | +2% |
| Taxa detecção binária | ~100% (atacante único) | 59,2% | ↓ |
| `dos` domina P2 | Sim | Sim | = |
| Recon detectado | 3.075 alertas | 961 alertas | ↓ |
| FN em ataques curtos | Sim | Sim | = |

O aumento de flows (20 k vs 11 k) com quase o mesmo número de alertas sugere que o IDS processou mais tráfego benigno ou tráfego de baixa confiança nesta sessão. A taxa de detecção de 59,2% vs ~100% anteriormente se explica pela diferença na composição do tráfego (esta sessão teve mais tráfego com score próximo ao limiar de 0.9).

---

## Parte 5 — Problemas Identificados e Ações

| Problema | Severidade | Status |
|---|---|---|
| PCAP capture falhou no orchestrator | Alta | A investigar — verificar permissões do tcpdump no PC atacante |
| `dos` domina P2 (DDoS/bruteforce mal classificados) | Alta | Conhecido — requer rebalanceamento ou feature engineering |
| Ataques curtos (<10 s) não detectados em tempo real | Média | Conhecido — reduzir `idle_timeout` ou implementar micro-flow |
| Fase 3 não roteada em tempo real no `network_ids.py` | Média | Pendente de implementação |
| Sem interface RAPL no VIM 4 (potência não disponível) | Baixa | Hardware não suporta; documentar como N/A |

---

## Resumo Executivo

O IDS hierárquico (Fase 1 + Fase 2) foi validado em tempo real no VIM 4 em 2026-05-31. Os ataques foram gerados pelo orchestrator no PC atacante com sucesso de execução, mas com falha na captura PCAP local (todos os arquivos 0 bytes). O tráfego chegou ao VIM 4 e foi detectado pelo IDS.

**O que funcionou bem:**
- Fase 1 (binário) rodou com latência média de 3,75 ms, adequada para edge.
- Recon (nmap) detectado com alta confiança e classificação correta.
- Sistema consumiu ≤35% CPU e ~1 GB RAM sob tráfego intenso.
- 34 flows corretamente encaminhados para Fase 3 (baixa confiança).

**O que precisa ser corrigido:**
- Captura PCAP no orchestrator (verificar permissões do tcpdump).
- Classificação multiclasse na Fase 2 (dominância do `dos` mascara DDoS e bruteforce).
- Detecção de ataques de curta duração (<10 s) que ficam abaixo do idle timeout do netflower.
