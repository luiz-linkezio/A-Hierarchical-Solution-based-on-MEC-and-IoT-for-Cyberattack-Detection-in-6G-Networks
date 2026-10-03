"""Testes do FlowInferenceWorker: enfileiramento não bloqueia, tudo é
processado em lote, e a drenagem no stop() não perde fluxo."""

import os
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from _ids_worker import FlowInferenceWorker


def test_processes_every_submitted_flow():
    seen = []
    lock = threading.Lock()

    def process_batch(batch):
        with lock:
            seen.extend(f["id"] for _, f in batch)

    w = FlowInferenceWorker(process_batch, max_batch=16)
    w.start()
    for i in range(1000):
        w.submit({"id": i})
    residual = w.stop()

    assert residual == 0
    assert sorted(seen) == list(range(1000))
    assert w.enqueued == 1000
    assert w.processed == 1000


def test_batches_multiple_flows_together():
    sizes = []
    lock = threading.Lock()

    def process_batch(batch):
        with lock:
            sizes.append(len(batch))
        time.sleep(0.01)  # segura o worker para os próximos submits se acumularem

    w = FlowInferenceWorker(process_batch, max_batch=256)
    w.start()
    for i in range(500):
        w.submit({"id": i})
    w.stop()

    assert sum(sizes) == 500
    # Ao menos um lote deve ter juntado mais de um fluxo (senão não há batching).
    assert max(sizes) > 1


def test_tracks_max_queue_depth():
    started = threading.Event()
    release = threading.Event()

    def process_batch(batch):
        started.set()
        release.wait(timeout=5)

    w = FlowInferenceWorker(process_batch, max_batch=1)
    w.start()
    w.submit({"id": 0})
    started.wait(timeout=5)          # worker está preso no 1º lote
    for i in range(1, 51):
        w.submit({"id": i})          # estes empilham na fila
    depth = w.queue_depth()
    release.set()
    w.stop()

    assert depth >= 40               # a fila cresceu enquanto o worker estava ocupado
    assert w.max_queue_depth >= depth


def test_stop_bounds_drain_and_reports_residual():
    # Consumidor lento + backlog grande: stop() com join curto deve abortar o
    # dreno, não travar, e devolver o residual não processado (> 0).
    def process_batch(batch):
        time.sleep(0.2)

    w = FlowInferenceWorker(process_batch, max_batch=1)
    w.start()
    for i in range(200):
        w.submit({"id": i})
    t0 = time.perf_counter()
    residual = w.stop(join_timeout=0.5)
    elapsed = time.perf_counter() - t0

    assert elapsed < 8.0        # não trava esperando drenar tudo
    assert residual > 0         # sobrou backlog não processado
    assert w.processed < 200    # não processou tudo


def test_full_drain_processes_everything_despite_slow_consumer():
    # stop(join_timeout=None) deve drenar a fila por COMPLETO, sem descartar
    # nada, mesmo com um consumidor lento e backlog acumulado (residual = 0).
    seen = []
    lock = threading.Lock()

    def process_batch(batch):
        time.sleep(0.05)
        with lock:
            seen.extend(f["id"] for _, f in batch)

    w = FlowInferenceWorker(process_batch, max_batch=8)
    w.start()
    for i in range(300):
        w.submit({"id": i})
    residual = w.stop(join_timeout=None)

    assert residual == 0
    assert sorted(seen) == list(range(300))
    assert w.processed == 300


def test_full_drain_stall_guard_aborts_when_wedged():
    # Se a inferência emperrar de vez (consumidor travado), o dreno completo não
    # pode ficar preso para sempre: a guarda de estagnação aborta e devolve o
    # residual. stall_limit curto para o teste ser rápido.
    wedged = threading.Event()

    def process_batch(batch):
        wedged.wait(timeout=30)  # trava indefinidamente (dentro do teste)

    w = FlowInferenceWorker(process_batch, max_batch=1)
    w.start()
    for i in range(50):
        w.submit({"id": i})
    t0 = time.perf_counter()
    residual = w.stop(join_timeout=None, stall_limit=1.0)
    elapsed = time.perf_counter() - t0
    wedged.set()

    assert elapsed < 10.0   # não trava para sempre
    assert residual > 0     # sobrou backlog: o dreno foi abortado por estagnação


def test_submit_does_not_block_on_slow_consumer():
    def process_batch(batch):
        time.sleep(0.05)

    w = FlowInferenceWorker(process_batch, max_batch=1)
    w.start()
    t0 = time.perf_counter()
    for i in range(200):
        w.submit({"id": i})          # não deve esperar o consumidor lento
    submit_elapsed = time.perf_counter() - t0
    w.stop()

    assert submit_elapsed < 0.5      # 200 submits em muito menos que 200*0.05 s
