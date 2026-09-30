"""
_ids_worker.py — Desacopla a captura de pacotes da inferência do IDS.

Motivação (medido no VIM 4, set/2026): quando a inferência roda dentro do
callback de captura do netflower, a thread de captura fica cega durante cada
predição e o buffer do kernel (libpcap) transborda sob flood, descartando
pacotes. A perda é maior no pipeline hierárquico (P1+P2), o que distorcia a
comparação entre as sessões.

Correção: o callback de captura só enfileira o fluxo e retorna na hora. Uma
thread separada esvazia a fila em LOTES e roda a inferência em batch (cerca de
36x mais rápido por fluxo que uma predição por vez). A fila não tem limite: em
rajada ela cresce e depois drena, então todo fluxo capturado acaba avaliado,
mesmo que o processamento fique para trás do ataque por alguns instantes.

A profundidade máxima da fila é registrada, para o relatório poder dizer quanta
folga foi usada e se sobrou backlog no encerramento.
"""

import logging
import queue
import threading
import time

log = logging.getLogger(__name__)


class FlowInferenceWorker:
    """
    Fila sem limite prático + thread única que processa fluxos em lote.

    process_batch(batch) recebe uma lista de (t_arrival, flow), onde t_arrival é
    o time.perf_counter() do instante em que o fluxo foi enfileirado (para medir
    a latência ponta a ponta, incluindo a espera na fila). O chamador é quem faz
    a inferência e grava as linhas; este worker só cuida do enfileiramento, do
    lote e do ciclo de vida da thread.
    """

    def __init__(self, process_batch, max_batch: int = 512,
                 poll_timeout: float = 0.2) -> None:
        self._process_batch = process_batch
        self._max_batch = max_batch
        self._poll_timeout = poll_timeout
        self._q: "queue.Queue" = queue.Queue()  # sem maxsize: nunca bloqueia
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()   # drena o que resta e sai
        self._abort = threading.Event()  # para já, sem drenar (fim do dreno limitado)
        self._lock = threading.Lock()
        self.enqueued = 0
        self.processed = 0
        self.max_queue_depth = 0

    def submit(self, flow: dict) -> None:
        """Chamado pela thread de captura. Enfileira e retorna imediatamente."""
        self._q.put((time.perf_counter(), flow))
        depth = self._q.qsize()
        with self._lock:
            self.enqueued += 1
            if depth > self.max_queue_depth:
                self.max_queue_depth = depth

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while True:
            if self._abort.is_set():
                break
            try:
                first = self._q.get(timeout=self._poll_timeout)
            except queue.Empty:
                if self._stop.is_set():
                    break
                continue
            batch = [first]
            while len(batch) < self._max_batch:
                try:
                    batch.append(self._q.get_nowait())
                except queue.Empty:
                    break
            try:
                self._process_batch(batch)
            except Exception as e:  # nunca deixa a thread morrer por 1 lote ruim
                log.error("Batch de inferência falhou (%d fluxos): %s", len(batch), e)
            with self._lock:
                self.processed += len(batch)

    def stop(self, join_timeout: float = 30.0) -> int:
        """Sinaliza parada, drena por até join_timeout e junta a thread.

        Deve ser chamado DEPOIS de a captura ter feito flush_all (que enfileira
        os últimos fluxos). Sob flood o backlog pode não caber em join_timeout;
        nesse caso o dreno é abortado (o restante não é logado) para o
        encerramento não travar. Retorna o backlog residual não processado."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=join_timeout)
            if self._thread.is_alive():
                # Dreno estourou o tempo: aborta para não escrever depois do
                # [SUMMARY] nem segurar o processo indefinidamente.
                self._abort.set()
                self._thread.join(timeout=5.0)
        return self._q.qsize()

    def queue_depth(self) -> int:
        return self._q.qsize()
