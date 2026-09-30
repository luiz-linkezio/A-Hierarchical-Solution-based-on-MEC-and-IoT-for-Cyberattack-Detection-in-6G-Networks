# Revalidação no VIM 4 com métrica por fluxo (leak-independent) — 2026-09-29

Reexecução completa da validação ao vivo no nó de borda VIM 4, com os modelos já
treinados (`models/*_20260601_001154.pkl`, **sem retreino**), agora sob uma
**métrica de detecção por fluxo, independente de vazamento**. Substitui a métrica
por segundo da sessão de 2026-06-19, que foi contaminada pelo atraso de emissão do
extrator de fluxos sob *flood*.

Run: `20260929_144008`. VIM 4 em 192.168.100.13 (UTC, NTP), PC atacante em
192.168.100.2/.245. Offset de relógio VIM−PC = 0,135 s.

---

## 1. O que mudou em relação à sessão de junho

A métrica antiga marcava, para **cada segundo** do teste, se havia ataque, usando o
instante em que o **alerta foi emitido**. Sob DoS/DDoS a VIM 4 satura e emite os
fluxos com atraso (idle_timeout 30 s, flow_timeout 120 s, mais fila), então os
ataques "vazavam" para segundos e janelas vizinhos. **Atraso de emissão medido
nesta sessão: mediana de 163 s (binário) e 216 s (multiclasse), p95 de 324/396 s,
máximo de 364/432 s.** Qualquer métrica ancorada na emissão é inválida.

A métrica nova pontua **por fluxo**, rotulando cada fluxo pela janela de ataque em
que ele **começou** (`flow_ts` = instante de captura do 1º pacote no cabeçalho do
PCAP), nunca pela emissão. Todo fluxo é logado (ATTACK e BENIGN), com `flow_ts` e o
P1/P2. O atraso de emissão passa a ser só um diagnóstico.

**Filtro de endpoints:** a LAN não é isolada (roteador .1, hosts .4/.7 com
mDNS/SSDP, NTP/apt da própria VIM). Um fluxo só é ataque se envolve o alvo e a
outra ponta é (a) um IP atacante, (b) um host de fora que iniciou o fluxo
(entrada: spoofing/ddos de origem forjada) ou (c) um host de fora contatado pela
VIM **na janela do mitm**. O resto é fundo (benigno).

**Janela estrita vs. calibrada (+2 s):** o orquestrador grava `start_time` depois
de já ter disparado a ferramenta, então os primeiros fluxos de ataque começam até
~2 s antes do instante anotado. Sob janela estrita, esses fluxos (do atacante ou de
origem forjada) caem fora da janela e viram "falsos positivos" — 88 % dos FP são
exatamente isso. A calibração `--window-guard 2` alarga cada janela em 2 s de cada
lado e os reabsorve (satura em 2 s; idêntico a +3 e +5 s). Continua rotulando por
`flow_ts`. **Reporta-se as duas.**

---

## 2. Como reproduzir

No **PC atacante**, na raiz do projeto:

```bash
export VIM4_PASS=<senha sudo da VIM 4>     # NUNCA versionar; lido do ambiente
./scripts/run_experiment.sh --skip-calibration --target 192.168.100.13 \
  2>&1 | tee logs/run_experiment_$(date +%Y%m%d_%H%M%S).log
```

O runner sobe e derruba o IDS na VIM sozinho em cada sessão (A binário, B
multiclasse), roda os 8 ataques com 120 s de intervalo ocioso, copia os logs e
calcula as métricas. As métricas calibradas (+2 s) são geradas com:

```bash
python3 scripts/ids_metrics.py --ids <log> --report <report.json> \
  --mode {binary|multiclass} --label-map ddos=dos --idle-slack 90 \
  --clock-offset 0.135 --target-ip 192.168.100.13 \
  --attacker-ips 192.168.100.2,192.168.100.245 --window-guard 2 \
  --output results/session_X_metrics_<ts>_guard2s.json
```

Saídas desta sessão: `logs/session_{a,b}_20260929_144008/`,
`results/session_{a,b}_metrics_20260929_144008.json` (estrita) e
`..._guard2s.json` (calibrada).

---

## 3. Resultados — Fase 1 binária (por fluxo, limiar 0,9)

| Métrica | Sessão A estrita | A calibrada +2 s | Sessão B (P1) estrita | B calibrada +2 s |
|---|---|---|---|---|
| Precisão | 0,890 | **0,986** | 0,803 | **0,992** |
| Revocação | 0,792 | 0,809 | 0,960 | 0,966 |
| F1 | 0,838 | 0,889 | 0,874 | 0,979 |
| FPR | 0,926 | 0,607 | 0,993 | 0,933 |
| Acurácia | 0,723 | 0,801 | 0,777 | 0,959 |

Matriz de confusão por fluxo (sessão A, estrita / +2 s): VP 63.363/70.249, FP
7.853/967, FN 16.626/16.632, VN 632/626.

**A precisão é a métrica de especificidade confiável.** A captura é ~99 % *flood*,
então o tráfego benigno soma poucas centenas de fluxos (A: ~1.600 negativos; B:
~405); o FPR herda um denominador minúsculo e ruidoso, não comparável a um FPR
sobre baseline limpo.

### Revocação por tipo de ataque (calibrada +2 s)

