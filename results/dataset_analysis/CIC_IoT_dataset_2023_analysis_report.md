# Dataset Analysis Report
## Exploratory Dataset Analysis

This report presents a complete exploratory analysis of the CIC_IoT_dataset_2023 dataset.

**Analysis Date**: 2026-02-17 23:35:07
**Dataset**: CIC_IoT_dataset_2023
**Sample Size**: 45,019,243 records

---

## 1. Initial Dataset Characterization

### Dataset Dimensions
- **Rows**: 45,019,243
- **Columns**: 40

### Database Storage Size
- **Total database size**: 36565.76 MB
- **Average size per row**: ~851.68 bytes

### Data Types
- **float**: 30 columns
- **int**: 9 columns
- **string**: 1 columns

### Column Names
Total: 40 features

1. Header_Length
2. Protocol Type
3. Time_To_Live
4. Rate
5. fin_flag_number
6. syn_flag_number
7. rst_flag_number
8. psh_flag_number
9. ack_flag_number
10. ece_flag_number
11. cwr_flag_number
12. ack_count
13. syn_count
14. fin_count
15. rst_count
16. HTTP
17. HTTPS
18. DNS
19. Telnet
20. SMTP
21. SSH
22. IRC
23. TCP
24. UDP
25. DHCP
26. ARP
27. ICMP
28. IGMP
29. IPv
30. LLC
31. Tot sum
32. Min
33. Max
34. AVG
35. Std
36. Tot size
37. IAT
38. Number
39. Variance
40. Label

---

## 2. Data Quality Analysis

### General Summary
- **Columns with missing values**: 36
- **Total missing values**: 1,498
- **Average completeness percentage**: 100.00%

### Missing values visualization

![Missing values per column and completeness distribution](../images/CIC_IoT_dataset_2023_missing_values.png)

### Duplicate Analysis

- **Duplicate records**: 24,013,983
- **Duplicate percentage**: 53.34%
- **Unique records**: 21,005,260

⚠️ **Warning**: 53.34% of records are duplicates

---

## 3. Descriptive Statistics

### Feature Classification
- **Numeric**: 39
- **Categorical**: 1

### Descriptive Statistics - Numeric-Like Features (Mean, Std, Min, Max)

| Column | Count | Mean | Std | Min | Max |
|--------|-------|------|-----|-----|-----|
| psh_flag_number | 45,019,241 | 0.0939 | 0.277 | 0.0 | 1.0 |
| Tot size | 45,019,236 | 131.4284 | 229.087 | 46.0 | 13583.0 |
| ARP | 45,019,237 | 0.0028 | 0.0187 | 0.0 | 1.0 |
| IGMP | 45,019,237 | 0.0 | 0.0013 | 0.0 | 1.0 |
| UDP | 45,019,239 | 0.2173 | 0.401 | 0.0 | 1.0 |
| DNS | 45,019,240 | 0.0026 | 0.0222 | 0.0 | 1.0 |
| Min | 45,019,236 | 79.9589 | 107.1724 | 42.0 | 13583.0 |
| Max | 45,019,236 | 223.3475 | 582.5857 | 46.0 | 52194.0 |
| cwr_flag_number | 45,019,241 | 0.0 | 0.0014 | 0.0 | 1.0 |
| TCP | 45,019,239 | 0.5747 | 0.4848 | 0.0 | 1.0 |
| IRC | 45,019,240 | 0.0 | 0.001 | 0.0 | 0.9 |
| fin_flag_number | 45,019,242 | 0.0869 | 0.2793 | 0.0 | 1.0 |
| Rate | 45,019,243 | inf |  | 0.0 | inf |
| SMTP | 45,019,240 | 0.0 | 0.0008 | 0.0 | 0.9 |
| IAT | 45,019,236 | 0.0103 | 21.1764 | -0.0178 | 78612.0039 |
| HTTP | 45,019,241 | 0.0502 | 0.2134 | 0.0 | 1.0 |
| ack_flag_number | 45,019,241 | 0.1298 | 0.3166 | 0.0 | 1.0 |
| Number | 45,019,235 | 95.5112 | 19.5556 | 1.0 | 100.0 |
| rst_count | 45,019,241 | 9.1711 | 28.2268 | 0.0 | 100.0 |
| Header_Length | 45,019,243 | 13.7371 | 8.7248 | 0.0 | 60.0 |
| DHCP | 45,019,239 | 0.0002 | 0.0048 | 0.0 | 1.0 |
| IPv | 45,019,236 | 0.9972 | 0.0187 | 0.0 | 1.0 |
| Std | 45,018,566 | 41.3115 | 180.3872 | 0.0 | 11655.4047 |
| Time_To_Live | 45,019,243 | 66.5317 | 14.4168 | 0.0 | 255.0 |
| syn_count | 45,019,241 | 20.3999 | 39.9078 | 0.0 | 100.0 |
| Tot sum | 45,019,236 | 10953.115 | 16852.2521 | 60.0 | 316492.0 |
| ece_flag_number | 45,019,241 | 0.0 | 0.002 | 0.0 | 1.0 |
| ack_count | 45,019,241 | 9.8562 | 28.0205 | 0.0 | 100.0 |
| Telnet | 45,019,240 | 0.0 | 0.0007 | 0.0 | 0.6 |
| Variance | 45,018,564 | 34246.2009 | 388353.609 | 0.0 | 135848458.0 |
| ICMP | 45,019,237 | 0.1635 | 0.3663 | 0.0 | 1.0 |
| LLC | 45,019,236 | 0.9972 | 0.0187 | 0.0 | 1.0 |
| syn_flag_number | 45,019,242 | 0.2064 | 0.3995 | 0.0 | 1.0 |
| Protocol Type | 45,019,243 | 9.0913 | 9.0944 | 0.0 | 47.0 |
| fin_count | 45,019,241 | 8.6083 | 27.927 | 0.0 | 100.0 |
| rst_flag_number | 45,019,241 | 0.0929 | 0.2833 | 0.0 | 1.0 |
| SSH | 45,019,240 | 0.0002 | 0.0076 | 0.0 | 1.0 |
| AVG | 45,019,236 | 131.4284 | 229.087 | 46.0 | 13583.0 |
| HTTPS | 45,019,241 | 0.0588 | 0.2195 | 0.0 | 1.0 |

