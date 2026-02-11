# Dataset Analysis Report
## Exploratory Dataset Analysis

This report presents a complete exploratory analysis of the CIC_IIoT_dataset_2025 dataset.

**Analysis Date**: 2026-02-11 01:55:30
**Dataset**: CIC_IIoT_dataset_2025
**Sample Size**: 685,671 records

---

## 1. Initial Dataset Characterization

### Dataset Dimensions
- **Rows**: 685,671
- **Columns**: 94

### Database Storage Size
- **Total database size**: 17416.53125 MB
- **Average size per row**: ~26634.57645 bytes

### Data Types
- **string**: 23 columns
- **float**: 47 columns
- **int**: 24 columns

### Column Names
Total: 94 features

1. device_name
2. device_mac
3. label_full
4. label1
5. label2
6. label3
7. label4
8. timestamp
9. timestamp_start
10. timestamp_end
11. log_data-ranges_avg
12. log_data-ranges_max
13. log_data-ranges_min
14. log_data-ranges_std_deviation
15. log_data-types
16. log_data-types_count
17. log_interval-messages
18. log_messages_count
19. network_fragmentation-score
20. network_fragmented-packets
21. network_header-length_avg
22. network_header-length_max
23. network_header-length_min
24. network_header-length_std_deviation
25. network_interval-packets
26. network_ip-flags_avg
27. network_ip-flags_max
28. network_ip-flags_min
29. network_ip-flags_std_deviation
30. network_ip-length_avg
31. network_ip-length_max
32. network_ip-length_min
33. network_ip-length_std_deviation
34. network_ips_all
35. network_ips_all_count
36. network_ips_dst
37. network_ips_dst_count
38. network_ips_src
39. network_ips_src_count
40. network_macs_all
41. network_macs_all_count
42. network_macs_dst
43. network_macs_dst_count
44. network_macs_src
45. network_macs_src_count
46. network_mss_avg
47. network_mss_max
48. network_mss_min
49. network_mss_std_deviation
50. network_packet-size_avg
51. network_packet-size_max
52. network_packet-size_min
53. network_packet-size_std_deviation
54. network_packets_all_count
55. network_packets_dst_count
56. network_packets_src_count
57. network_payload-length_avg
58. network_payload-length_max
59. network_payload-length_min
60. network_payload-length_std_deviation
61. network_ports_all
62. network_ports_all_count
63. network_ports_dst
64. network_ports_dst_count
65. network_ports_src
66. network_ports_src_count
67. network_protocols_all
68. network_protocols_all_count
69. network_protocols_dst
70. network_protocols_dst_count
71. network_protocols_src
72. network_protocols_src_count
73. network_tcp-flags-ack_count
74. network_tcp-flags-fin_count
75. network_tcp-flags-psh_count
76. network_tcp-flags-rst_count
77. network_tcp-flags-syn_count
78. network_tcp-flags-urg_count
79. network_tcp-flags_avg
80. network_tcp-flags_max
81. network_tcp-flags_min
82. network_tcp-flags_std_deviation
83. network_time-delta_avg
84. network_time-delta_max
85. network_time-delta_min
86. network_time-delta_std_deviation
87. network_ttl_avg
88. network_ttl_max
89. network_ttl_min
90. network_ttl_std_deviation
91. network_window-size_avg
92. network_window-size_max
93. network_window-size_min
94. network_window-size_std_deviation

---

## 2. Data Quality Analysis

### General Summary
- **Columns with missing values**: 0
- **Total missing values**: 0
- **Average completeness percentage**: 100.00000%

### Duplicate Analysis

- **Duplicate records**: 0
- **Duplicate percentage**: 0.00000%
- **Unique records**: 685,671

✓ **No duplicates found**

---

## 3. Descriptive Statistics

### Feature Classification
- **Numeric**: 71
- **Categorical**: 23

### Descriptive Statistics - Numeric-Like Features (Mean, Std, Min, Max)

| Column | Count | Mean | Std | Min | Max |
|--------|-------|------|-----|-----|-----|
| network_time-delta_avg | 685,671 | 0.0095 | 0.0176 | -0.0 | 0.4091 |
| network_protocols_src_count | 685,671 | 1.5337 | 1.416 | 0.0 | 14.0 |
| network_tcp-flags-psh_count | 685,671 | 3149.4591 | 39898.0425 | 0.0 | 1144412.0 |
| network_ttl_max | 685,671 | 150.3535 | 116.0116 | 0.0 | 255.0 |
| network_ips_dst_count | 685,671 | 5.9807 | 23.622 | 0.0 | 260.0 |
| network_payload-length_avg | 685,671 | 111.7519 | 298.7817 | 0.0 | 2429.8333 |
| network_ip-length_avg | 685,671 | 116.7877 | 218.6081 | 0.0 | 2481.8333 |
| network_fragmentation-score | 685,671 | 0.4664 | 2.2919 | 0.0 | 13.08 |
| log_data-ranges_min | 685,671 | 57.3982 | 210.0542 | -0.94 | 2000.0 |
| network_packets_src_count | 685,671 | 1884.8546 | 15513.8198 | 0.0 | 637142.0 |
| network_ips_src_count | 685,671 | 3.5791 | 6.484 | 0.0 | 78.0 |
| network_mss_min | 685,671 | 266.6931 | 562.4755 | 0.0 | 1460.0 |
| network_header-length_max | 685,671 | 14.4844 | 8.9508 | 0.0 | 24.0 |
| log_interval-messages | 685,671 | 133.5741 | 346.989 | 0.0 | 9995.0 |
| network_ip-flags_max | 685,671 | 1.0606 | 0.9819 | 0.0 | 2.0 |
| network_packets_dst_count | 685,671 | 26906.9448 | 115622.6209 | 0.0 | 1487601.0 |
| network_ttl_avg | 685,671 | 97.4668 | 83.3519 | 0.0 | 255.0 |
| network_tcp-flags-ack_count | 685,671 | 4819.9003 | 42086.3376 | 0.0 | 1149957.0 |
| network_window-size_avg | 685,671 | 11033.8624 | 15960.2888 | 0.0 | 65535.0 |
| network_tcp-flags_max | 685,671 | 16.9472 | 100.7973 | 0.0 | 2242.0 |

*Showing top 20 of 71 numeric-like features*

### Descriptive Statistics - Categorical Features

| Column | Count | Unique_Values | Mode | Mode_Frequency | Mode_Percent |
|--------|-------|---------------|------|----------------|-------------|
| device_name | 685671 | 38 | mqtt-broker | 39,136 | 5.71000% |
| device_mac | 685671 | 38 | dc:a6:32:dc:28:46 | 39,136 | 5.71000% |
| label_full | 685671 | 937 | benign_whole-network3 | 400,672 | 58.44000% |
| label1 | 685671 | 2 | benign | 400,672 | 58.44000% |
| label2 | 685671 | 8 | benign | 400,672 | 58.44000% |
| label3 | 685671 | 61 | benign | 400,672 | 58.44000% |
| label4 | 685671 | 84 | benign | 400,672 | 58.44000% |
| timestamp | 685671 | 290007 | 2025-09-09T15:09:39.400000Z_2025-09-09T15:09:40.400000Z | 38 | 0.01000% |
| timestamp_start | 685671 | 92136 | 2025-09-09T14:51:40.400000Z | 380 | 0.06000% |
| timestamp_end | 685671 | 92136 | 2025-09-09T14:51:40.400000Z | 380 | 0.06000% |
| log_data-types | 685671 | 7 | [] | 515,764 | 75.22000% |
| network_ips_all | 685671 | 62426 | [] | 146,212 | 21.32000% |
| network_ips_dst | 685671 | 61777 | [] | 146,212 | 21.32000% |
| network_ips_src | 685671 | 60642 | [] | 146,212 | 21.32000% |
| network_macs_all | 685671 | 58491 | [] | 137,326 | 20.03000% |
| network_macs_dst | 685671 | 56865 | [] | 137,326 | 20.03000% |
| network_macs_src | 685671 | 53846 | [] | 137,326 | 20.03000% |
| network_ports_all | 685671 | 205883 | [] | 206,038 | 30.05000% |
| network_ports_dst | 685671 | 186137 | [] | 206,038 | 30.05000% |
| network_ports_src | 685671 | 202188 | [] | 206,038 | 30.05000% |

