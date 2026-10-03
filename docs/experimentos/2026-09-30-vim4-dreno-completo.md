# Dreno completo no encerramento (residual zero) — 2026-09-30

Segunda reexecução de 2026-09-30, na sequência de
`2026-09-30-vim4-vazao-e-rerun.md` (run `20260930_014420`). Mesmos modelos
(`models/*_20260601_001154.pkl`, sem retreino) e mesmo protocolo. A única
mudança de código foi tornar o encerramento do IDS um **dreno completo**: em vez
de drenar a fila por até 60 s e reportar o que sobrasse como residual, o worker
agora espera a fila esvaziar por inteiro antes de gravar o `[SUMMARY]`, com uma
guarda de estagnação que só aborta se a inferência parar de progredir.

Run: `20260930_162133`. VIM 4 em 192.168.100.13. Offset de relógio VIM−PC
medido na pré-checagem: +0,153 s. Métricas calibradas com `--window-guard 2`.

---

## 1. Motivação

Na run `20260930_014420` a sessão hierárquica (B) encerrou com 26.928 fluxos
ainda na fila, descartados pelo limite de 60 s do dreno. Eram fluxos
capturados, não perdidos na captura, que o nó não terminou de processar dentro
da janela de encerramento. O objetivo desta rodada foi eliminar esse residual,
para que todo fluxo capturado seja avaliado e as duas sessões fechem com
contagens comparáveis, sem cauda não logada.

## 2. A mudança

`scripts/_ids_worker.py`: `stop(join_timeout=None)` passou a drenar a fila por
completo (a thread só encerra quando a fila zera), com guarda de estagnação
(`stall_limit`, padrão 180 s) que aborta apenas se o backlog não diminuir. Os
dois IDS (`network_ids.py`, `network_binary_ids.py`) chamam esse modo no
`KeyboardInterrupt`. A carência do SIGINT no `run_experiment.sh` subiu de 120 s
para 1200 s, para não matar o processo no meio do dreno. Testes novos em
`tests/test_ids_worker.py` cobrem o dreno completo e a guarda de estagnação.

## 3. Resultado central: residual zero

As duas sessões encerraram graciosamente, com `[SUMMARY]` gravado e
**`queue_residual = 0`**. O dreno completo levou alguns minutos a mais por
sessão, dentro da carência. Com isso os totais de fluxo ficaram próximos sem
precisar somar cauda: 827.458 em A e 809.448 em B (diferença de ~2,2%, só
variação do flood entre execuções). O teto de vazão continua evidente: a fila
ainda chega perto de meio milhão de fluxos e o atraso de emissão mediano da B
fica em 428 s. O residual deixou de ser necessário como evidência do teto; a
latência e o pico de fila bastam.

## 4. Fase 1 binária (por fluxo, limiar 0,9, janela +2 s)

| Métrica | Sessão A (binário) | Sessão B (hierárquico, P1) |
|---|---|---|
| Precisão | 0,968 | 0,974 |
| Revocação | 0,701 | 0,643 |
| F1 | 0,813 | 0,775 |
| Acurácia | 0,694 | 0,639 |
| FPR | 0,423 | 0,478 |

Janela estrita (sessão A): acurácia 0,679, precisão 0,945, revocação 0,696,
F1 0,802, FPR 0,553.

### Revocação por ataque (sessão A, calibrada)

| Ataque | Revocação | Fluxos |
|---|---|---|
| spoofing | 0,95 | 148.763 |
| dos | 0,90 | 166.428 |
| recon | 0,59 | 3.526 |
| ddos | 0,56 | 456.514 |
| bruteforce | 0,17 | 233 |
| mitm | 0,08 | 193 |
| web | 0,006 | 8.168 |
| malware | 0,03 | 103 |

## 5. Fase 2 multiclasse (sessão B, por fluxo)

Acurácia de tipo 0,417, macro-F1 sobre ataques 0,194, acurácia de tipo sobre
detectados 0,643, 71.875 fluxos de baixa confiança. Por classe: recon F1 0,746
(prec 0,949, rec 0,614), dos F1 0,606 (prec 0,743, rec 0,512). O spoofing
colapsa em dos (98.473 fluxos) e em malware (34.728). As demais classes ficam
próximas de zero.

## 6. Vazão e custo

| | Sessão A (binário) | Sessão B (hierárquico) |
|---|---|---|
| Fluxos classificados | 827.458 | 809.448 |
| Alertas | 567.836 | 516.182 |
| Vazão de ataque | ~985 fluxos/s | ~1.050 fluxos/s |
| Pico da fila | 433.469 | 491.880 |
| Residual na saída | 0 | 0 |
| Latência ponta a ponta média | 116 s | 343 s |
| Latência máxima | 182 s | 550 s |
| Atraso de emissão (mediana) | 181 s | 428 s |
| Inferência por fluxo | 0,17 ms | P1 0,14 ms + P2 1,22 ms |
| CPU média / máx | 12,3% / 43% | 41,6% / 73% |
| RAM média / máx | 1.866 / 2.449 MB | 2.041 / 2.606 MB |

O teto de vazão persiste: a ~1.050 fluxos/s o VIM 4 não classifica em tempo
real, enfileira para não descartar, e a Fase 2 triplica a latência e leva a CPU
média de 12% a 42%. A diferença: agora a fila é drenada por completo no
encerramento, então o custo aparece como latência e memória, sem residual
descartado.

### Energia (modelo linear de CPU, banda de sensibilidade)

Sessão A: 5.523 J no total (banda 4.375–6.672), potência média 3,37 W. Sessão B:
8.261 J (banda 6.478–10.043), potência média 5,13 W. O idle da B permanece alto
(4,81 W contra 2,77 W da A) porque o pipeline hierárquico continua drenando
backlog durante os intervalos entre ataques. Energia é estimativa: a VIM não
expõe RAPL/INA226/hwmon.

## 7. Comparação com a run 20260930_014420

O que mudou: residual da B de 26.928 para 0; totais de fluxo agora próximos sem
somar cauda (809k logados na B). O resto variou pouco, dentro do flood: A subiu
revocação (0,64→0,70) e F1 (0,78→0,81) e caiu precisão (0,98→0,97) e FPR piorou
(0,33→0,42); B praticamente igual na Fase 1. Multiclasse estável (macro-F1 0,194
nas duas). Energia dentro de ~1%. O teto de vazão e a leitura de que as duas
fases não cabem no orçamento de tempo real sob flood permanecem.

## 8. Reproduzir

Igual ao writeup anterior, agora com a carência longa já no runner:

```bash
export VIM4_PASS=<senha sudo da VIM 4>
sudo -v
./scripts/run_experiment.sh --skip-calibration --target 192.168.100.13
```

Métricas calibradas: `ids_metrics.py ... --clock-offset 0.153 --window-guard 2`.
Saídas: `logs/session_{a,b}_20260930_162133/`,
`results/session_{a,b}_metrics_20260930_162133{,_guard2s}.json`.
