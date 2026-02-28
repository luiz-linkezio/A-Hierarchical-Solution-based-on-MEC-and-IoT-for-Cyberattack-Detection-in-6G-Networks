# Dataset Analysis Report
## Exploratory Dataset Analysis

This report presents a complete exploratory analysis of the CIC_BCCC_NRC_IoMT_2024 dataset.

**Analysis Date**: 2026-02-18 21:11:56
**Dataset**: CIC_BCCC_NRC_IoMT_2024
**Sample Size**: 3,385,313 records

---

## 1. Initial Dataset Characterization

### Dataset Dimensions
- **Rows**: 3,385,313
- **Columns**: 85

### Data Types
- **string**: 5 columns
- **int**: 35 columns
- **float**: 45 columns

### Column Names
Total: 85 features

1. Flow ID
2. Src IP
3. Src Port
4. Dst IP
5. Dst Port
6. Protocol
7. Timestamp
8. Flow Duration
9. Total Fwd Packet
10. Total Bwd packets
11. Total Length of Fwd Packet
12. Total Length of Bwd Packet
13. Fwd Packet Length Max
14. Fwd Packet Length Min
15. Fwd Packet Length Mean
16. Fwd Packet Length Std
17. Bwd Packet Length Max
18. Bwd Packet Length Min
19. Bwd Packet Length Mean
20. Bwd Packet Length Std
21. Flow Bytes/s
22. Flow Packets/s
23. Flow IAT Mean
24. Flow IAT Std
25. Flow IAT Max
26. Flow IAT Min
27. Fwd IAT Total
28. Fwd IAT Mean
29. Fwd IAT Std
30. Fwd IAT Max
31. Fwd IAT Min
32. Bwd IAT Total
33. Bwd IAT Mean
34. Bwd IAT Std
35. Bwd IAT Max
36. Bwd IAT Min
37. Fwd PSH Flags
38. Bwd PSH Flags
39. Fwd URG Flags
40. Bwd URG Flags
41. Fwd Header Length
42. Bwd Header Length
43. Fwd Packets/s
44. Bwd Packets/s
45. Packet Length Min
46. Packet Length Max
47. Packet Length Mean
48. Packet Length Std
49. Packet Length Variance
50. FIN Flag Count
51. SYN Flag Count
52. RST Flag Count
53. PSH Flag Count
54. ACK Flag Count
55. URG Flag Count
56. CWR Flag Count
57. ECE Flag Count
58. Down/Up Ratio
59. Average Packet Size
60. Fwd Segment Size Avg
61. Bwd Segment Size Avg
62. Fwd Bytes/Bulk Avg
63. Fwd Packet/Bulk Avg
64. Fwd Bulk Rate Avg
65. Bwd Bytes/Bulk Avg
66. Bwd Packet/Bulk Avg
67. Bwd Bulk Rate Avg
68. Subflow Fwd Packets
69. Subflow Fwd Bytes
70. Subflow Bwd Packets
71. Subflow Bwd Bytes
72. FWD Init Win Bytes
73. Bwd Init Win Bytes
74. Fwd Act Data Pkts
75. Fwd Seg Size Min
76. Active Mean
77. Active Std
78. Active Max
79. Active Min
80. Idle Mean
81. Idle Std
82. Idle Max
83. Idle Min
84. Attack Name
85. Label

---

## 2. Data Quality Analysis

### General Summary
- **Columns with missing values**: 0
- **Total missing values**: 0
- **Average completeness percentage**: 100.00%

### Missing values visualization

![Missing values per column and completeness distribution](../images/CIC_BCCC_NRC_IoMT_2024_missing_values.png)

### Duplicate Analysis

- **Duplicate records**: 109,180
- **Duplicate percentage**: 3.23%
- **Unique records**: 3,276,133

⚠️ **Warning**: 3.23% of records are duplicates

---

## 3. Descriptive Statistics

### Feature Classification
- **Numeric**: 80
- **Categorical**: 5

### Descriptive Statistics - Numeric-Like Features (Mean, Std, Min, Max)

