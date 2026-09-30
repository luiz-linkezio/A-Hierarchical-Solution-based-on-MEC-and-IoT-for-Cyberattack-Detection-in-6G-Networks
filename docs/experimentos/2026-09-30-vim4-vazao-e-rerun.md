# Vazão desacoplada e reexecução no VIM 4 — 2026-09-30

Reexecução completa da validação ao vivo no nó de borda VIM 4, com os modelos já
treinados (`models/*_20260601_001154.pkl`, sem retreino), depois de duas
correções na captura e no gerador de tráfego. Continua a linha da métrica por
fluxo de 2026-09-29 (ver `2026-09-29-vim4-metrica-por-fluxo.md`).

Run: `20260930_014420`. VIM 4 em 192.168.100.13 (UTC, NTP), PC atacante em
192.168.100.2/.245. Offset de relógio VIM−PC = −0,085 s.

---

## 1. O problema que motivou a rodada

Na sessão de 2026-09-29 as duas sessões divergiam apesar de a Fase 1 ser o mesmo
modelo: a sessão A (binária) via um conjunto de fluxos e a B (hierárquica) via
outro, menor, perdendo floods UDP inteiros. A causa não era o detector nem o
tráfego. A inferência rodava dentro do callback de captura do netflower
(`session.process` → `_flush_flow` → `writer.write` → `on_flow`), então a thread
de captura ficava bloqueada durante cada predição. Sob flood, o buffer do kernel
(libpcap) transbordava nesse intervalo e descartava pacotes. A sessão B, que paga
Fase 1 e Fase 2 por alerta, era mais lenta e descartava mais, por isso via menos
tráfego.

---

## 2. As duas correções

**Captura desacoplada da inferência.** O callback de captura agora só enfileira o
fluxo e retorna. Uma thread worker separada (`scripts/_ids_worker.py`) esvazia a
fila em lotes e roda a inferência em batch, cerca de 36 vezes mais rápido por
fluxo que uma predição por vez. No pipeline hierárquico o lote é processado por
fase: a Fase 1 no lote inteiro e a Fase 2 só no subconjunto que alertou. A fila
não tem limite prático, de modo que todo fluxo capturado é avaliado mesmo que o
processamento fique atrás do ataque. No encerramento o dreno é limitado a 60 s e
o que sobrar é reportado como residual, para o encerramento não travar. A
profundidade da fila é gravada a cada 3 s no log.

**Gerador de tráfego.** A força bruta passou a usar 20 usuários e listas de senha
geradas com 6000 entradas, em vez de cair numa reserva de 17 entradas quando a
wordlist padrão não existe. O MITM passou a gerar tráfego TCP e UDP pela rota
ARP-envenenada, em vez de ICMP, já que o netflower só converte TCP e UDP em fluxo.
Com isso força bruta e MITM voltaram a ser avaliáveis.

---

## 3. Resultados — Fase 1 binária (por fluxo, limiar 0,9, janela +2 s)

| Métrica | Sessão A (binário) | Sessão B (hierárquico, P1) |
|---|---|---|
| Precisão | 0,984 | 0,970 |
| Revocação | 0,643 | 0,640 |
| F1 | 0,778 | 0,771 |
| Acurácia | 0,644 | 0,635 |
| FPR | 0,332 | 0,477 |

As duas sessões agora convergem (revocação 0,643 e 0,640), o que confirma que a
divergência anterior era perda de pacote, não tráfego diferente. A precisão é a
métrica de especificidade confiável: a captura é quase toda flood, então o
tráfego benigno soma poucas centenas de fluxos e o FPR herda um denominador
diminuto.

A revocação de ~0,64 é o retrato honesto no limiar operacional 0,9. Os floods UDP
de pacote único são pontuados pela Fase 1 em torno de 0,807 e caem logo abaixo do
limiar, entrando como falso negativo. Antes eles eram descartados na captura e
nem entravam na conta.

### Revocação por ataque (sessão A)

| Ataque | Revocação | Fluxos | Observação |
|---|---|---|---|
| spoofing | 0,94 | 152.698 | flood de origem forjada |
| dos | 0,92 | 167.322 | robusto |
| ddos | 0,46 | 473.821 | cauda de pacote único UDP escapa em 0,9 |
| recon | 0,57 | 3.684 | scan do nmap, poucos pacotes por porta |
| bruteforce | 0,14 | 258 | avaliável; baixo volume por natureza |
| mitm | 0,10 | 192 | avaliável; TCP e UDP pela rota envenenada |
| web | 0,007 | 8.154 | majoritariamente perdido |
| malware | 0,03 | 103 | poucos fluxos, low-and-slow |