*Showing top 20 of 23 categorical features*

---

## 4. Class Distribution Analysis

### Distribution of column 'label_full'

| Class | Count | Percent |
|-------|-------|----------|
| benign_whole-network3 | 400,672 | 58.43502% |
| attack_recon_os-scan_whole-network | 7,115 | 1.03767% |
| attack_recon_host-disc-tcp-ack-ping_whole-network | 7,056 | 1.02906% |
| attack_recon_vuln-scan_whole-network | 7,041 | 1.02688% |
| attack_recon_host-disc-tcp-syn-ping_whole-network | 6,991 | 1.01959% |
| attack_recon_port-scan_whole-network | 6,962 | 1.01536% |
| attack_recon_ping-sweep_whole-network | 6,955 | 1.01433% |
| attack_recon_host-disc-tcp-syn-stealth_whole-network | 6,923 | 1.00967% |
| attack_recon_host-disc-arp-ping_whole-network | 6,915 | 1.00850% |
| attack_recon_host-disc-udp-ping_whole-network | 6,880 | 1.00340% |
| attack_web_command-injection_edge1 | 3,226 | 0.47049% |
| attack_web_sql-injection-blind_edge1 | 3,206 | 0.46757% |
| attack_malware_mirai-udp-flood_steam-sensor--edge1,mqtt-broker | 2,345 | 0.34200% |
| attack_malware_mirai-syn-flood_ap--edge1,mqtt-broker | 2,106 | 0.30714% |
| attack_malware_mirai-udp-flood_yi-camera--edge1,mqtt-broker | 1,668 | 0.24327% |
| attack_malware_mirai-udp-flood_ap--edge1,mqtt-broker | 1,646 | 0.24006% |
| attack_malware_mirai-udp-flood_wisenet-camera--edge1,mqtt-broker | 1,628 | 0.23743% |
| attack_malware_mirai-syn-flood_router--edge1,mqtt-broker | 1,590 | 0.23189% |
| attack_malware_mirai-udp-flood_router--edge1,mqtt-broker | 1,506 | 0.21964% |
| attack_malware_mirai-udp-flood_weather-sensor--edge1,mqtt-broker | 1,456 | 0.21235% |
| attack_malware_mirai-syn-flood_motion-sensor--edge1,mqtt-broker | 1,434 | 0.20914% |
| attack_malware_mirai-udp-flood_motion-sensor--edge1,mqtt-broker | 1,410 | 0.20564% |
| attack_malware_mirai-syn-flood_wisenet-camera--edge1,mqtt-broker | 1,379 | 0.20112% |
| attack_malware_mirai-syn-flood_yi-camera--edge1,mqtt-broker | 1,312 | 0.19135% |
| attack_web_sql-injection_edge1 | 1,240 | 0.18084% |
| attack_malware_mirai-syn-flood_mqtt-broker--edge1 | 1,218 | 0.17764% |
| attack_malware_mirai-udp-flood_mqtt-broker--edge1 | 1,210 | 0.17647% |
| attack_malware_mirai-syn-flood_steam-sensor--edge1,mqtt-broker | 1,150 | 0.16772% |
| attack_malware_mirai-syn-flood_weather-sensor--edge1,mqtt-broker | 1,119 | 0.16320% |
| attack_bruteforce_dictionary-telnet_mqtt-broker | 971 | 0.14161% |
| attack_bruteforce_dictionary-telnet_edge1 | 971 | 0.14161% |
| attack_bruteforce_dictionary-telnet_ap | 971 | 0.14161% |
| attack_bruteforce_dictionary-ssh_mqtt-broker | 971 | 0.14161% |
| attack_bruteforce_dictionary-ssh_edge1 | 971 | 0.14161% |
| attack_mitm_arp-spoofing_mqtt-broker--water-sensor | 774 | 0.11288% |
| attack_mitm_arp-spoofing_mqtt-broker--sound-sensor | 774 | 0.11288% |
| attack_mitm_arp-spoofing_mqtt-broker--soil-sensor | 774 | 0.11288% |
| attack_mitm_arp-spoofing_mqtt-broker--weather-sensor | 773 | 0.11274% |
| attack_mitm_arp-spoofing_mqtt-broker--ultrasonic-sensor | 773 | 0.11274% |
| attack_mitm_arp-spoofing_mqtt-broker--steam-sensor | 773 | 0.11274% |
| attack_mitm_arp-spoofing_mqtt-broker--light-sensor | 773 | 0.11274% |
| attack_mitm_arp-spoofing_mqtt-broker--gas-sensor | 773 | 0.11274% |
| attack_mitm_arp-spoofing_mqtt-broker--accelerometer-sensor | 773 | 0.11274% |
| attack_mitm_arp-spoofing_mqtt-broker--motion-sensor | 758 | 0.11055% |
| attack_mitm_arp-spoofing_mqtt-broker--flame-sensor | 758 | 0.11055% |
| attack_mitm_arp-spoofing_mqtt-broker--rfid-sensor | 754 | 0.10997% |
| attack_mitm_arp-spoofing_mqtt-broker--proximity-collision-sensor | 754 | 0.10997% |
| attack_mitm_arp-spoofing_mqtt-broker--vibration-sensor | 751 | 0.10953% |
| attack_web_xss_edge1 | 698 | 0.10180% |
| attack_web_backdoor-upload_edge1 | 670 | 0.09771% |
| attack_mitm_ip-spoofing_mqtt-broker--sound-sensor | 388 | 0.05659% |
| attack_bruteforce_dictionary-ssh_switch | 387 | 0.05644% |
| attack_bruteforce_dictionary-ssh_router | 387 | 0.05644% |
| attack_bruteforce_dictionary-ssh_ap | 387 | 0.05644% |
| attack_mitm_ip-spoofing_router--yi-camera | 386 | 0.05630% |
| attack_mitm_ip-spoofing_router--wisenet-camera | 386 | 0.05630% |
| attack_mitm_ip-spoofing_mqtt-broker--proximity-collision-sensor | 386 | 0.05630% |
| attack_mitm_ip-spoofing_mqtt-broker--gas-sensor | 386 | 0.05630% |
| attack_mitm_ip-spoofing_router--plug-all-cameras | 384 | 0.05600% |
| attack_mitm_ip-spoofing_router--mqtt-broker | 384 | 0.05600% |
| attack_mitm_ip-spoofing_router--blurams-camera | 384 | 0.05600% |
| attack_mitm_ip-spoofing_mqtt-broker--weather-sensor | 384 | 0.05600% |
| attack_mitm_ip-spoofing_mqtt-broker--water-sensor | 384 | 0.05600% |
| attack_mitm_ip-spoofing_mqtt-broker--ultrasonic-sensor | 384 | 0.05600% |
| attack_mitm_ip-spoofing_mqtt-broker--steam-sensor | 384 | 0.05600% |
| attack_mitm_ip-spoofing_mqtt-broker--soil-sensor | 384 | 0.05600% |
| attack_mitm_ip-spoofing_mqtt-broker--light-sensor | 384 | 0.05600% |
| attack_mitm_ip-spoofing_mqtt-broker--flame-sensor | 384 | 0.05600% |
| attack_mitm_ip-spoofing_mqtt-broker--accelerometer-sensor | 384 | 0.05600% |
| attack_mitm_arp-spoofing_router--myq-camera | 384 | 0.05600% |
| attack_mitm_arp-spoofing_router--mqtt-broker | 384 | 0.05600% |
| attack_mitm_arp-spoofing_router--geeni-camera | 384 | 0.05600% |
| attack_mitm_ip-spoofing_router--geeni-camera | 383 | 0.05586% |
| attack_mitm_arp-spoofing_router--blurams-camera | 383 | 0.05586% |
| attack_mitm_ip-spoofing_router--dekco-camera | 377 | 0.05498% |
| attack_mitm_ip-spoofing_router--switch | 375 | 0.05469% |
| attack_mitm_ip-spoofing_router--myq-camera | 375 | 0.05469% |
| attack_mitm_ip-spoofing_router--edge1 | 375 | 0.05469% |
| attack_mitm_ip-spoofing_router--ap | 375 | 0.05469% |
| attack_mitm_ip-spoofing_mqtt-broker--vibration-sensor | 375 | 0.05469% |
| attack_mitm_ip-spoofing_mqtt-broker--rfid-sensor | 375 | 0.05469% |
| attack_mitm_ip-spoofing_mqtt-broker--motion-sensor | 375 | 0.05469% |
| attack_mitm_arp-spoofing_router--yi-camera | 373 | 0.05440% |
| attack_mitm_arp-spoofing_router--dekco-camera | 373 | 0.05440% |
| attack_mitm_arp-spoofing_router--edge1 | 371 | 0.05411% |
| attack_recon_port-scan_dekco-camera | 194 | 0.02829% |
| attack_dos_udp-frag-flood_water-sensor | 194 | 0.02829% |
| attack_dos_udp-frag-flood_vibration-sensor | 194 | 0.02829% |
| attack_dos_udp-frag-flood_rfid-sensor | 194 | 0.02829% |
| attack_dos_udp-frag-flood_mqtt-broker | 194 | 0.02829% |
| attack_dos_udp-frag-flood_blurams-camera | 194 | 0.02829% |
| attack_dos_udp-flood_yi-camera | 194 | 0.02829% |
| attack_dos_udp-flood_wisenet-camera | 194 | 0.02829% |
| attack_dos_udp-flood_weather-sensor | 194 | 0.02829% |
| attack_dos_udp-flood_vibration-sensor | 194 | 0.02829% |
| attack_dos_udp-flood_ultrasonic-sensor | 194 | 0.02829% |
| attack_dos_udp-flood_switch | 194 | 0.02829% |
| attack_dos_udp-flood_steam-sensor | 194 | 0.02829% |
| attack_dos_udp-flood_soil-sensor | 194 | 0.02829% |
| attack_dos_udp-flood_proximity-collision-sensor | 194 | 0.02829% |
| attack_dos_udp-flood_plug-proximity | 194 | 0.02829% |
| attack_dos_udp-flood_plug-all-cameras | 194 | 0.02829% |
| attack_dos_udp-flood_motion-sensor | 194 | 0.02829% |
| attack_dos_udp-flood_dekco-camera | 194 | 0.02829% |
| attack_dos_udp-flood_accelerometer-sensor | 194 | 0.02829% |
| attack_dos_tcp-flood-port-80_plug-proximity | 194 | 0.02829% |
| attack_dos_tcp-flood-port-80_plug-cameras-dekco-blurams | 194 | 0.02829% |
| attack_dos_tcp-flood-port-1883_water-sensor | 194 | 0.02829% |
| attack_dos_tcp-flood-port-1883_ultrasonic-sensor | 194 | 0.02829% |
| attack_dos_tcp-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_dos_tcp-flood-port-1883_soil-sensor | 194 | 0.02829% |
| attack_dos_tcp-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_dos_tcp-flood-port-1883_flame-sensor | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-80_wisenet-camera | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-80_geeni-camera | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-80_blurams-camera | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-1883_weather-sensor | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-1883_vibration-sensor | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-1883_ultrasonic-sensor | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-1883_motion-sensor | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-1883_gas-sensor | 194 | 0.02829% |
| attack_dos_synonymousip-flood-port-1883_flame-sensor | 194 | 0.02829% |
| attack_dos_syn-flood-port-80_router | 194 | 0.02829% |
| attack_dos_syn-flood-port-1883_rfid-sensor | 194 | 0.02829% |
| attack_dos_syn-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_dos_syn-flood-port-1883_motion-sensor | 194 | 0.02829% |
| attack_dos_syn-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-80_plug-proximity | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_soil-sensor | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_rfid-sensor | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_proximity-collision-sensor | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_myq-camera | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_motion-sensor | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_dekco-camera | 194 | 0.02829% |
| attack_dos_rst-fin-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-80_plug-cameras-dekco-blurams | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-1883_weather-sensor | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-1883_water-sensor | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-1883_sound-sensor | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-1883_soil-sensor | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-1883_flame-sensor | 194 | 0.02829% |
| attack_dos_push-ack-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_water-sensor | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_vibration-sensor | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_switch | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_steam-sensor | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_proximity-collision-sensor | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_mqtt-broker | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_motion-sensor | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_gas-sensor | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_edge1 | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_dekco-camera | 194 | 0.02829% |
| attack_dos_icmp-frag-flood_blurams-camera | 194 | 0.02829% |
| attack_dos_icmp-flood_wisenet-camera | 194 | 0.02829% |
| attack_dos_icmp-flood_water-sensor | 194 | 0.02829% |
| attack_dos_icmp-flood_vibration-sensor | 194 | 0.02829% |
| attack_dos_icmp-flood_sound-sensor | 194 | 0.02829% |
| attack_dos_icmp-flood_motion-sensor | 194 | 0.02829% |
| attack_dos_icmp-flood_edge1 | 194 | 0.02829% |
| attack_dos_icmp-flood_ap | 194 | 0.02829% |
| attack_dos_http-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-80_wisenet-camera | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-80_switch | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-80_myq-camera | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-80_edge1 | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-80_blurams-camera | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-1883_water-sensor | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-1883_soil-sensor | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-1883_light-sensor | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-1883_gas-sensor | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-1883_flame-sensor | 194 | 0.02829% |
| attack_dos_ack-frag-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_yi-camera | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_wisenet-camera | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_water-sensor | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_vibration-sensor | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_ultrasonic-sensor | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_steam-sensor | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_soil-sensor | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_motion-sensor | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_edge1 | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_dekco-camera | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_blurams-camera | 194 | 0.02829% |
| attack_ddos_udp-frag-flood_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_udp-flood-port-80_yi-camera | 194 | 0.02829% |
| attack_ddos_udp-flood-port-80_wisenet-camera | 194 | 0.02829% |
| attack_ddos_udp-flood-port-80_router | 194 | 0.02829% |
| attack_ddos_udp-flood-port-80_plug-all-sensors | 194 | 0.02829% |
| attack_ddos_udp-flood-port-80_ap | 194 | 0.02829% |
| attack_ddos_udp-flood-port-1883_weather-sensor | 194 | 0.02829% |
| attack_ddos_udp-flood-port-1883_water-sensor | 194 | 0.02829% |
| attack_ddos_udp-flood-port-1883_vibration-sensor | 194 | 0.02829% |
| attack_ddos_udp-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_ddos_udp-flood-port-1883_soil-sensor | 194 | 0.02829% |
| attack_ddos_udp-flood-port-1883_rfid-sensor | 194 | 0.02829% |
| attack_ddos_udp-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-80_yi-camera | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-80_switch | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-80_myq-camera | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-80_dekco-camera | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-80_blurams-camera | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-80_ap | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-1883_sound-sensor | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-1883_rfid-sensor | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-1883_light-sensor | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-1883_gas-sensor | 194 | 0.02829% |
| attack_ddos_tcp-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-80_yi-camera | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-80_wisenet-camera | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-80_switch | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-80_router | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-80_myq-camera | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-80_edge1 | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-80_ap | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_weather-sensor | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_soil-sensor | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_rfid-sensor | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_motion-sensor | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_light-sensor | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_gas-sensor | 194 | 0.02829% |
| attack_ddos_synonymousip-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_syn-flood-port-80_edge1 | 194 | 0.02829% |
| attack_ddos_syn-flood-port-80_dekco-camera | 194 | 0.02829% |
| attack_ddos_syn-flood-port-1883_weather-sensor | 194 | 0.02829% |
| attack_ddos_syn-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_ddos_syn-flood-port-1883_soil-sensor | 194 | 0.02829% |
| attack_ddos_syn-flood-port-1883_proximity-collision-sensor | 194 | 0.02829% |
| attack_ddos_syn-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_ddos_syn-flood-port-1883_gas-sensor | 194 | 0.02829% |
| attack_ddos_syn-flood-port-1883_flame-sensor | 194 | 0.02829% |
| attack_ddos_syn-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-80_switch | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-80_router | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-80_plug-all-rpb | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-80_myq-camera | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-80_blurams-camera | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-80_ap | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_weather-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_water-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_vibration-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_ultrasonic-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_soil-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_rfid-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_proximity-collision-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_flame-sensor | 194 | 0.02829% |
| attack_ddos_rst-fin-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-80_router | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-80_edge1 | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-80_dekco-camera | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-80_ap | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-1883_ultrasonic-sensor | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-1883_motion-sensor | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-1883_light-sensor | 194 | 0.02829% |
| attack_ddos_push-ack-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_icmp-frag-flood_wisenet-camera | 194 | 0.02829% |
| attack_ddos_icmp-frag-flood_sound-sensor | 194 | 0.02829% |
| attack_ddos_icmp-frag-flood_light-sensor | 194 | 0.02829% |
| attack_ddos_icmp-frag-flood_flame-sensor | 194 | 0.02829% |
| attack_ddos_icmp-frag-flood_dekco-camera | 194 | 0.02829% |
| attack_ddos_icmp-frag-flood_accelerometer-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_yi-camera | 194 | 0.02829% |
| attack_ddos_icmp-flood_weather-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_water-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_ultrasonic-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_steam-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_soil-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_router | 194 | 0.02829% |
| attack_ddos_icmp-flood_proximity-collision-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_myq-camera | 194 | 0.02829% |
| attack_ddos_icmp-flood_light-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_flame-sensor | 194 | 0.02829% |
| attack_ddos_icmp-flood_blurams-camera | 194 | 0.02829% |
| attack_ddos_icmp-flood_ap | 194 | 0.02829% |
| attack_ddos_http-flood-port-80_wisenet-camera | 194 | 0.02829% |
| attack_ddos_http-flood-port-80_edge1 | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-80_yi-camera | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-80_switch | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-80_router | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-80_dekco-camera | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_weather-sensor | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_water-sensor | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_ultrasonic-sensor | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_steam-sensor | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_sound-sensor | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_mqtt-broker | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_light-sensor | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_flame-sensor | 194 | 0.02829% |
| attack_ddos_ack-frag-flood-port-1883_accelerometer-sensor | 194 | 0.02829% |
| attack_recon_vuln-scan_yi-camera | 192 | 0.02800% |
| attack_recon_vuln-scan_wisenet-camera | 192 | 0.02800% |
| attack_recon_vuln-scan_weather-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_water-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_vibration-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_ultrasonic-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_switch | 192 | 0.02800% |
| attack_recon_vuln-scan_steam-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_sound-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_soil-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_router | 192 | 0.02800% |
| attack_recon_vuln-scan_rfid-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_proximity-collision-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_plug-vibration | 192 | 0.02800% |
| attack_recon_vuln-scan_plug-proximity | 192 | 0.02800% |
| attack_recon_vuln-scan_plug-flame | 192 | 0.02800% |
| attack_recon_vuln-scan_myq-camera | 192 | 0.02800% |
| attack_recon_vuln-scan_mqtt-broker | 192 | 0.02800% |
| attack_recon_vuln-scan_motion-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_light-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_geeni-camera | 192 | 0.02800% |
| attack_recon_vuln-scan_gas-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_flame-sensor | 192 | 0.02800% |
| attack_recon_vuln-scan_edge1 | 192 | 0.02800% |
| attack_recon_vuln-scan_dekco-camera | 192 | 0.02800% |
| attack_recon_vuln-scan_blurams-camera | 192 | 0.02800% |
| attack_recon_vuln-scan_ap | 192 | 0.02800% |
| attack_recon_vuln-scan_accelerometer-sensor | 192 | 0.02800% |
| attack_recon_port-scan_yi-camera | 192 | 0.02800% |
| attack_recon_port-scan_wisenet-camera | 192 | 0.02800% |
| attack_recon_port-scan_weather-sensor | 192 | 0.02800% |
| attack_recon_port-scan_water-sensor | 192 | 0.02800% |
| attack_recon_port-scan_vibration-sensor | 192 | 0.02800% |
| attack_recon_port-scan_ultrasonic-sensor | 192 | 0.02800% |
| attack_recon_port-scan_switch | 192 | 0.02800% |
| attack_recon_port-scan_steam-sensor | 192 | 0.02800% |
| attack_recon_port-scan_sound-sensor | 192 | 0.02800% |
| attack_recon_port-scan_soil-sensor | 192 | 0.02800% |
| attack_recon_port-scan_router | 192 | 0.02800% |
| attack_recon_port-scan_rfid-sensor | 192 | 0.02800% |
| attack_recon_port-scan_proximity-collision-sensor | 192 | 0.02800% |
| attack_recon_port-scan_plug-mqtt | 192 | 0.02800% |
| attack_recon_port-scan_plug-all-rpb | 192 | 0.02800% |
| attack_recon_port-scan_plug-all-cameras | 192 | 0.02800% |
| attack_recon_port-scan_myq-camera | 192 | 0.02800% |
| attack_recon_port-scan_mqtt-broker | 192 | 0.02800% |
| attack_recon_port-scan_motion-sensor | 192 | 0.02800% |
| attack_recon_port-scan_light-sensor | 192 | 0.02800% |
| attack_recon_port-scan_geeni-camera | 192 | 0.02800% |
| attack_recon_port-scan_gas-sensor | 192 | 0.02800% |
| attack_recon_port-scan_flame-sensor | 192 | 0.02800% |
| attack_recon_port-scan_edge1 | 192 | 0.02800% |
| attack_recon_port-scan_blurams-camera | 192 | 0.02800% |
| attack_recon_port-scan_ap | 192 | 0.02800% |
| attack_recon_port-scan_accelerometer-sensor | 192 | 0.02800% |
| attack_recon_os-scan_yi-camera | 192 | 0.02800% |
| attack_recon_os-scan_wisenet-camera | 192 | 0.02800% |
| attack_recon_os-scan_weather-sensor | 192 | 0.02800% |
| attack_recon_os-scan_water-sensor | 192 | 0.02800% |
| attack_recon_os-scan_vibration-sensor | 192 | 0.02800% |
| attack_recon_os-scan_ultrasonic-sensor | 192 | 0.02800% |
| attack_recon_os-scan_switch | 192 | 0.02800% |
| attack_recon_os-scan_steam-sensor | 192 | 0.02800% |
| attack_recon_os-scan_sound-sensor | 192 | 0.02800% |
| attack_recon_os-scan_soil-sensor | 192 | 0.02800% |
| attack_recon_os-scan_router | 192 | 0.02800% |
| attack_recon_os-scan_rfid-sensor | 192 | 0.02800% |
| attack_recon_os-scan_proximity-collision-sensor | 192 | 0.02800% |
| attack_recon_os-scan_plug-rfid | 192 | 0.02800% |
| attack_recon_os-scan_plug-motion | 192 | 0.02800% |
| attack_recon_os-scan_plug-edge1 | 192 | 0.02800% |
| attack_recon_os-scan_myq-camera | 192 | 0.02800% |
| attack_recon_os-scan_mqtt-broker | 192 | 0.02800% |
| attack_recon_os-scan_motion-sensor | 192 | 0.02800% |
| attack_recon_os-scan_light-sensor | 192 | 0.02800% |
| attack_recon_os-scan_geeni-camera | 192 | 0.02800% |
| attack_recon_os-scan_gas-sensor | 192 | 0.02800% |
| attack_recon_os-scan_flame-sensor | 192 | 0.02800% |
| attack_recon_os-scan_edge1 | 192 | 0.02800% |
| attack_recon_os-scan_dekco-camera | 192 | 0.02800% |
| attack_recon_os-scan_blurams-camera | 192 | 0.02800% |
| attack_recon_os-scan_ap | 192 | 0.02800% |
| attack_recon_os-scan_accelerometer-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_yi-camera | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_wisenet-camera | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_weather-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_water-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_vibration-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_ultrasonic-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_switch | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_steam-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_sound-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_soil-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_router | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_rfid-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_proximity-collision-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_plug-all-sensors | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_plug-all-rpb | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_plug-all-cameras | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_myq-camera | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_mqtt-broker | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_motion-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_light-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_geeni-camera | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_gas-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_flame-sensor | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_edge1 | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_dekco-camera | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_blurams-camera | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_ap | 192 | 0.02800% |
| attack_recon_host-disc-udp-ping_accelerometer-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_yi-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_wisenet-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_weather-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_water-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_vibration-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_ultrasonic-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_switch | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_steam-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_sound-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_soil-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_router | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_rfid-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_proximity-collision-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_plug-vibration | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_plug-proximity | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_plug-flame | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_myq-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_mqtt-broker | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_motion-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_light-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_geeni-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_gas-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_flame-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_edge1 | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_dekco-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_blurams-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_ap | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-stealth_accelerometer-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_yi-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_wisenet-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_weather-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_water-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_vibration-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_ultrasonic-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_switch | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_steam-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_sound-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_soil-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_router | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_rfid-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_proximity-collision-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_plug-cameras-yi | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_plug-cameras-geeni | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_plug-cameras-dekco-blurams | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_myq-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_mqtt-broker | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_motion-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_light-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_geeni-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_gas-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_flame-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_edge1 | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_dekco-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_blurams-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_ap | 192 | 0.02800% |
| attack_recon_host-disc-tcp-syn-ping_accelerometer-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_yi-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_wisenet-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_weather-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_water-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_vibration-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_ultrasonic-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_switch | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_steam-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_sound-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_soil-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_router | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_rfid-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_proximity-collision-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_plug-rfid | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_plug-all-rpb | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_plug-all-cameras | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_myq-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_mqtt-broker | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_motion-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_light-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_geeni-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_gas-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_flame-sensor | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_edge1 | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_dekco-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_blurams-camera | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_ap | 192 | 0.02800% |
| attack_recon_host-disc-tcp-ack-ping_accelerometer-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_yi-camera | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_wisenet-camera | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_weather-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_water-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_vibration-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_ultrasonic-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_switch | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_steam-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_sound-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_soil-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_router | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_rfid-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_proximity-collision-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_plug-rfid | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_plug-motion | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_plug-edge1 | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_myq-camera | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_mqtt-broker | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_motion-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_light-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_geeni-camera | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_gas-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_flame-sensor | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_edge1 | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_dekco-camera | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_blurams-camera | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_ap | 192 | 0.02800% |
| attack_recon_host-disc-arp-ping_accelerometer-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_yi-camera | 192 | 0.02800% |
| attack_dos_udp-frag-flood_wisenet-camera | 192 | 0.02800% |
| attack_dos_udp-frag-flood_weather-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_ultrasonic-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_switch | 192 | 0.02800% |
| attack_dos_udp-frag-flood_steam-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_sound-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_soil-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_router | 192 | 0.02800% |
| attack_dos_udp-frag-flood_proximity-collision-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_plug-flame | 192 | 0.02800% |
| attack_dos_udp-frag-flood_myq-camera | 192 | 0.02800% |
| attack_dos_udp-frag-flood_motion-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_light-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_geeni-camera | 192 | 0.02800% |
| attack_dos_udp-frag-flood_gas-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_flame-sensor | 192 | 0.02800% |
| attack_dos_udp-frag-flood_edge1 | 192 | 0.02800% |
| attack_dos_udp-frag-flood_dekco-camera | 192 | 0.02800% |
| attack_dos_udp-frag-flood_ap | 192 | 0.02800% |
| attack_dos_udp-frag-flood_accelerometer-sensor | 192 | 0.02800% |
| attack_dos_udp-flood_water-sensor | 192 | 0.02800% |
| attack_dos_udp-flood_sound-sensor | 192 | 0.02800% |
| attack_dos_udp-flood_router | 192 | 0.02800% |
| attack_dos_udp-flood_rfid-sensor | 192 | 0.02800% |
| attack_dos_udp-flood_plug-all-rpb | 192 | 0.02800% |
| attack_dos_udp-flood_myq-camera | 192 | 0.02800% |
| attack_dos_udp-flood_mqtt-broker | 192 | 0.02800% |
| attack_dos_udp-flood_light-sensor | 192 | 0.02800% |
| attack_dos_udp-flood_geeni-camera | 192 | 0.02800% |
| attack_dos_udp-flood_gas-sensor | 192 | 0.02800% |
| attack_dos_udp-flood_flame-sensor | 192 | 0.02800% |
| attack_dos_udp-flood_edge1 | 192 | 0.02800% |
| attack_dos_udp-flood_blurams-camera | 192 | 0.02800% |
| attack_dos_udp-flood_ap | 192 | 0.02800% |
| attack_dos_tcp-flood-port-80_switch | 192 | 0.02800% |
| attack_dos_tcp-flood-port-80_router | 192 | 0.02800% |
| attack_dos_tcp-flood-port-80_plug-cameras-yi | 192 | 0.02800% |
| attack_dos_tcp-flood-port-80_mqtt-broker | 192 | 0.02800% |
| attack_dos_tcp-flood-port-80_edge1 | 192 | 0.02800% |
| attack_dos_tcp-flood-port-80_ap | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_weather-sensor | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_rfid-sensor | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_dos_tcp-flood-port-1883_accelerometer-sensor | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_yi-camera | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_switch | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_router | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_plug-all-cameras | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_myq-camera | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_mqtt-broker | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_edge1 | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_dekco-camera | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-80_ap | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-1883_water-sensor | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-1883_soil-sensor | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-1883_rfid-sensor | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-1883_mqtt-broker | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_dos_synonymousip-flood-port-1883_accelerometer-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-80_switch | 192 | 0.02800% |
| attack_dos_syn-flood-port-80_plug-vibration | 192 | 0.02800% |
| attack_dos_syn-flood-port-80_plug-cameras-yi | 192 | 0.02800% |
| attack_dos_syn-flood-port-80_plug-cameras-geeni | 192 | 0.02800% |
| attack_dos_syn-flood-port-80_mqtt-broker | 192 | 0.02800% |
| attack_dos_syn-flood-port-80_edge1 | 192 | 0.02800% |
| attack_dos_syn-flood-port-80_ap | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_weather-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_water-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_steam-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_soil-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_dos_syn-flood-port-1883_flame-sensor | 192 | 0.02800% |
| attack_dos_slowloris-port-80_yi-camera | 192 | 0.02800% |
| attack_dos_slowloris-port-80_wisenet-camera | 192 | 0.02800% |
| attack_dos_slowloris-port-80_edge1 | 192 | 0.02800% |
| attack_dos_slowloris-port-8000_edge1 | 192 | 0.02800% |
| attack_dos_slowloris-port-554_wisenet-camera | 192 | 0.02800% |
| attack_dos_slowloris-port-1883_mqtt-broker | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-80_switch | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-80_router | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-80_edge1 | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-80_ap | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_yi-camera | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_wisenet-camera | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_weather-sensor | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_water-sensor | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_geeni-camera | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_flame-sensor | 192 | 0.02800% |
| attack_dos_rst-fin-flood-port-1883_blurams-camera | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_yi-camera | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_wisenet-camera | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_switch | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_router | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_myq-camera | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_edge1 | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_dekco-camera | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_blurams-camera | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-80_ap | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-1883_rfid-sensor | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_dos_push-ack-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_dos_mqtt-publish-flood_mqtt-broker | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_yi-camera | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_wisenet-camera | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_weather-sensor | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_ultrasonic-sensor | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_sound-sensor | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_soil-sensor | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_router | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_rfid-sensor | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_plug-all-cameras | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_myq-camera | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_light-sensor | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_geeni-camera | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_flame-sensor | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_ap | 192 | 0.02800% |
| attack_dos_icmp-frag-flood_accelerometer-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_yi-camera | 192 | 0.02800% |
| attack_dos_icmp-flood_weather-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_ultrasonic-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_switch | 192 | 0.02800% |
| attack_dos_icmp-flood_steam-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_soil-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_router | 192 | 0.02800% |
| attack_dos_icmp-flood_rfid-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_proximity-collision-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_plug-mqtt | 192 | 0.02800% |
| attack_dos_icmp-flood_plug-all-rpb | 192 | 0.02800% |
| attack_dos_icmp-flood_plug-all-cameras | 192 | 0.02800% |
| attack_dos_icmp-flood_myq-camera | 192 | 0.02800% |
| attack_dos_icmp-flood_mqtt-broker | 192 | 0.02800% |
| attack_dos_icmp-flood_light-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_geeni-camera | 192 | 0.02800% |
| attack_dos_icmp-flood_gas-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_flame-sensor | 192 | 0.02800% |
| attack_dos_icmp-flood_dekco-camera | 192 | 0.02800% |
| attack_dos_icmp-flood_blurams-camera | 192 | 0.02800% |
| attack_dos_icmp-flood_accelerometer-sensor | 192 | 0.02800% |
| attack_dos_http-flood-port-9595_myq-camera | 192 | 0.02800% |
| attack_dos_http-flood-port-80_wisenet-camera | 192 | 0.02800% |
| attack_dos_http-flood-port-80_switch | 192 | 0.02800% |
| attack_dos_http-flood-port-80_router | 192 | 0.02800% |
| attack_dos_http-flood-port-80_edge1 | 192 | 0.02800% |
| attack_dos_http-flood-port-80_ap | 192 | 0.02800% |
| attack_dos_http-flood-port-6668_plug-cameras-yi | 192 | 0.02800% |
| attack_dos_http-flood-port-6668_plug-all-rpb | 192 | 0.02800% |
| attack_dos_http-flood-port-6668_plug-all-cameras | 192 | 0.02800% |
| attack_dos_http-flood-port-6668_geeni-camera | 192 | 0.02800% |
| attack_dos_http-flood-port-554_wisenet-camera | 192 | 0.02800% |
| attack_dos_http-flood-port-443_wisenet-camera | 192 | 0.02800% |
| attack_dos_connect-flood_mqtt-broker | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-80_yi-camera | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-80_router | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-80_plug-all-cameras | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-80_dekco-camera | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-80_ap | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-1883_weather-sensor | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-1883_steam-sensor | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-1883_rfid-sensor | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_dos_ack-frag-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_weather-sensor | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_switch | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_sound-sensor | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_router | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_rfid-sensor | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_proximity-collision-sensor | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_plug-cameras-yi | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_myq-camera | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_mqtt-broker | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_light-sensor | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_geeni-camera | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_gas-sensor | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_flame-sensor | 192 | 0.02800% |
| attack_ddos_udp-frag-flood_ap | 192 | 0.02800% |
| attack_ddos_udp-flood-port-80_switch | 192 | 0.02800% |
| attack_ddos_udp-flood-port-80_myq-camera | 192 | 0.02800% |
| attack_ddos_udp-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_ddos_udp-flood-port-80_edge1 | 192 | 0.02800% |
| attack_ddos_udp-flood-port-80_dekco-camera | 192 | 0.02800% |
| attack_ddos_udp-flood-port-80_blurams-camera | 192 | 0.02800% |
| attack_ddos_udp-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_ddos_udp-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_ddos_udp-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_ddos_udp-flood-port-1883_mqtt-broker | 192 | 0.02800% |
| attack_ddos_udp-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_ddos_udp-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_ddos_udp-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_ddos_udp-flood-port-1883_flame-sensor | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-80_wisenet-camera | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-80_router | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-80_plug-all-rpb | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-80_edge1 | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-1883_weather-sensor | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-1883_water-sensor | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-1883_soil-sensor | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_ddos_tcp-flood-port-1883_flame-sensor | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-80_plug-proximity | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-80_dekco-camera | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-80_blurams-camera | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-1883_water-sensor | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_ddos_synonymousip-flood-port-1883_flame-sensor | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_yi-camera | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_wisenet-camera | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_switch | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_router | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_plug-all-cameras | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_myq-camera | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_blurams-camera | 192 | 0.02800% |
| attack_ddos_syn-flood-port-80_ap | 192 | 0.02800% |
| attack_ddos_syn-flood-port-1883_water-sensor | 192 | 0.02800% |
| attack_ddos_syn-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_ddos_syn-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_ddos_syn-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_ddos_syn-flood-port-1883_rfid-sensor | 192 | 0.02800% |
| attack_ddos_syn-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_ddos_syn-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_ddos_slowloris-port-80_yi-camera | 192 | 0.02800% |
| attack_ddos_slowloris-port-80_wisenet-camera | 192 | 0.02800% |
| attack_ddos_slowloris-port-80_edge1 | 192 | 0.02800% |
| attack_ddos_slowloris-port-8000_edge1 | 192 | 0.02800% |
| attack_ddos_slowloris-port-554_wisenet-camera | 192 | 0.02800% |
| attack_ddos_slowloris-port-1883_mqtt-broker | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-80_yi-camera | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-80_wisenet-camera | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-80_edge1 | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-80_dekco-camera | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-1883_steam-sensor | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-1883_mqtt-broker | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_ddos_rst-fin-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-80_yi-camera | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-80_wisenet-camera | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-80_switch | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-80_plug-cameras-geeni | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-80_myq-camera | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-80_blurams-camera | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_weather-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_water-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_soil-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_rfid-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_ddos_push-ack-flood-port-1883_flame-sensor | 192 | 0.02800% |
| attack_ddos_mqtt-publish-flood_mqtt-broker | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_yi-camera | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_weather-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_water-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_vibration-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_ultrasonic-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_switch | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_steam-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_soil-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_router | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_rfid-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_proximity-collision-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_plug-cameras-geeni | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_myq-camera | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_mqtt-broker | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_motion-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_geeni-camera | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_gas-sensor | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_edge1 | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_blurams-camera | 192 | 0.02800% |
| attack_ddos_icmp-frag-flood_ap | 192 | 0.02800% |
| attack_ddos_icmp-flood_wisenet-camera | 192 | 0.02800% |
| attack_ddos_icmp-flood_vibration-sensor | 192 | 0.02800% |
| attack_ddos_icmp-flood_switch | 192 | 0.02800% |
| attack_ddos_icmp-flood_sound-sensor | 192 | 0.02800% |
| attack_ddos_icmp-flood_rfid-sensor | 192 | 0.02800% |
| attack_ddos_icmp-flood_plug-rfid | 192 | 0.02800% |
| attack_ddos_icmp-flood_mqtt-broker | 192 | 0.02800% |
| attack_ddos_icmp-flood_motion-sensor | 192 | 0.02800% |
| attack_ddos_icmp-flood_geeni-camera | 192 | 0.02800% |
| attack_ddos_icmp-flood_gas-sensor | 192 | 0.02800% |
| attack_ddos_icmp-flood_edge1 | 192 | 0.02800% |
| attack_ddos_icmp-flood_dekco-camera | 192 | 0.02800% |
| attack_ddos_icmp-flood_accelerometer-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_yi-camera | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_switch | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_router | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_plug-proximity | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_myq-camera | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_dekco-camera | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_blurams-camera | 192 | 0.02800% |
| attack_ddos_http-flood-port-80_ap | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_weather-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_water-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_ultrasonic-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_steam-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_sound-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_soil-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_rfid-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_mqtt-broker | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_light-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_flame-sensor | 192 | 0.02800% |
| attack_ddos_http-flood-port-1883_accelerometer-sensor | 192 | 0.02800% |
| attack_ddos_connect-flood_mqtt-broker | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-80_wisenet-camera | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-80_plug-vibration | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-80_myq-camera | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-80_geeni-camera | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-80_edge1 | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-80_blurams-camera | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-80_ap | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-1883_vibration-sensor | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-1883_soil-sensor | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-1883_rfid-sensor | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-1883_proximity-collision-sensor | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-1883_motion-sensor | 192 | 0.02800% |
| attack_ddos_ack-frag-flood-port-1883_gas-sensor | 192 | 0.02800% |
| attack_mitm_impersonation_weather-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_water-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_vibration-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_ultrasonic-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_steam-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_sound-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_soil-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_rfid-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_proximity-collision-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_motion-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_light-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_gas-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_flame-sensor | 183 | 0.02669% |
| attack_mitm_impersonation_accelerometer-sensor | 183 | 0.02669% |
| attack_dos_tcp-flood-port-80_blurams-camera | 98 | 0.01429% |
| attack_dos_tcp-flood-port-554_geeni-camera | 98 | 0.01429% |
| attack_dos_tcp-flood-port-443_edge1 | 98 | 0.01429% |
| attack_dos_syn-flood-port-80_dekco-camera | 98 | 0.01429% |
| attack_dos_syn-flood-port-554_dekco-camera | 98 | 0.01429% |
| attack_dos_syn-flood-port-443_router | 98 | 0.01429% |
| attack_dos_syn-flood-port-22_mqtt-broker | 98 | 0.01429% |
| attack_dos_syn-flood-port-22_edge1 | 98 | 0.01429% |
| attack_dos_tcp-flood-port-80_yi-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-80_wisenet-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-80_myq-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-80_geeni-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-80_dekco-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-554_yi-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-554_wisenet-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-554_myq-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-554_dekco-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-554_blurams-camera | 94 | 0.01371% |
| attack_dos_tcp-flood-port-443_router | 94 | 0.01371% |
| attack_dos_tcp-flood-port-443_mqtt-broker | 94 | 0.01371% |
| attack_dos_tcp-flood-port-443_ap | 94 | 0.01371% |
| attack_dos_tcp-flood-port-23_switch | 94 | 0.01371% |
| attack_dos_tcp-flood-port-23_router | 94 | 0.01371% |
| attack_dos_tcp-flood-port-22_mqtt-broker | 94 | 0.01371% |
| attack_dos_tcp-flood-port-22_edge1 | 94 | 0.01371% |
| attack_dos_syn-flood-port-80_yi-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-80_wisenet-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-80_myq-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-80_geeni-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-80_blurams-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-557_wisenet-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-554_yi-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-554_myq-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-554_geeni-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-554_blurams-camera | 94 | 0.01371% |
| attack_dos_syn-flood-port-443_mqtt-broker | 94 | 0.01371% |
| attack_dos_syn-flood-port-443_edge1 | 94 | 0.01371% |
| attack_dos_syn-flood-port-443_ap | 94 | 0.01371% |
| attack_dos_syn-flood-port-23_switch | 94 | 0.01371% |
| attack_dos_syn-flood-port-23_router | 94 | 0.01371% |