| Column | Count | Mean | Std | Min | Max |
|--------|-------|------|-----|-----|-----|
| Fwd Segment Size Avg | 3,385,313 | 11.5683 | 111.3202 | 0.0 | 1460.0 |
| Src Port | 3,385,313 | 28157.0721 | 20872.5129 | 0.0 | 65535.0 |
| Label | 3,385,313 | 0.9904 | 0.0977 | 0.0 | 1.0 |
| Flow IAT Max | 3,385,313 | 8352615.5203 | 13412983.09 | 0.0 | 119979299.0 |
| Fwd Seg Size Min | 3,385,313 | 20.8881 | 3.1823 | 20.0 | 52.0 |
| Bwd IAT Min | 3,385,313 | 46073.6848 | 1465571.6771 | -12820973.0 | 65881399.0 |
| Bwd Packet Length Std | 3,385,313 | 6.0465 | 53.6155 | 0.0 | 1023.8906 |
| Fwd Packet Length Std | 3,385,313 | 5.0448 | 45.9182 | 0.0 | 1023.8906 |
| SYN Flag Count | 3,385,313 | 0.3253 | 0.6701 | 0.0 | 23.0 |
| Bwd Packet Length Min | 3,385,313 | 3.71 | 58.5133 | 0.0 | 1448.0 |
| Packet Length Std | 3,385,313 | 12.9838 | 81.0745 | 0.0 | 842.9314 |
| PSH Flag Count | 3,385,313 | 1.7283 | 66.8793 | 0.0 | 7479.0 |
| Bwd IAT Mean | 3,385,313 | 177436.3801 | 2084250.4327 | 0.0 | 65881399.0 |
| Fwd Packets/s | 3,385,313 | 955.1363 | 32481.0709 | 0.0 | 3000000.0 |
| Dst Port | 3,385,313 | 20786.3065 | 21911.9317 | 1.0 | 65487.0 |
| Flow IAT Mean | 3,385,313 | 3899848.9143 | 4668025.5555 | 0.0 | 119604586.0 |
| Packet Length Mean | 3,385,313 | 18.8164 | 131.4417 | 0.0 | 1460.0 |
| Fwd IAT Mean | 3,385,313 | 3899064.9261 | 4713661.7887 | 0.0 | 119604586.0 |
| Fwd Bytes/Bulk Avg | 3,385,313 | 0.0 | 0.0 | 0.0 | 0.0 |
| Fwd Packet Length Mean | 3,385,313 | 11.5683 | 111.3202 | 0.0 | 1460.0 |
| Fwd Packet/Bulk Avg | 3,385,313 | 0.0 | 0.0 | 0.0 | 0.0 |
| Packet Length Variance | 3,385,313 | 6741.6547 | 48568.3916 | 0.0 | 710533.3333 |
| Bwd Header Length | 3,385,313 | 64.6522 | 2139.4196 | 0.0 | 316488.0 |
| Bwd IAT Total | 3,385,313 | 1178941.7293 | 10736990.1703 | 0.0 | 119999985.0 |
| Idle Std | 3,385,313 | 1646199.4331 | 5157396.9589 | 0.0 | 74964635.3427 |
| Protocol | 3,385,313 | 6.0 | 0.0 | 6.0 | 6.0 |
| Total Length of Bwd Packet | 3,385,313 | 442.953 | 35430.5511 | 0.0 | 13895734.0 |
| Flow Bytes/s | 3,385,313 | 37680.7352 | 5841996.6697 | 0.0 | 2896000000.0 |
| Bwd Packet/Bulk Avg | 3,385,313 | 1.1845 | 60.509 | 0.0 | 31871.0 |
| Active Std | 3,385,313 | 1562606.1913 | 5861979.7113 | 0.0 | 58057147.9333 |
| RST Flag Count | 3,385,313 | 0.4497 | 0.6637 | 0.0 | 2.0 |
| Bwd Bulk Rate Avg | 3,385,313 | 71355.2799 | 10933677.0943 | 0.0 | 5792000000.0 |
| Fwd Packet Length Max | 3,385,313 | 17.5594 | 149.5838 | 0.0 | 1460.0 |
| Total Fwd Packet | 3,385,313 | 16.0732 | 82.2072 | 1.0 | 31872.0 |
| Fwd IAT Min | 3,385,313 | 2474515.1962 | 3112836.731 | -12820919.0 | 119604586.0 |
| Down/Up Ratio | 3,385,313 | 0.3159 | 1.5706 | 0.0 | 1555.0 |
| Bwd Packet Length Max | 3,385,313 | 19.1614 | 158.9603 | 0.0 | 1460.0 |
| Active Min | 3,385,313 | 4028302.0655 | 13614621.535 | 0.0 | 113319356.0 |
| CWR Flag Count | 3,385,313 | 0.0001 | 0.0142 | 0.0 | 12.0 |
| Fwd Bulk Rate Avg | 3,385,313 | 0.0 | 0.0 | 0.0 | 0.0 |
| Bwd Packets/s | 3,385,313 | 14.6509 | 1892.5631 | 0.0 | 2000000.0 |
| Bwd Init Win Bytes | 3,385,313 | 1051.4701 | 7286.8736 | 0.0 | 65535.0 |
| Packet Length Max | 3,385,313 | 35.7522 | 215.2854 | 0.0 | 1460.0 |
| Fwd IAT Std | 3,385,313 | 1869924.3833 | 4307266.2177 | 0.0 | 84848319.3717 |
| Bwd Segment Size Avg | 3,385,313 | 11.8839 | 109.2821 | 0.0 | 1448.0 |
| Bwd IAT Max | 3,385,313 | 334329.9169 | 3602332.662 | 0.0 | 118962181.0 |
| Bwd IAT Std | 3,385,313 | 158650.1378 | 1872106.9223 | 0.0 | 84118854.5812 |
| Total Bwd packets | 3,385,313 | 2.0521 | 66.8513 | 0.0 | 9890.0 |
| Fwd PSH Flags | 3,385,313 | 0.0138 | 0.1166 | 0.0 | 1.0 |
| Bwd PSH Flags | 3,385,313 | 0.0 | 0.0 | 0.0 | 0.0 |
| ACK Flag Count | 3,385,313 | 4.0955 | 145.0533 | 0.0 | 31872.0 |
| Subflow Fwd Bytes | 3,385,313 | 140.9758 | 15936.9195 | 0.0 | 9493790.0 |
| FWD Init Win Bytes | 3,385,313 | 4602.5178 | 15836.5983 | 0.0 | 65535.0 |
| Fwd Packet Length Min | 3,385,313 | 4.265 | 63.0357 | 0.0 | 1460.0 |
| Flow IAT Std | 3,385,313 | 1831300.9785 | 4084316.1188 | 0.0 | 83514417.5833 |
| Active Max | 3,385,313 | 6839138.5692 | 17293063.55 | 0.0 | 113319356.0 |
| Fwd IAT Max | 3,385,313 | 8267568.5906 | 13399237.1122 | 0.0 | 119995142.0 |
| Fwd Header Length | 3,385,313 | 347.5606 | 2610.0816 | 20.0 | 1019904.0 |
| Bwd Packet Length Mean | 3,385,313 | 11.8839 | 109.2821 | 0.0 | 1448.0 |
| Flow IAT Min | 3,385,313 | 2539597.3306 | 3234222.206 | -12821038.0 | 119604586.0 |
| Idle Mean | 3,385,313 | 5154799.9264 | 9462275.0595 | 0.0 | 119979299.0 |
| Bwd URG Flags | 3,385,313 | 0.0 | 0.0 | 0.0 | 0.0 |
| Average Packet Size | 3,385,313 | 20.5091 | 143.3418 | 0.0 | 2172.0 |
| Bwd Bytes/Bulk Avg | 3,385,313 | 732.5135 | 40609.4821 | 0.0 | 46140140.0 |
| Flow Duration | 3,385,313 | 59818056.8121 | 54489580.7581 | 0.0 | 120000000.0 |
| ECE Flag Count | 3,385,313 | 0.0001 | 0.0134 | 0.0 | 3.0 |
| Idle Min | 3,385,313 | 3692315.4324 | 7773545.4681 | 0.0 | 119979299.0 |
| Subflow Fwd Packets | 3,385,313 | 1.1655 | 41.5616 | 0.0 | 7611.0 |
| Fwd Act Data Pkts | 3,385,313 | 1.5437 | 77.1723 | 0.0 | 31870.0 |
| Active Mean | 3,385,313 | 5226416.5259 | 14508856.3372 | 0.0 | 113319356.0 |
| Subflow Bwd Packets | 3,385,313 | 0.4257 | 35.1082 | 0.0 | 6138.0 |
| Packet Length Min | 3,385,313 | 0.7814 | 25.3638 | 0.0 | 1460.0 |
| Flow Packets/s | 3,385,313 | 1012.357 | 32633.2034 | 0.0167 | 3000000.0 |
| Fwd IAT Total | 3,385,313 | 59658998.5685 | 54571068.1473 | 0.0 | 120000000.0 |
| Fwd URG Flags | 3,385,313 | 0.0 | 0.0038 | 0.0 | 1.0 |
| URG Flag Count | 3,385,313 | 0.0001 | 0.0105 | 0.0 | 2.0 |
| Total Length of Fwd Packet | 3,385,313 | 709.745 | 61134.9815 | 0.0 | 46140140.0 |
| Idle Max | 3,385,313 | 7066657.0561 | 13961286.9322 | 0.0 | 119979299.0 |
| FIN Flag Count | 3,385,313 | 0.0477 | 0.2317 | 0.0 | 3.0 |
| Subflow Bwd Bytes | 3,385,313 | 36.0786 | 5911.4795 | 0.0 | 6902088.0 |