| Ataque | Sessão A | Sessão B | Observação |
|---|---|---|---|
| spoofing | 1,00 (32.616) | 1,00 (16.528) | *flood* de origem forjada, detectado sempre |
| dos | 0,84 (32.134) | 0,95 (21.712) | robusto |
| ddos | 0,47 (18.202) | 1,00 (6.911) | queda em A sob maior taxa de pacotes |
| recon | 0,58 (3.659) | 0,80 (1.320) | scan do nmap, poucos pacotes/porta |
| web | 0,03 (240) | 0,14 (240) | majoritariamente perdido |
| bruteforce | n.a. (26) | n.a. (8) | não avaliável: lista de senhas ausente no PC, reserva de 17 entradas; P1 0,70–0,88 |
| mitm | n.a. (4) | n.a. (3) | não avaliável: tráfego ICMP, que o netflower não converte em fluxo; os fluxos da janela são o SSH de controle |
| malware | — (0) | — (0) | não gerou fluxos direcionados ao alvo |

(entre parênteses: nº de fluxos da classe). Tempo até o 1º fluxo detectado
(janela estrita): dos e spoofing 0,0 s, recon 0,4 s, web 0,6 s, ddos 5,9 s —
detecção quase instantânea.

**Falhas do gerador de tráfego (não do detector):** o PC atacante não tinha
`/usr/share/wordlists/`, então bruteforce (17 senhas) e web (18 caminhos) rodaram
com listas reserva e geraram pouco tráfego. O MITM envenenou o ARP, mas o tráfego
pela rota envenenada foi `ping`, e o netflower só parseia TCP e UDP, então nada
virou fluxo (os floods ICMP de DoS e spoofing também não entram nas contagens).
Bruteforce e mitm ficam como não avaliáveis nesta execução. Para repetir: instalar
as listas, gerar tráfego TCP no MITM e fazer o runner abortar se faltar lista.

---

## 4. Resultados — Fase 2 multiclasse (Sessão B, por fluxo)

| Métrica | Estrita | Calibrada +2 s |
|---|---|---|
| Acurácia de tipo | 0,454 | **0,605** |
| Macro-F1 (classes avaliáveis) | — | 0,404 |
| Macro-F1 (n.a. contando como 0) | 0,246 | 0,269 |
| Acurácia de tipo sobre detectados | 0,583 | 0,631 |

Por classe (calibrada): recon F1 **0,861** (prec 0,99, rec 0,76) — única bem
separada; dos F1 0,753 (prec 0,62, rec 0,96); **spoofing 100 % → dos** (16.528
fluxos, o erro dominante — mas classificar *flood* forjado como dos é
defensavelmente correto); web colapsa em benigno/dos; bruteforce e mitm não avaliáveis;
malware 0 fluxos. Confiança do P2: média 0,972 (alta mesmo quando erra em
spoofing→dos).

---

## 5. Recursos, throughput e energia

| | Sessão A (binário) | Sessão B (hierárquico) | Δ Fase 2 |
|---|---|---|---|
| CPU média / máx | 11,8 % / 28,4 % | 12,1 % / 27,7 % | ~igual |
| RAM média / máx | 1.161 / 1.286 MB | 1.214 / 1.349 MB | **+53 / +63 MB** |
| Fluxos classificados | 88.474 | 47.127 | |
| Alertas | 71.216 | 45.529 | |
| Tráfego de ataque | ~120 fluxos/s | ~57 fluxos/s | |
| Energia total (banda) | 5.310 J (4.209–6.410) | 5.366 J (4.253–6.478) | ~igual |
| Potência em ataque | 3,39 W | 3,40 W | ~igual |

**Custo da Fase 2 = memória (~+53 MB), sem CPU nem energia.** Energia é estimativa
(modelo linear de CPU; a VIM não expõe RAPL/INA226/hwmon), reportada com banda de
sensibilidade.

---

## 6. Correções de narrativa (vs. artigo/relatório anteriores)

Afirmações antigas **derrubadas** e substituídas:

1. ~~"FPR 0 % em baseline limpo" / "1 FP em 98.288"~~ → precisão por fluxo ≈0,99
   (calibrada); FPR não é medida de especificidade confiável aqui (denominador
   diminuto sob *flood*).
2. ~~"≥99 % de recall em bruteforce/web/mitm/spoofing"~~ → só spoofing 1,00;
   bruteforce/mitm não avaliáveis (falha do gerador), web 0,03–0,14,
   malware 0 fluxos.
3. recon multiclasse F1 0,976 → **0,861** (ainda a única bem separada).
4. multiclasse acurácia 48,4 % / macro-F1 0,320 → 60,5 % (45,4 % estrita) /
   0,404 sobre as classes avaliáveis (0,269 com n.a. = 0).
5. Atraso de emissão "~80 s" → **163–216 s de mediana** (medido).
6. **Sobrevive:** custo da Fase 2 = ~+50 MB RAM sem CPU/energia; detecção rápida
   (0–6 s); spoofing→dos.

Documentos atualizados nesta rodada (cópias, originais preservados):
`docs/artigo/main.tex`, `docs/artigo/main_short.tex`,
`docs/relatorio_ic/relatorio_final_pibic.tex`; figuras
`docs/results/images/timeseries_session_{a,b}_*.png`; `README.md`.
