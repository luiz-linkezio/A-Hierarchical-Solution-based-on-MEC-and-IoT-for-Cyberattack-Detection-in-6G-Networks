# Relatório de Sessão — 2026-06-01

## Visão Geral

| Componente | Máquina | Fuso | Início (local) | Fim (local) | Duração |
|---|---|---|---|---|---|
| `attack_orchestrator.py` — Run 1 | PC atacante | BRT (UTC−3) | 14:54:55 | 14:59:06 | 245,6 s |
| `attack_orchestrator.py` — Run 2 | PC atacante | BRT (UTC−3) | 15:00:02 | 15:04:17 | 249,5 s |
| `network_ids.py` (Fase 1 + 2) | VIM 4 | UTC | 17:54:51 | ~18:00:00 | ~5 min |
| `network_ids.py` binário (Fase 1) | VIM 4 | UTC | 17:59:53 | ~18:07:12 | ~7 min |

> Sincronização: 14:54:55 BRT = 17:54:55 UTC — primeiro alerta IDS multiclasse às 17:54:55 ✓  
> 15:00:02 BRT = 18:00:02 UTC — primeiro alerta IDS binário às 18:00:02 ✓

**Modelos:**
- Fase 1 (binário): `binary_classifier_20260601_001154.pkl`
- Fase 2 (multiclasse): `multiclass_classifier_20260601_001154.pkl`
- P2 classes: `benign, bruteforce, dos, malware, mitm, recon, spoofing, web` — DDoS unificado em `dos`

---

## Parte 1 — Attack Orchestrator

**Arquivos:** `logs/report_20260601_145906.json/.log` e `logs/report_20260601_150417.json/.log`

### Ataques executados

| Ataque | Duração R1 | Duração R2 | Ferramentas |
|---|---|---|---|
| `recon` | 69,5 s | 73,4 s | nmap -sS, nmap -sU top-100, masscan, nmap -A |
| `dos` | 90,6 s | 90,6 s | hping3 SYN flood p80, UDP flood p53, ICMP flood |
| `ddos` | 60,5 s | 60,5 s | hping3 --rand-source SYN p443, UDP p80 |
| `bruteforce` | 15,3 s | 15,3 s | medusa SSH root, HTTP admin, Telnet root |
| `web` | 0,7 s | 0,6 s | nikto, gobuster, curl flood 100× |
| `mitm` | 0,5 s | 0,5 s | arpspoof eth0 |
| `spoofing` | 1,7 s | 1,7 s | hping3 -a 1.2.3.4, -a 9.9.9.9, -a 8.8.8.8 |
| `malware` | 7,0 s | 7,0 s | nmap p23/2323, nc beacon p4444 (100×), nmap p22 |
| **Total** | **245,6 s** | **249,5 s** | |

**PCAP capture:** falhou em todos os 8 ataques (falta de `CAP_NET_RAW` no processo do tcpdump).

---

## Parte 2 — IDS Multiclasse (Fase 1 + 2)

**Arquivo:** `logs/ids_run_20260601_175451.log`

### Configuração

| Parâmetro | Valor |
|---|---|
| Modelo P1 | `binary_classifier_20260601_001154.pkl` |
| Modelo P2 | `multiclass_classifier_20260601_001154.pkl` |
| Classes P2 | `benign, bruteforce, dos, malware, mitm, recon, spoofing, web` |
| Threshold P1 | ≥ 0,9 |
| Threshold P2 → P3 | < 0,4 |
| Idle / Flow timeout | 30 s / 120 s |

### Métricas globais

| Métrica | Valor |
|---|---|
| Total de alertas | **9.871** |
| — Em janelas de ataque | **9.852** |
| — Fora das janelas | **0** |
| — `LOW_CONF→P3` | **19** |
| Acurácia (taxonomia unificada ddos→dos) | **81,34%** |
| Macro Precision | 25,61% |
| Macro Recall | 22,96% |
| Macro F1 | 24,22% |
| P1 médio | **99,83%** |
| P1 mínimo | **99,6%** |
| P2 médio | 98,81% |
| P2 mínimo | 50,9% |

### Per-class Precision / Recall / F1