---

## 4. Resultados — Fase 2 multiclasse (Sessão B, por fluxo)

Acurácia de tipo 0,442, macro-F1 sobre ataques 0,194, acurácia de tipo sobre
detectados 0,686. Por classe: recon F1 0,737 (prec 0,924, rec 0,612), dos F1
0,618 (prec 0,745, rec 0,528). O spoofing colapsa em dos (98.335 fluxos) e em
malware (17.491). Boa parte dos fluxos de dos e spoofing vira benigno porque a
Fase 1 não alerta a cauda de pacote único. As demais classes ficam próximas de
zero.

---

## 5. Vazão e custo — a descoberta central

| | Sessão A (binário) | Sessão B (hierárquico) |
|---|---|---|
| Fluxos classificados | 831.154 | 786.821 |
| Alertas | 526.928 | 498.066 |
| Vazão de ataque | ~1.078 fluxos/s | ~1.021 fluxos/s |
| Pico da fila | 456.681 | 495.051 |
| Residual na saída | 0 | 26.928 |
| Latência ponta a ponta média | 120 s | 352 s |
| Latência máxima | 181 s | 550 s |
| Atraso de emissão (mediana) | 180 s | 437 s |
| Inferência por fluxo | 0,15 ms | P1 0,13 ms + P2 1,23 ms |
| CPU média / máx | 11,8% / 44% | 40,1% / 74% |
| RAM média / máx | 1.907 / 2.528 MB | 2.010 / 2.663 MB |

A ~1050 fluxos/s o VIM 4 não classifica em tempo real. Ele enfileira para não
descartar, com latência média de 120 s no pipeline binário e 352 s no
hierárquico, uma fila que chega perto de meio milhão de fluxos e RAM em torno de
2,6 GB. A Fase 2 triplica a latência, leva a CPU média de 12% para 40% e a
potência média de 3,36 W para 5,03 W, e deixa um backlog residual que o nó não
esvazia. A média de CPU baixa engana, porque um único núcleo (o do worker) satura
enquanto a média sobre os 8 núcleos fica baixa.

Isso substitui a leitura antiga de que as duas fases cabem no orçamento do nó ARM
e de que a Fase 2 custa só memória. Sob flood sustentado elas não cabem no
orçamento de tempo real, e esse teto de vazão é a limitação a reportar. Caminhos
para fechá-la ficam como trabalho futuro: amostragem sob sobrecarga, mais de um
worker de inferência, ou hardware mais capaz.

### Energia (modelo linear de CPU, banda de sensibilidade)

Sessão A: 5.343 J no total (banda 4.233–6.454), potência média 3,36 W. Sessão B:
8.205 J (banda 6.437–9.973), potência média 5,03 W. Energia é estimativa: a VIM
não expõe RAPL/INA226/hwmon.

---

## 6. Por que os totais de fluxo diferem entre A e B

831k em A contra 786k em B. Dois motivos: o flood é não determinístico entre
execuções, o que dá uma diferença de poucos por cento (o spoofing, por exemplo,
gerou 152k fluxos em A e 119k em B); e a sessão B terminou com um residual de
26.928 fluxos que não foram logados, porque o dreno de 60 s não esvaziou a fila.
Somando o residual, a B viu cerca de 813k, a ~2% da A. Não vale refazer o
experimento só por esses 3% de cauda ociosa: o residual é, ele próprio, evidência
do teto de vazão.

---

## 7. Reproduzir

No PC atacante, na raiz do projeto:

```bash
export VIM4_PASS=<senha sudo da VIM 4>     # NUNCA versionar; lido do ambiente
sudo -v
./scripts/run_experiment.sh --skip-calibration --target 192.168.100.13 \
  2>&1 | tee logs/run_experiment_$(date +%Y%m%d_%H%M%S).log
```

Métricas calibradas (+2 s) geradas com `scripts/ids_metrics.py ... --clock-offset
-0.085 --window-guard 2`. Saídas: `logs/session_{a,b}_20260930_014420/`,
`results/session_{a,b}_metrics_20260930_014420{,_guard2s}.json`.
