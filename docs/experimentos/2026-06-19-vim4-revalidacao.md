# Revalidação ao vivo do IDS hierárquico no VIM 4 — 2026-06-19

Registro de metodologia e resultados da revalidação ao vivo da Seção 4 do artigo
(`docs/artigo.tex`), refeita por completo com os modelos já treinados
(`models/*_20260601_001154.pkl`, **sem retreino**). Objetivos: (i) cobrir as **8
classes** de ataque no multiclasse; (ii) medir energia de forma mais séria.

Spec de design: `docs/superpowers/specs/2026-06-19-vim4-multiclass-energy-revalidation-design.md`.
Plano: `docs/superpowers/plans/2026-06-19-vim4-multiclass-energy-revalidation.md`.

---

## 1. Como reproduzir (sem o agente)

No **PC atacante**, na raiz do projeto:

```bash
export VIM4_PASS=khadas          # senha de sudo da VIM 4 (NUNCA versionar)
./scripts/run_experiment.sh --skip-calibration \
  2>&1 | tee logs/run_experiment_$(date +%Y%m%d_%H%M%S).log
```

- O script pede **uma vez** a senha de sudo do PC (ataques precisam de root) e
  mantém o `sudo` vivo durante toda a sessão (~55–60 min).
- `--skip-calibration` reaproveita `constants/power_model_vim4.json` já calibrado.
  Para recalibrar a energia: rode sem essa flag (faz idle vs. stress na VIM 4).
- Login na VIM 4 é por **chave SSH** (`~/.ssh/id_ed25519`); a senha só é usada
  para `sudo` remoto, lida de `$VIM4_PASS` (nunca escrita em arquivo do repo).

Flags úteis: `--gap N` (ocioso entre ataques, padrão 120), `--slack N`
(`idle_slack` da análise, padrão 90), `--duration N` (ataques por tempo, 60),
`--baseline N` (idle antes/depois, 60), `--capture` (liga PCAP, off por padrão),
`--dry-run` (imprime tudo sem executar).

Saídas: `logs/session_{a,b}_<ts>/` (logs do IDS + report do orquestrador) e
`results/session_{a,b}_metrics_<ts>.json` (métricas).

---

## 2. Artefatos e o que cada um faz

| Arquivo | Onde roda | Função |
|---|---|---|
| `scripts/run_experiment.sh` | PC | Orquestra tudo: pré-checagem → deploy p/ VIM 4 → http.server → Sessão A (binário) → Sessão B (multiclasse) → teardown → análise. Idempotente, com teardown garantido (`trap`). |
| `scripts/attack_orchestrator.py` | PC | Executa 8 categorias de ataque em sequência contra a VIM 4, com `--gap` ocioso entre elas; grava `report_*.json` com as janelas de tempo (ground truth). |
| `scripts/network_binary_ids.py` | VIM 4 | IDS Fase 1 (binário benigno×ataque). |
| `scripts/network_ids.py` | VIM 4 | IDS Fase 1+2 (binário + tipo de ataque). |
| `constants/power_telemetry.py` | ambos | Telemetria: temperatura, frequência por cluster (DVFS) e potência estimada (modelo de CPU) — usado pelos IDS, pelo calibrador e pela análise. |
| `scripts/calibrate_power.py` | VIM 4 | Calibra o modelo de energia (idle vs. `stress`), ancora P_idle/P_max e grava `constants/power_model_vim4.json`. |
| `scripts/ids_metrics.py` | PC | Calcula as métricas a partir do log do IDS + janelas do report. |
| `constants/power_model_vim4.json` | ambos | Parâmetros do modelo de energia (gerado pela calibração). |

### Formato dos logs do IDS
- **Linha de alerta** (por fluxo com P1 ≥ 0,9): `HH:MM:SS\tP1%\t[p2_label\tP2%\t]src_ip\t...`
- **`[SYS_SNAPSHOT]`** (a cada ~3 s): `CPU x% | RAM y% (z MB) | Net ... | Power w W | Temp t C | Freq f1/f2 MHz`.
  É a fonte de CPU/RAM/energia/throughput — **não dependemos do bloco
  `[SUMMARY]`**, que pode não ser escrito se o IDS for encerrado à força.

### Como interpretar as métricas
- **Binário**: granularidade **por segundo** — cada segundo dentro de uma janela
  de ataque (estendida por `idle_slack`) é "ataque"; fora, "benigno". O **FPR
  confiável** é o do **baseline pré-ataque** (benigno limpo, sem flood anterior
  drenando); o FPR "global" inclui o rastro de flood pós-ataque e **não é
  representativo**.
- **Multiclasse**: cada alerta é mapeado à sua janela (rótulo verdadeiro) e
  comparado ao tipo previsto pelo P2. Alertas fora de qualquer janela são
  descartados.