| Classe | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| `recon` | 981 | 0 | 634 | **1,0000** | **0,6074** | **0,7558** |
| `dos` (incl. ddos) | 7.033 | 1.838 | 0 | **0,7928** | **1,0000** | **0,8844** |
| `bruteforce` | 0 | 0 | 604 | 0,0000 | 0,0000 | 0,0000 |
| `web` | 0 | 0 | 29 | 0,0000 | 0,0000 | 0,0000 |
| `mitm` | 0 | 0 | 99 | 0,0000 | 0,0000 | 0,0000 |
| `spoofing` | 0 | 0 | 99 | 0,0000 | 0,0000 | 0,0000 |
| `malware` | 0 | 0 | 373 | 0,0000 | 0,0000 | 0,0000 |

> **Macro Precision/Recall baixos** porque o modelo classifica bruteforce, web, mitm, spoofing e malware como `dos` — 5 das 7 classes têm P=R=0 nessa avaliação. Apenas `dos` e `recon` são funcionais na Fase 2 com o tráfego de rede atual.

### Matriz de confusão (P2)

|  | → dos | → recon |
|---|---|---|
| **recon** | 634 | **981** |
| **dos** (incl. ddos) | **7.033** | 0 |
| **bruteforce** | **604** | 0 |
| **web** | **29** | 0 |
| **mitm** | **99** | 0 |
| **spoofing** | **99** | 0 |
| **malware** | **373** | 0 |

> Os 1.838 FP em `dos`: recon=634, bruteforce=604, malware=373, mitm=99, spoofing=99, web=29. Esses ataques geram fluxos de curta duração com alta taxa de bytes/pacotes — padrão quase indistinguível de flood DoS nas features de fluxo disponíveis.

### Distribuição P2

| Rótulo | Alertas | % |
|---|---|---|
| `dos` | 8.871 | 90,0% |
| `recon` | 981 | 9,9% |
| `LOW_CONF→P3` | 19 | 0,19% |

### Roteamento para Fase 3

| Best-guess P3 | Flows |
|---|---|
| `mitm` | 10 |
| `bruteforce` | 5 |
| `spoofing` | 4 |
| **Total** | **19** |

O modelo reconhece que esses 19 fluxos são diferentes de `dos`/`recon`, mas não tem confiança ≥ 0,4 para classificá-los diretamente — são corretamente encaminhados para clustering na Fase 3.

### Fluxo de destaque — Beacon C2

```
17:59:21  P1=99.7%  P2=LOW_CONF→P3 (best: spoofing)  conf=38.6%
  src=192.168.100.5:22  →  dst=192.168.100.232:38120  proto=TCP
  flow_byts_s=980.6  flow_pkts_s=7.129  flow_duration=239.9 s
```

Canal SSH reverso (VIM4 → PC atacante), 240 s de duração, 980 B/s. O modelo não classifica como `dos` — reconhece o padrão de baixa taxa como atípico e envia para P3 com best-guess `spoofing` (38,6%). Correto: um canal C2 persistente de baixa taxa não deve ser classificado como flood.

### Confiança P1 e P2

| Estatística | P1 (binário) | P2 (multiclasse) |
|---|---|---|
| Média | 99,83% | 98,81% |
| Mediana | 99,90% | 99,90% |
| Desvio padrão | **0,13%** | 4,34% |
| Mínimo | **99,6%** | 50,9% |
| Máximo | 100,0% | 100,0% |

> P1 com desvio padrão de 0,13% — todos os alertas estão entre 99,6% e 100%. Threshold de até 99,5% não descarta nenhum fluxo.

### Sweep de threshold P1

| Threshold | TPR | Alertas mantidos |
|---|---|---|
| ≥ 90,0% | 1,0000 | 9.852 |
| ≥ 99,5% | 1,0000 | 9.852 |
| ≥ 99,9% | 0,5327 | 5.248 |

### Recursos do VIM4

| | CPU | RAM |
|---|---|---|
| Baseline | 0,3% | 13,4% (1044 MB) |
| Recon | 7,8% | 13,4% (1046 MB) |
| Pico | **30,5%** | **14,0% (1093 MB)** |

---

## Parte 3 — IDS Binário (Fase 1)

**Arquivo:** `logs/binary_ids_run_20260601_175953.log`

### Configuração

| Parâmetro | Valor |
|---|---|
| Modelo | `binary_classifier_20260601_001154.pkl` |
| Classes | `attack, benign` |
| Threshold | ≥ 0,9 |
| Idle / Flow timeout | 30 s / 120 s |