**Summary:**
- **Total classes**: 937
- **Most frequent class**: benign_whole-network3 (58.43502%)
- **Least frequent class**: attack_dos_syn-flood-port-23_router (0.01371%)
- **Imbalance ratio**: 4262.46809:1

⚠️ **Highly imbalanced dataset!**

### Distribution of column 'label1'

| Class | Count | Percent |
|-------|-------|----------|
| benign | 400,672 | 58.43502% |
| attack | 284,999 | 41.56498% |

**Summary:**
- **Total classes**: 2
- **Most frequent class**: benign (58.43502%)
- **Least frequent class**: attack (41.56498%)
- **Imbalance ratio**: 1.40587:1

✓ **Relatively balanced dataset**

### Distribution of column 'label2'

| Class | Count | Percent |
|-------|-------|----------|
| benign | 400,672 | 58.43502% |
| recon | 105,848 | 15.43714% |
| dos | 57,736 | 8.42036% |
| ddos | 56,692 | 8.26811% |
| mitm | 25,490 | 3.71753% |
| malware | 24,177 | 3.52604% |
| web | 9,040 | 1.31842% |
| bruteforce | 6,016 | 0.87739% |

**Summary:**
- **Total classes**: 8
- **Most frequent class**: benign (58.43502%)
- **Least frequent class**: bruteforce (0.87739%)
- **Imbalance ratio**: 66.60106:1