- **Energia**: ver Seção 5.

---

## 3. Ambiente (verificado 2026-06-19)

| | PC (atacante) | VIM 4 (IDS/alvo) |
|---|---|---|
| IP / iface | 192.168.100.232 / `eno1` | 192.168.100.5 / `eth0` |
| Gateway | 192.168.100.1 | 192.168.100.1 |
| SoC | AMD Ryzen 5 7600 | Amlogic A311D2 (4×A73 + 4×A53), 8 GB |
| Rede | laboratório isolado (só PC + VIM 4 + roteador) | idem |

Modelos na VIM 4: `binary_classifier_20260601_001154.pkl`,
`multiclass_classifier_20260601_001154.pkl` (re-sincronizados no deploy).

---

## 4. Resultados (rodada `20260619_230219`)

Sessão A (binário): 23:03–23:28 BRT. Sessão B (multiclasse): 23:30–23:55 BRT.
Cada sessão: 60 s de baseline benigno antes e depois; 8 ataques com **120 s de
intervalo ocioso** entre eles. Análise com `idle_slack = 90 s`.

### 4.1 IDS Binário (Fase 1) — por segundo

| Métrica | Valor |
|---|---|
| Acurácia | 68,6% |
| Precisão | 89,3% |
| Revocação (TPR) | 71,1% |
| F1 | 79,2% |
| **FPR (baseline pré-ataque limpo)** | **0,0%** (0/57 s) |

Matriz por segundo: TP 967, FP 116, FN 393, TN 144. O FPR "global" (44,6%) é
inteiramente o rastro de flood pós-ataque (ver Seção 6) e não representa o
comportamento do modelo — no benigno limpo o FPR é **zero**.

Taxa de detecção por ataque (por segundo): recon 20,9%; dos 59,4%; bruteforce
100%; web 100%; mitm 100%; spoofing 99,3%; malware 21,3%. recon/malware baixos
pelas causas conhecidas (lacuna do scan UDP; janela curta do malware).

### 4.2 IDS Multiclasse (Fase 2) — por classe

| Classe | TP | FP | FN | Precisão | Revocação | F1 |
|---|---:|---:|---:|---:|---:|---:|
| recon | 987 | 14 | 35 | 0,986 | 0,966 | **0,976** |
| dos (incl. ddos) | 13302 | 15468 | 29 | 0,462 | 0,998 | 0,632 |
| malware | 373 | 137 | 1898 | 0,731 | 0,164 | 0,268 |
| bruteforce | 4 | 17 | 5023 | 0,190 | 0,001 | 0,002 |
| web | 0 | 9 | 2737 | 0,000 | 0,000 | 0,000 |
| mitm | 0 | 1 | 1133 | 0,000 | 0,000 | 0,000 |
| spoofing | 0 | 2 | 4793 | 0,000 | 0,000 | 0,000 |

Acurácia geral (tipo): **48,4%**; Macro F1: 0,320. Alertas em janela: 30.314;
fora de janela: 5.108.

**Leitura honesta.** Com as janelas isoladas pelos gaps, o resultado é genuíno
(não é mais artefato de bleed): apenas **recon** é classificado corretamente e
**malware** parcialmente; **bruteforce, web, mitm e spoofing colapsam em `dos`**.
Para `spoofing` isso é até correto (é um flood). Para os demais, é a **limitação
de features** já documentada (curtos/rápidos, indistinguíveis de dos nas 55
features por-fluxo) somada ao **desvio treino→produção**: na avaliação offline
(CIC) web/mitm/bruteforce têm F1 0,80/0,53/0,31, mas o tráfego ao vivo gerado
aqui (medusa contra serviços que falham rápido, nikto contra um `http.server`
trivial, MITM por arpspoof sem sessão de vítima real) difere do dataset e cai
em dos. Avaliar essas classes "de verdade" exigiria serviços/vítimas reais ou
features de estado agregado entre fluxos (trabalho futuro).

### 4.3 Comparação Binário × Multiclasse (recursos)

| Métrica | Binário (A) | Multiclasse (B) | Δ |
|---|---:|---:|---:|
| CPU média | 12,9% | 13,9% | +1,0 p.p. |
| CPU máxima | 29,0% | 31,7% | — |
| RAM média | 1187 MB | 1238 MB | **+50 MB** |
| RAM máxima | 1263 MB | 1333 MB | +70 MB |
| Throughput | 62,9 alertas/s | 22,1 alertas/s | — |

**Achado central (reproduzido):** o overhead do P2 é **praticamente só RAM
(+50 MB)**, sem custo de CPU nem de energia — consistente com o artigo original
(+52 MB). O binário emite ~2,8× mais alertas brutos (filtro adicional do P2).

### 4.4 Energia (estimativa calibrada — ver Seção 5)