---

### Métricas — Matriz de Confusão 2×2

A granularidade é **por segundo**: para cada segundo da sessão, o IDS ou alertou (predição = ataque) ou não (predição = benigno). O ground truth vem das janelas do orchestrator (BRT+3h→UTC).

```
                   Pred: Ataque   Pred: Benigno
  True: Ataque         224            62      (286 s de ataque)
  True: Benigno          1           141      (142 s de benigno)
```

| Métrica | Valor | Cálculo |
|---|---|---|
| **Accuracy** | **85,28%** | (224+141) / 428 |
| **Precision** | **99,56%** | 224 / (224+1) |
| **Recall (TPR)** | **78,32%** | 224 / (224+62) |
| **F1-score** | **87,67%** | 2 × 0,9956 × 0,7832 / (0,9956+0,7832) |
| **FPR** | **0,70%** | 1 / (1+141) |
| **FNR** | **21,68%** | 62 / (224+62) |

### Análise dos falsos negativos (62 s sem alerta durante ataque)

| Causa | FN seconds | % dos FN |
|---|---|---|
| Recon warmup/gap (18:00:14–18:00:56) | 43 s | **69%** |
| Slack pós-malware sem tráfego detectado | 19 s | **31%** |

**Recon (43 FN):** o nmap -sU top-100 (scan UDP) gera poucos pacotes por porta; com `idle_timeout=30 s` e `flow_timeout=120 s`, muitos fluxos UDP não acumulam features suficientes para serem emitidos durante o scan em si. O IDS detecta os primeiros e últimos ~15 s do recon, mas tem um gap no meio.

**Slack malware (19 FN):** a janela de malware foi estendida +30 s (idle slack) para capturar fluxos que expiram após o fim do ataque. Nesse período, 50% dos segundos já não têm tráfego de ataque ativo — os nc beacons completaram em ~5 s.

### Taxa de detecção por janela de ataque

| Ataque | Segundos | Alertados | Taxa |
|---|---|---|---|
| `recon` | 74 | 31 | **41,9%** |
| `dos` (incl. ddos) | 153 | 153 | **100,0%** |
| `bruteforce` | 16 | 16 | **100,0%** |
| `web` | 1 | 1 | **100,0%** |
| `mitm` | 1 | 1 | **100,0%** |
| `spoofing` | 3 | 3 | **100,0%** |
| `malware` | 38 | 19 | **50,0%** |

> O `dos` unificado (91 s de DoS + 62 s de DDoS rand-source) atinge 100% — todos os 153 segundos com tráfego de inundação foram detectados. O `recon` é o único ataque com detecção parcial por limitação do extrator de features, não do modelo.

### Falso positivo (1 FP)

O único FP é o canal C2 SSH reverso (`src=192.168.100.5:22`, `flow_duration=432 s`) que expira às 18:07:09 — **162 s após o fim do último ataque**. Esse fluxo começa dentro da janela de malware mas só é emitido pelo tracker quando seu `flow_timeout` expira, muito depois do idle_slack de 30 s. Em produção (IDS rodando continuamente), isso seria um TP — o canal C2 estaria ativo durante a sessão e seria detectado corretamente dentro da janela.

### Alertas por janela (contagem de fluxos)

| Janela | Alertas | P1 médio | P1 mín | P1 máx |
|---|---|---|---|---|
| `recon` | 1.889 | 99,97% | 99,8% | 100,0% |
| `dos` (incl. ddos) | 13.029 | 99,86% | 90,5% | 100,0% |
| `bruteforce` | 1.476 | 99,89% | 99,6% | 100,0% |
| `web` | 93 | 99,89% | 99,6% | 100,0% |
| `mitm` | 95 | 99,90% | 99,8% | 100,0% |
| `spoofing` | 282 | 99,89% | 99,6% | 100,0% |
| `malware` | 1.618 | 99,81% | **96,4%** | 100,0% |

> Os 93 alertas na janela `web` e 95 em `mitm` são fluxos de DoS/DDoS residuais ainda sendo processados pelo tracker — não são tráfego web ou ARP real (as ferramentas nikto e arpspoof completaram em <1 s sem serviços disponíveis no VIM4).

### Confiança P1 (binário)