### Descriptive Statistics - Categorical Features

| Column | Count | Unique_Values | Mode | Mode_% |
|--------|-------|---------------|------|-------|
| Flow ID | 3385313 | 1055241 | 10.0.0.7-10.0.0.254-45727-1883-6 | 0.02% |
| Src IP | 3385313 | 406 | 192.168.137.48 | 68.59% |
| Dst IP | 3385313 | 354 | 192.168.137.250 | 21.30% |
| Timestamp | 3385313 | 25527 | 30/08/2023 02:33:04 PM | 0.74% |
| Attack Name | 3385313 | 15 | DoS TCP Flood | 62.24% |

### Numeric features - Distributions and boxplots

![Numeric features distributions](../images/CIC_BCCC_NRC_IoMT_2024_numeric_distributions.png)

![Boxplots - outlier detection](../images/CIC_BCCC_NRC_IoMT_2024_boxplots.png)

---

## 4. Class Distribution Analysis

### Number of classification columns (label column):

- **Label**

#### Distribution of column 'Label'

| Class | Count | Percent |
|-------|-------|----------|
| 1 | 3,352,693 | 99.04% |
| 0 | 32,620 | 0.96% |

**Summary:**
- **Total classes**: 2
- **Most frequent class**: 1 (99.04%)
- **Least frequent class**: 0 (0.96%)
- **Imbalance ratio**: 102.78:1