| | Binário (A) | Multiclasse (B) |
|---|---:|---:|
| Potência média (durante ataque) | 3,46 W | 3,50 W |
| Potência média (idle) | 2,90 W | 3,00 W |
| Energia total da sessão | 5.443,8 J (1,51 Wh) | 5.500,2 J (1,53 Wh) |
| Banda de sensibilidade | 4.312–6.576 J | 4.355–6.646 J |

Potência durante ataques praticamente idêntica nos dois pipelines — reforça que
o custo do P2 é RAM, não CPU/energia.

---

## 5. Energia: metodologia e limitações

A VIM 4 **não expõe medição de potência por software** (sem RAPL, INA226,
`hwmon` ou `power_supply`; confirmado por sondagem). Logo, a energia é uma
**estimativa**, não medição direta.

- **Modelo**: linear na utilização de CPU,
  `P(t) = P_idle + (P_max − P_idle) · CPU%(t)`, integrado sobre a série de
  `SYS_SNAPSHOT` (~3 s), separando ataque vs. idle pelas mesmas janelas de ground
  truth.
- **Calibração** (`calibrate_power.py`, 1×): mede CPU% em idle real (0,14%) e sob
  `stress --cpu 8` (99,93%), registrando temperatura (49→64 °C) e frequência por
  cluster (A73 1800→2208 MHz; A53 500→2016 MHz) como proveniência. Os watts
  (`P_idle = 2,5 W`, `P_max = 9,0 W`) são **ancorados** no envelope de potência
  board-level do Khadas VIM 4 / A311D2 (USB-C PD), **não medidos**.
- **Incerteza**: reportada como **banda de sensibilidade** com
  `P_idle ∈ [2,0; 3,0] W` e `P_max ∈ [7,0; 11,0] W`.
- **Melhoria vs. artigo original**: antes o campo `power_w` ficava vazio (só lia
  RAPL/Intel) e os watts eram chutados (2/11 W). Agora os IDS registram
  `power_w`, temperatura e DVFS por amostra, e os endpoints são calibrados +
  declarados como estimativa com banda. Medição absoluta exigiria um medidor de
  hardware externo (trabalho futuro).

---

## 6. Problemas encontrados durante a execução (e como foram resolvidos)

1. **Captura PCAP gigante** (3,8 GB no `dos`) nas primeiras tentativas → captura
   desligada por padrão (as métricas não usam PCAP; vêm do log do IDS + janelas).
2. **Contaminação entre sessões**: o IDS binário não morria com SIGINT
   (netflower's `capture_live` sequestra o sinal) e seguia rodando na Sessão B,
   contaminando CPU/RAM. **Correções**: (a) reinstalar handlers de SIGINT/SIGTERM
   *após* `handle.start()` nos IDS (shutdown gracioso); (b) `stop_ids` no runner
   com escalada `INT→TERM→KILL` e verificação por `ps -p`. Confirmado sem
   contaminação na rodada válida (timestamps A terminam antes de B começar).
3. **`[SUMMARY]` ausente** quando o IDS é morto à força → a análise passou a
   derivar CPU/RAM/throughput dos `SYS_SNAPSHOT`, sem depender do `[SUMMARY]`.
4. **Saturação do IDS sob flood (achado)**: os floods (`--flood`) geram fluxos
   mais rápido do que a VIM 4 processa (~98/s de emissão), criando um **rastro de
   fluxos atrasados (~80 s)** que (a) inflava o FPR pós-ataque e (b) vazava para
   as janelas seguintes. **Correções**: intervalos ociosos de **120 s** entre
   ataques (drenam o rastro fora das janelas) + `idle_slack = 90 s` (credita o
   dreno à janela do próprio flood) + matriz por-segundo baseada em janelas (gaps
   contam como benigno) + FPR medido no baseline pré-ataque limpo. Após isso, as
   janelas ficaram isoladas (só 14% de alertas fora de janela) e `malware` subiu
   de F1 0 → 0,27.
5. **`spoofing` saía com 0 pacotes** (`hping3 --faster -c` colapsava) → trocado
   por `--flood` com fonte forjada fixa (`-a`), limitado pelo timeout da janela.

---

## 7. Limitações e trabalhos futuros

- Medição de energia por hardware (medidor externo) para validar a estimativa.
- Tráfego realista para web/mitm/bruteforce (serviços e vítimas reais) e/ou
  features de estado agregado entre fluxos, para avaliar essas classes além do
  colapso em `dos`.
- Mitigar a saturação do extrator de fluxos sob flood (rate dos floods, ou
  captura mais eficiente) para reduzir o rastro pós-ataque.
- Lacuna de detecção do recon (scan UDP do nmap vs. `idle_timeout`) — já no
  artigo como trabalho futuro.