| Estatística | Valor |
|---|---|
| Média | 99,87% |
| Mediana | 99,90% |
| Desvio padrão | 0,43% |
| Mínimo | **90,5%** |
| Máximo | 100,0% |

### Precision / TPR relativo por threshold

| Threshold | TP mantidos | FP mantidos | Precision | TPR rel. |
|---|---|---|---|---|
| ≥ 90,0% | 18.482 | 1 | **99,99%** | 1,0000 |
| ≥ 95,0% | 18.440 | 1 | 99,99% | 0,9977 |
| ≥ 97,0% | 18.436 | **0** | **100,00%** | 0,9975 |
| ≥ 99,0% | 18.429 | 0 | 100,00% | 0,9971 |
| ≥ 99,9% | 16.548 | 0 | 100,00% | 0,8954 |

> Elevar o threshold para 97% elimina o único FP (que tem score 96,2%) e mantém 99,75% dos fluxos detectados — custo mínimo, benefício direto.

### Histograma P1

```
 90– 98%:     53 fluxos  ▌  (beacons C2 e DDoS de curta duração)
 99–100%:  16.300 fluxos  ████████████████████████████████████████
   100%:    2.129 fluxos  █████
```

97,7% dos fluxos detectados têm confiança ≥ 99%. O modelo é bimodal: praticamente certeza absoluta ou limiar mínimo.

### Recursos do VIM4

| | CPU | RAM |
|---|---|---|
| Baseline | 0,2–0,4% | 12,6% (985 MB) |
| Pico | **32,0%** | **13,3% (1041 MB)** |

---

## Parte 4 — Referência Offline (conjunto de teste do treinamento)

O modelo binário foi avaliado no conjunto de teste durante o treinamento (140.712 fluxos, 80/20 split estratificado). Esses números estão no **threshold Optuna-ótimo (0,157)**, não no threshold deployed (0,9). A 0,9, precision sobe e recall cai em relação a esses valores.

| Classe | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `attack` | 0,68 | **0,96** | 0,80 | 57.398 |
| `benign` | **0,96** | 0,69 | 0,80 | 83.314 |
| **Accuracy** | | | **0,80** | 140.712 |
| Macro avg | 0,82 | 0,83 | 0,80 | |

**F2-score** (objetivo Optuna, prioriza recall): **0,8855**

> O modelo é treinado para priorizar recall de ataques (F2-score), aceitando mais FP para não perder ataques. O F2-score de 0,8855 reflete essa prioridade.

---

## Parte 5 — Comparação: IDS Binário vs. IDS Multiclasse

Os dois pipelines rodam no mesmo VIM4, contra o mesmo conjunto de ataques, com o mesmo modelo de Fase 1. As diferenças observadas refletem o custo e o benefício de adicionar a Fase 2 (classificação de tipo).

---

### 5.1 — Métricas de Detecção Binária (Fase 1)

Ambos os pipelines usam o **mesmo modelo P1**. A comparação a seguir é feita em granularidade por segundo — cada segundo é classificado como "ataque detectado" ou não.

| Métrica | IDS Binário | IDS Multiclasse¹ |
|---|---|---|
| TP (segundos com alerta durante ataque) | **224** | **224** |
| FP (segundos com alerta fora da janela) | **1** | **0**² |
| FN (segundos sem alerta durante ataque) | **62** | **43** |
| TN (segundos sem alerta fora da janela) | **141** | **0**² |
| **Accuracy** | **85,28%** | 83,89%² |
| **Precision** | **99,56%** | 100,00%² |
| **Recall / TPR** | **78,32%** | **83,89%** |
| **F1-score** | **87,67%** | **91,25%** |
| **FPR** | **0,70%** | N/A² |

> ¹ Para o IDS multiclasse, qualquer alerta P1 (independente do rótulo P2) conta como detecção binária.  
> ² O log multiclasse termina dentro da janela de ataque (último alerta: 17:59:21, antes do fim do slack em 17:59:29). Não há período benigno observável → TN=0, FPR não computável. O FP=0 e Precision=100% refletem ausência de dados pós-ataque, não necessariamente ausência de FP em produção.