⚠️ **Highly imbalanced dataset!**

### Distribution of column 'label3'

| Class | Count | Percent |
|-------|-------|----------|
| benign | 400,672 | 58.43502% |
| arp-spoofing | 13,387 | 1.95239% |
| mirai-udp-flood | 12,869 | 1.87685% |
| os-scan | 12,491 | 1.82172% |
| host-disc-tcp-ack-ping | 12,432 | 1.81311% |
| vuln-scan | 12,417 | 1.81093% |
| host-disc-tcp-syn-ping | 12,367 | 1.80363% |
| port-scan | 12,340 | 1.79970% |
| host-disc-tcp-syn-stealth | 12,299 | 1.79372% |
| host-disc-arp-ping | 12,291 | 1.79255% |
| host-disc-udp-ping | 12,256 | 1.78745% |
| mirai-syn-flood | 11,308 | 1.64919% |
| icmp-flood | 10,408 | 1.51793% |
| udp-frag-flood | 10,018 | 1.46105% |
| icmp-frag-flood | 10,018 | 1.46105% |
| ip-spoofing | 9,541 | 1.39148% |
| ping-sweep | 6,955 | 1.01433% |
| rst-fin-flood-port-1883 | 6,948 | 1.01331% |
| synonymousip-flood-port-1883 | 5,792 | 0.84472% |
| ack-frag-flood-port-1883 | 5,792 | 0.84472% |
| push-ack-flood-port-1883 | 5,788 | 0.84414% |
| tcp-flood-port-1883 | 5,786 | 0.84384% |
| syn-flood-port-1883 | 5,784 | 0.84355% |
| udp-flood | 5,404 | 0.78813% |
| synonymousip-flood-port-80 | 4,436 | 0.64696% |
| ack-frag-flood-port-80 | 4,242 | 0.61866% |
| push-ack-flood-port-80 | 4,234 | 0.61750% |
| tcp-flood-port-80 | 4,232 | 0.61721% |
| syn-flood-port-80 | 4,222 | 0.61575% |
| command-injection | 3,226 | 0.47049% |
| sql-injection-blind | 3,206 | 0.46757% |
| dictionary-ssh | 3,103 | 0.45255% |
| rst-fin-flood-port-80 | 3,086 | 0.45007% |
| http-flood-port-80 | 3,076 | 0.44861% |
| http-flood-port-1883 | 3,074 | 0.44832% |
| dictionary-telnet | 2,913 | 0.42484% |
| udp-flood-port-1883 | 2,894 | 0.42207% |
| impersonation | 2,562 | 0.37365% |
| udp-flood-port-80 | 2,122 | 0.30948% |
| sql-injection | 1,240 | 0.18084% |
| slowloris-port-80 | 1,152 | 0.16801% |
| http-flood-port-6668 | 768 | 0.11201% |
| xss | 698 | 0.10180% |
| backdoor-upload | 670 | 0.09771% |
| tcp-flood-port-554 | 568 | 0.08284% |
| syn-flood-port-554 | 474 | 0.06913% |
| slowloris-port-8000 | 384 | 0.05600% |
| slowloris-port-554 | 384 | 0.05600% |
| slowloris-port-1883 | 384 | 0.05600% |
| mqtt-publish-flood | 384 | 0.05600% |
| connect-flood | 384 | 0.05600% |
| tcp-flood-port-443 | 380 | 0.05542% |
| syn-flood-port-443 | 380 | 0.05542% |
| syn-flood-port-22 | 196 | 0.02859% |
| http-flood-port-9595 | 192 | 0.02800% |
| http-flood-port-554 | 192 | 0.02800% |
| http-flood-port-443 | 192 | 0.02800% |
| tcp-flood-port-23 | 188 | 0.02742% |
| tcp-flood-port-22 | 188 | 0.02742% |
| syn-flood-port-23 | 188 | 0.02742% |
| syn-flood-port-557 | 94 | 0.01371% |