### Descriptive Statistics - Categorical Features

| Column | Count | Unique_Values | Mode | Mode_% |
|--------|-------|---------------|------|-------|
| Label | 45019234 | 34 | DDOS-ICMP_FLOOD | 15.31% |

### Numeric features - Distributions and boxplots

![Numeric features distributions](../images/CIC_IoT_dataset_2023_numeric_distributions.png)

![Boxplots - outlier detection](../images/CIC_IoT_dataset_2023_boxplots.png)

---

## 4. Class Distribution Analysis

### Number of classification columns (label column):

- **Label**

#### Distribution of column 'Label'

| Class | Count | Percent |
|-------|-------|----------|
| DDOS-ICMP_FLOOD | 6,893,259 | 15.31% |
| DDOS-UDP_FLOOD | 5,181,027 | 11.51% |
| DDOS-TCP_FLOOD | 4,306,086 | 9.56% |
| DDOS-PSHACK_FLOOD | 3,920,372 | 8.71% |
| DDOS-SYN_FLOOD | 3,886,130 | 8.63% |
| DDOS-RSTFINFLOOD | 3,872,808 | 8.60% |
| DDOS-SYNONYMOUSIP_FLOOD | 3,445,659 | 7.65% |
| DOS-UDP_FLOOD | 3,177,323 | 7.06% |
| DOS-TCP_FLOOD | 2,558,256 | 5.68% |
| DOS-SYN_FLOOD | 1,942,176 | 4.31% |
| BENIGN | 1,051,373 | 2.34% |
| MIRAI-GREETH_FLOOD | 949,381 | 2.11% |
| MIRAI-UDPPLAIN | 852,695 | 1.89% |
| MIRAI-GREIP_FLOOD | 719,655 | 1.60% |
| DDOS-ICMP_FRAGMENTATION | 433,157 | 0.96% |
| VULNERABILITYSCAN | 357,583 | 0.79% |
| MITM-ARPSPOOFING | 294,469 | 0.65% |
| DDOS-UDP_FRAGMENTATION | 274,909 | 0.61% |
| DDOS-ACK_FRAGMENTATION | 272,793 | 0.61% |
| DNS_SPOOFING | 171,468 | 0.38% |
| RECON-HOSTDISCOVERY | 128,677 | 0.29% |
| RECON-OSSCAN | 93,970 | 0.21% |
| RECON-PORTSCAN | 78,730 | 0.17% |
| DOS-HTTP_FLOOD | 68,799 | 0.15% |
| DDOS-HTTP_FLOOD | 27,597 | 0.06% |
| DDOS-SLOWLORIS | 22,400 | 0.05% |
| DICTIONARYBRUTEFORCE | 12,522 | 0.03% |
| BROWSERHIJACKING | 5,630 | 0.01% |
| COMMANDINJECTION | 5,168 | 0.01% |
| SQLINJECTION | 5,022 | 0.01% |
| XSS | 3,705 | 0.01% |
| BACKDOOR_MALWARE | 3,078 | 0.01% |
| RECON-PINGSWEEP | 2,161 | 0.00% |
| UPLOADING_ATTACK | 1,196 | 0.00% |
| None | 9 | 0.00% |

**Summary:**
- **Total classes**: 35
- **Most frequent class**: DDOS-ICMP_FLOOD (15.31%)
- **Least frequent class**: None (0.00%)
- **Imbalance ratio**: 765917.67:1

⚠️ **Highly imbalanced dataset!**

### Class distribution - Bar and pie charts

![Class distribution - bar](../images/CIC_IoT_dataset_2023_class_distribution_bar.png)

![Class distribution - pie](../images/CIC_IoT_dataset_2023_class_distribution_pie.png)

---

## 5. Feature Analysis and Correlations

### Correlation matrix

![Correlation heatmap](../images/CIC_IoT_dataset_2023_correlation_heatmap.png)

![Strong correlations](../images/CIC_IoT_dataset_2023_strong_correlations.png)

### Cardinality Analysis - Categorical Features

**Cardinality Categories:**
- **High** (>50% unique): 0 features
- **Medium** (10-50% unique): 0 features
- **Low** (<10% unique): 1 features

---

### Key Findings

1. **Data Quality**: Needs attention - 100.00% completeness, 1,498 missing values, 24,013,983 duplicates
2. **Data Types**: 3 unique data types - 1 categorical, 39 numeric
3. **Class Distribution**: 34 classes found in 'Label'
4. **High Cardinality**: 0 features with >90% unique values
## Appendix: Dataset Information

- **Dataset**: CIC_IoT_dataset_2023
- **Sample Size**: 45,019,243 records
- **Total Features**: 40
- **Database Size**: 36565.76 MB
- **Analysis Date**: 2026-02-17 23:35:33
- **Database**: SQLite---

*Report generated from dataset_analysis.ipynb notebook*