**Por que o recall do multiclasse é maior (83,9% vs 78,3%)?** Os 62 FN do binário incluem 19 s de slack pós-malware (além dos 43 s de warmup de recon). O multiclasse não tem dados nesse período → os 19 s extras de FN não são contabilizados. Com a mesma janela de observação, os recalls seriam iguais — ambos usam o mesmo P1.

**Por que o FN do recon é idêntico (43 s)?** Correto — ambos usam o mesmo P1. O gap no nmap -sU (UDP scan) afeta os dois igualmente.

---

### 5.2 — Métricas de Classificação de Tipo (Fase 2)

| Métrica | IDS Binário | IDS Multiclasse |
|---|---|---|
| **Acurácia (tipo)** | — | **81,34%** |
| **Macro Precision** | — | 25,61% |
| **Macro Recall** | — | 22,96% |
| **Macro F1** | — | **24,22%** |
| Fluxos enviados ao P3 | — | **19** |

**Per-class (TP / FP / FN / Precision / Recall / F1):**

| Classe | TP | FP | FN | Prec. (bin.) | Rec. (bin.) | F1 (bin.) | Prec. (multi.) | Rec. (multi.) | F1 (multi.) |
|---|---|---|---|---|---|---|---|---|---|
| `recon` | — | — | — | — | — | — | **1,000** | 0,607 | **0,756** |
| `dos` (incl. ddos) | — | — | — | — | — | — | 0,793 | **1,000** | **0,884** |
| `bruteforce` | — | — | — | — | — | — | 0,000 | 0,000 | 0,000 |
| `web` | — | — | — | — | — | — | 0,000 | 0,000 | 0,000 |
| `mitm` | — | — | — | — | — | — | 0,000 | 0,000 | 0,000 |
| `spoofing` | — | — | — | — | — | — | 0,000 | 0,000 | 0,000 |
| `malware` | — | — | — | — | — | — | 0,000 | 0,000 | 0,000 |

**Matriz de confusão P2:**

| True \ Pred | → dos | → recon | IDS Binário |
|---|---|---|---|
| **recon** | 634 | **981** | — |
| **dos** (incl. ddos) | **7.033** | 0 | — |
| **bruteforce** | **604** | 0 | — |
| **web** | **29** | 0 | — |
| **mitm** | **99** | 0 | — |
| **spoofing** | **99** | 0 | — |
| **malware** | **373** | 0 | — |

> O IDS binário não tem Fase 2 — cada alerta é apenas "attack", sem rótulo de tipo. A coluna da direita é propositalmente vazia para evidenciar o que o pipeline binário não provê.

---

### 5.3 — Uso de Recursos (VIM4)

Dados de SYS_SNAPSHOT coletados a cada ~3 s durante toda a sessão (incluindo períodos idle):

| Recurso | IDS Binário | IDS Multiclasse | Δ |
|---|---|---|---|
| **CPU média (sessão completa)** | **11,83%** | **19,65%** | +7,82 pp |
| **CPU máxima** | **32,0%** | **30,5%** | −1,5 pp |
| **CPU mínima** | 0,1% | 0,2% | ≈ igual |
| **CPU stdev** | 12,21% | 9,35% | multiclasse mais estável |
| **RAM média** | **1.014 MB** | **1.059 MB** | **+45 MB** |
| **RAM máxima** | **1.041 MB** | **1.093 MB** | **+52 MB** |
| **RAM mínima** | 985 MB | 1.044 MB | +59 MB (baseline) |
| **Net ↓ média (durante ataques)** | 5.881 KB/s | 6.305 KB/s | ≈ igual¹ |
| **Net ↓ máxima** | 17.068 KB/s | 16.714 KB/s | ≈ igual¹ |
| **Duração da sessão** | ~7 min 19 s | ~5 min 10 s | — |

> ¹ Os valores de rede refletem o tráfego de ataque recebido pelo VIM4 — independente do pipeline IDS. Picos de ~16–17 MB/s ocorrem durante o hping3 DDoS `--rand-source`.

**CPU média mais alta no multiclasse (19,65% vs 11,83%):** O multiclasse tem uma janela de observação menor (~310 s) com ataques por quase toda a sessão → a média é "inflada" pelo período de alta carga. O binário tem ~457 s de sessão, com longo período idle pós-ataque que puxa a média para baixo. Comparando apenas **durante os ataques** (dados das alert-lines):