⚠️ **Highly imbalanced dataset!**

### Class distribution - Bar and pie charts

![Class distribution - bar](../images/CIC_BCCC_NRC_IoMT_2024_class_distribution_bar.png)

![Class distribution - pie](../images/CIC_BCCC_NRC_IoMT_2024_class_distribution_pie.png)

---

## 5. Feature Analysis and Correlations

⚠️ **Correlation analysis requires loading numeric data into memory**

**Note**: Since all features are stored as strings in SQLite, correlation analysis requires type conversion to numeric format first. This would require loading data into memory.

### Cardinality Analysis - Categorical Features

**Cardinality Categories:**
- **High** (>50% unique): 0 features
- **Medium** (10-50% unique): 1 features
- **Low** (<10% unique): 4 features

---

### Key Findings

1. **Data Quality**: Needs attention - 100.00% completeness, 0 missing values, 109,180 duplicates
2. **Data Types**: 3 unique data types - 5 categorical, 80 numeric
3. **Class Distribution**: 2 classes found in 'Label'
4. **High Cardinality**: 0 features with >90% unique values
## Appendix: Dataset Information

- **Dataset**: CIC_BCCC_NRC_IoMT_2024
- **Sample Size**: 3,385,313 records
- **Total Features**: 85
- **Database Size**: 37727.15 MB
- **Analysis Date**: 2026-02-18 21:11:57
- **Database**: SQLite---

*Report generated from dataset_analysis.ipynb notebook*