**Summary:**
- **Total classes**: 61
- **Most frequent class**: benign (58.43502%)
- **Least frequent class**: syn-flood-port-557 (0.01371%)
- **Imbalance ratio**: 4262.46809:1

⚠️ **Highly imbalanced dataset!**

### Distribution of column 'label4'

| Class | Count | Percent |
|-------|-------|----------|
| benign | 400,672 | 58.43502% |
| mitm_arp-spoofing | 13,387 | 1.95239% |
| malware_mirai-udp-flood | 12,869 | 1.87685% |
| recon_os-scan | 12,491 | 1.82172% |
| recon_host-disc-tcp-ack-ping | 12,432 | 1.81311% |
| recon_vuln-scan | 12,417 | 1.81093% |
| recon_host-disc-tcp-syn-ping | 12,367 | 1.80363% |
| recon_port-scan | 12,340 | 1.79970% |
| recon_host-disc-tcp-syn-stealth | 12,299 | 1.79372% |
| recon_host-disc-arp-ping | 12,291 | 1.79255% |
| recon_host-disc-udp-ping | 12,256 | 1.78745% |
| malware_mirai-syn-flood | 11,308 | 1.64919% |
| mitm_ip-spoofing | 9,541 | 1.39148% |
| recon_ping-sweep | 6,955 | 1.01433% |
| dos_udp-flood | 5,404 | 0.78813% |
| dos_icmp-flood | 5,390 | 0.78609% |
| ddos_icmp-flood | 5,018 | 0.73184% |
| ddos_udp-frag-flood | 5,016 | 0.73155% |
| dos_icmp-frag-flood | 5,014 | 0.73125% |
| ddos_icmp-frag-flood | 5,004 | 0.72980% |
| dos_udp-frag-flood | 5,002 | 0.72950% |
| dos_rst-fin-flood-port-1883 | 4,050 | 0.59066% |
| web_command-injection | 3,226 | 0.47049% |
| web_sql-injection-blind | 3,206 | 0.46757% |
| bruteforce_dictionary-ssh | 3,103 | 0.45255% |
| bruteforce_dictionary-telnet | 2,913 | 0.42484% |
| ddos_synonymousip-flood-port-1883 | 2,898 | 0.42265% |
| ddos_rst-fin-flood-port-1883 | 2,898 | 0.42265% |
| ddos_ack-frag-flood-port-1883 | 2,898 | 0.42265% |
| dos_push-ack-flood-port-1883 | 2,896 | 0.42236% |
| ddos_syn-flood-port-1883 | 2,896 | 0.42236% |
| dos_synonymousip-flood-port-1883 | 2,894 | 0.42207% |
| dos_ack-frag-flood-port-1883 | 2,894 | 0.42207% |
| ddos_udp-flood-port-1883 | 2,894 | 0.42207% |
| ddos_tcp-flood-port-1883 | 2,894 | 0.42207% |
| dos_tcp-flood-port-1883 | 2,892 | 0.42178% |
| ddos_push-ack-flood-port-1883 | 2,892 | 0.42178% |
| dos_syn-flood-port-1883 | 2,888 | 0.42119% |
| ddos_http-flood-port-1883 | 2,880 | 0.42003% |
| mitm_impersonation | 2,562 | 0.37365% |
| dos_synonymousip-flood-port-80 | 2,310 | 0.33690% |
| ddos_synonymousip-flood-port-80 | 2,126 | 0.31006% |
| ddos_tcp-flood-port-80 | 2,124 | 0.30977% |
| ddos_rst-fin-flood-port-80 | 2,124 | 0.30977% |
| dos_ack-frag-flood-port-80 | 2,122 | 0.30948% |
| ddos_udp-flood-port-80 | 2,122 | 0.30948% |
| ddos_push-ack-flood-port-80 | 2,120 | 0.30919% |
| ddos_ack-frag-flood-port-80 | 2,120 | 0.30919% |
| ddos_syn-flood-port-80 | 2,116 | 0.30860% |
| ddos_http-flood-port-80 | 2,116 | 0.30860% |
| dos_push-ack-flood-port-80 | 2,114 | 0.30831% |
| dos_tcp-flood-port-80 | 2,108 | 0.30744% |
| dos_syn-flood-port-80 | 2,106 | 0.30714% |
| web_sql-injection | 1,240 | 0.18084% |
| dos_rst-fin-flood-port-80 | 962 | 0.14030% |
| dos_http-flood-port-80 | 960 | 0.14001% |
| dos_http-flood-port-6668 | 768 | 0.11201% |
| web_xss | 698 | 0.10180% |
| web_backdoor-upload | 670 | 0.09771% |
| dos_slowloris-port-80 | 576 | 0.08401% |
| ddos_slowloris-port-80 | 576 | 0.08401% |
| dos_tcp-flood-port-554 | 568 | 0.08284% |
| dos_syn-flood-port-554 | 474 | 0.06913% |
| dos_tcp-flood-port-443 | 380 | 0.05542% |
| dos_syn-flood-port-443 | 380 | 0.05542% |
| dos_syn-flood-port-22 | 196 | 0.02859% |
| dos_http-flood-port-1883 | 194 | 0.02829% |
| dos_slowloris-port-8000 | 192 | 0.02800% |
| dos_slowloris-port-554 | 192 | 0.02800% |
| dos_slowloris-port-1883 | 192 | 0.02800% |
| dos_mqtt-publish-flood | 192 | 0.02800% |
| dos_http-flood-port-9595 | 192 | 0.02800% |
| dos_http-flood-port-554 | 192 | 0.02800% |
| dos_http-flood-port-443 | 192 | 0.02800% |
| dos_connect-flood | 192 | 0.02800% |
| ddos_slowloris-port-8000 | 192 | 0.02800% |
| ddos_slowloris-port-554 | 192 | 0.02800% |
| ddos_slowloris-port-1883 | 192 | 0.02800% |
| ddos_mqtt-publish-flood | 192 | 0.02800% |
| ddos_connect-flood | 192 | 0.02800% |
| dos_tcp-flood-port-23 | 188 | 0.02742% |
| dos_tcp-flood-port-22 | 188 | 0.02742% |
| dos_syn-flood-port-23 | 188 | 0.02742% |
| dos_syn-flood-port-557 | 94 | 0.01371% |