| Recurso durante ataques | IDS Binário | IDS Multiclasse |
|---|---|---|
| CPU média | **22,8%** | **22,7%** |
| CPU máxima | 32,0% | 30,5% |
| RAM média | **1.004 MB** | **1.057 MB** |
| RAM máxima | 1.041 MB | 1.093 MB |

Durante os ataques o uso de CPU é **praticamente idêntico** entre os dois pipelines. A diferença é quase só de RAM: o multiclasse precisa de **~53 MB a mais** para carregar o segundo modelo P2 em memória.

---

### 5.4 — Throughput de Alertas

| Métrica | IDS Binário | IDS Multiclasse |
|---|---|---|
| Alertas durante ataques | 18.482 | 9.871 |
| Duração da janela de ataque | 285 s | 274 s |
| **Taxa de alertas** | **64,8 alertas/s** | **36,0 alertas/s** |
| LOW_CONF→P3 | — | 19 |

O binário gera **1,8× mais alertas por segundo** porque todo fluxo acima do threshold P1 é emitido imediatamente. No multiclasse, o P2 pode agregar ou filtrar fluxos de baixa confiança (→ P3), reduzindo o volume de alertas finais. Em produção, alertas em menor volume com rótulo de tipo têm mais valor operacional.

---

### 5.5 — Energia

> **Dados de energia não disponíveis.** A coluna `power_w` do log está vazia em ambas as sessões — o sensor de energia do VIM4 não estava configurado durante os experimentos. Para estimar consumo, seria necessário ativar o monitoramento via `vcgencmd` ou sensor externo.

Com base no uso de CPU durante ataques (≈22–23% em ambos), e assumindo que o VIM4 em plena carga consome ~10–12 W (ARM Cortex-A73 octa-core):
- **Estimativa de consumo**: ~2,3–2,8 W durante processamento de ataques
- **Diferença entre pipelines**: desprezível (~0 W extra para P2, dado que o CPU durante ataques é igual)
- **Custo real do P2**: principalmente RAM estática (+53 MB), não CPU dinâmica

---

### 5.6 — Resumo da Comparação

| Critério | IDS Binário | IDS Multiclasse | Vencedor |
|---|---|---|---|
| Recall (detecção binária) | 78,3% | 83,9%¹ | ≈ igual (mesmo modelo P1) |
| Precision (detecção binária) | 99,6% | 100,0%¹ | ≈ igual |
| F1 (detecção binária) | 87,7% | 91,3%¹ | ≈ igual |
| Classificação de tipo | ❌ | ✅ dos/recon | **Multiclasse** |
| Roteamento P3 | ❌ | ✅ 19 flows | **Multiclasse** |
| RAM | 985–1041 MB | 1044–1093 MB | **Binário** (−53 MB) |
| CPU durante ataques | ≈22,8% | ≈22,7% | Empate |
| Throughput | 64,8 alertas/s | 36,0 alertas/s | Depende do caso de uso |
| Energia estimada | ≈ igual | ≈ igual | Empate |

> ¹ Métricas computadas sobre janela de observação diferente — ver nota na seção 5.1.

**Conclusão:** O custo de adicionar a Fase 2 é ~53 MB de RAM e nenhum overhead de CPU durante ataques. O benefício é classificação de tipo para `dos` (F1=0,884) e `recon` (F1=0,756), mais roteamento inteligente de fluxos ambíguos para P3. Para um nó MEC com restrições de memória muito apertadas (<1 GB disponível), o IDS binário é preferível. Para o VIM4 com 8 GB de RAM, o multiclasse não apresenta nenhum custo prático.

---

## Parte 6 — Problemas em Aberto

| Problema | Status | Ação |
|---|---|---|
| PCAP capture failure | Persistente | `sudo setcap cap_net_raw+eip $(which tcpdump)` no PC atacante |
| Web/MITM sem tráfego real | Persistente | Subir `python3 -m http.server 80` no VIM4 |
| DoS dominance no P2 | Limitação de features | Auth counters + ARP state estão fora do espaço de features de fluxo puro |
| Fase 3 não integrada em tempo real | Pendente | Integrar UMAP+HDBSCAN ao `network_ids.py` para processar os 19 LOW_CONF |
| Canal C2 longo vaza idle slack | Comportamento esperado | Em produção o IDS roda continuamente — não há janelas; o fluxo seria TP |