**Summary:**
- **Total classes**: 84
- **Most frequent class**: benign (58.43502%)
- **Least frequent class**: dos_syn-flood-port-557 (0.01371%)
- **Imbalance ratio**: 4262.46809:1

⚠️ **Highly imbalanced dataset!**

---

## 5. Feature Analysis and Correlations

⚠️ **Correlation analysis requires loading numeric data into memory**

**Note**: Since all features are stored as strings in SQLite, correlation analysis requires type conversion to numeric format first. This would require loading data into memory.

### Cardinality Analysis - Categorical Features

**Cardinality Categories:**
- **High** (>50% unique): 0 features
- **Medium** (10-50% unique): 6 features
- **Low** (<10% unique): 17 features

---

### Key Findings

1. **Data Quality**: Excellent - 100.00000% completeness, 0 missing values, 0 duplicates
2. **Data Types**: 3 unique data types - 23 categorical, 71 numeric
3. **Class Distribution**: 937 classes found in 'label_full'
4. **High Cardinality**: 0 features with >90% unique values

### Suggested Next Steps

1. **Data Type Conversion**: Convert numeric features from string to appropriate numeric types
2. **Feature Engineering**: Remove constant features, consider dimensionality reduction for high-cardinality features
3. **Data Loading**: Investigate if additional data needs to be loaded
4. **Temporal Analysis**: Analyze patterns over time using timestamp features
5. **Preprocessing**: Prepare data for modeling with appropriate encoding strategies

---

## Appendix: Dataset Information

- **Dataset**: CIC_IIoT_dataset_2025
- **Sample Size**: 685,671 records
- **Total Features**: 94
- **Database Size**: 17416.53125 MB
- **Analysis Date**: 2026-02-11 01:55:32
- **Database**: SQLite (`../data/sqlite/data.db`)

---

*Report generated from dataset_analysis.ipynb notebook*
