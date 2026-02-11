# Dataset Analysis Report
## Exploratory Dataset Analysis

This report presents a complete exploratory analysis of the CIC_IoT_DIAD_2024 dataset.

**Analysis Date**: 2026-02-10 08:23:36
**Dataset**: CIC_IoT_DIAD_2024
**Sample Size**: 55,619,998 records

---

## 1. Initial Dataset Characterization

### Dataset Dimensions
- **Rows**: 55,619,998
- **Columns**: 84

### Database Storage Size
- **Total database size**: 53576.82 MB
- **Average size per row**: ~1010.06 bytes

### Data Types
- **string**: 84 columns

### Column Names
Total: 84 features

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
84. Label

---

## 2. Data Quality Analysis

### General Summary
- **Columns with missing values**: 1
- **Total missing values**: 172,710
- **Average completeness percentage**: 100.00%

### Duplicate Analysis

- **Duplicate records**: 27,843,090
- **Duplicate percentage**: 50.06%
- **Unique records**: 27,776,908

⚠️ **Warning**: 50.06% of records are duplicates

---

## 3. Descriptive Statistics

### Feature Classification
- **Numeric**: 0
- **Categorical**: 84

### Descriptive Statistics - Numeric-Like Features (Mean, Std, Min, Max)

| Column | Count | Mean | Std | Min | Max |
|--------|-------|------|-----|-----|-----|
| Flow ID | 55,619,998 | 191.2291 | 12.0442 | 0.0 | 223.109 |
| Src IP | 55,619,998 | 191.2291 | 12.0442 | 0.0 | 223.109 |
| Src Port | 55,619,998 | 31910.455 | 20263.114 | 0.0 | 65535.0 |
| Dst IP | 55,619,998 | 187.8363 | 26.0558 | 0.0 | 255.255 |
| Dst Port | 55,619,998 | 13031.0522 | 18001.1103 | 0.0 | 65535.0 |
| Protocol | 55,619,998 | 8.4554 | 4.6008 | 0.0 | 17.0 |
| Timestamp | 55,619,998 | 7.2559 | 6.5943 | 2.0 | 29.0 |
| Flow Duration | 55,619,998 | 61731415.491 | 48007036.3948 | -123420.0 | 120000000.0 |
| Total Fwd Packet | 55,619,998 | 46.7984 | 3171.354 | 1.0 | 1499573.0 |
| Total Bwd packets | 55,619,998 | 4.1767 | 1094.5849 | 0.0 | 1209556.0 |
| Total Length of Fwd Packet | 55,619,998 | 869.3578 | 37444.5237 | 0.0 | 57073142.0 |
| Total Length of Bwd Packet | 55,619,998 | 194.4957 | 50904.4448 | 0.0 | 116437870.0 |
| Fwd Packet Length Max | 55,619,998 | 141.7459 | 441.1321 | 0.0 | 52128.0 |
| Fwd Packet Length Min | 55,619,998 | 114.497 | 358.16 | 0.0 | 5544.0 |
| Fwd Packet Length Mean | 55,619,998 | 122.6381 | 365.1262 | 0.0 | 5544.0 |
| Fwd Packet Length Std | 55,619,998 | 9.9562 | 83.9286 | 0.0 | 7229.9365 |
| Bwd Packet Length Max | 55,619,998 | 48.7345 | 276.0483 | 0.0 | 34752.0 |
| Bwd Packet Length Min | 55,619,998 | 33.6634 | 209.6387 | 0.0 | 4344.0 |
| Bwd Packet Length Mean | 55,619,998 | 37.308 | 215.3298 | 0.0 | 4516.5333 |
| Bwd Packet Length Std | 55,619,998 | 5.6928 | 64.2322 | 0.0 | 4231.443 |

*Showing top 20 of 84 numeric-like features*

### Descriptive Statistics - Categorical Features

| Column | Count | Unique_Values | Mode | Mode_Frequency | Mode_Percent |
|--------|-------|---------------|------|----------------|-------------|
| Flow ID | 55619998 | 7902693 | 8.6.0.1-8.0.6.4-0-0-0 | 7,094 | 0.01% |
| Src IP | 55619998 | 7129 | 192.168.137.182 | 18,596,068 | 33.43% |
| Src Port | 55619998 | 65536 | 4070 | 2,501,614 | 4.50% |
| Dst IP | 55619998 | 12142 | 192.168.137.182 | 3,763,472 | 6.77% |
| Dst Port | 55619998 | 65536 | 6668 | 12,414,798 | 22.32% |
| Protocol | 55619998 | 3 | 6 | 43,046,802 | 77.39% |
| Timestamp | 55619998 | 374033 | 10/08/2022 10:16:07 AM | 42,022 | 0.08% |
| Flow Duration | 55619998 | 11429977 | 0 | 179,466 | 0.32% |
| Total Fwd Packet | 55619998 | 9133 | 1 | 10,867,218 | 19.54% |
| Total Bwd packets | 55619998 | 2729 | 0 | 33,331,058 | 59.93% |
| Total Length of Fwd Packet | 55619998 | 50570 | 0.0 | 39,817,454 | 71.59% |
| Total Length of Bwd Packet | 55619998 | 22861 | 0.0 | 50,416,628 | 90.64% |
| Fwd Packet Length Max | 55619998 | 4108 | 0.0 | 39,817,454 | 71.59% |
| Fwd Packet Length Min | 55619998 | 1418 | 0.0 | 41,716,888 | 75.00% |
| Fwd Packet Length Mean | 55619998 | 125464 | 0.0 | 39,817,454 | 71.59% |
| Fwd Packet Length Std | 55619998 | 203937 | 0.0 | 53,402,062 | 96.01% |
| Bwd Packet Length Max | 55619998 | 3244 | 0.0 | 50,405,188 | 90.62% |
| Bwd Packet Length Min | 55619998 | 1134 | 0.0 | 51,582,424 | 92.74% |
| Bwd Packet Length Mean | 55619998 | 62393 | 0.0 | 50,405,188 | 90.62% |
| Bwd Packet Length Std | 55619998 | 94523 | 0.0 | 54,256,256 | 97.55% |

*Showing top 20 of 84 categorical features*

---

## 4. Class Distribution Analysis

### Distribution of column 'Label'

| Class | Count | Percent |
|-------|-------|----------|
| NeedManualLabel | 55,619,998 | 100.00% |

**Summary:**
- **Total classes**: 1
- **Most frequent class**: NeedManualLabel (100.00%)
- **Least frequent class**: NeedManualLabel (100.00%)
- **Imbalance ratio**: 1.00:1

✓ **Relatively balanced dataset**

---

## 5. Feature Analysis and Correlations

⚠️ **Less than 2 numeric features found for correlation analysis**

### Cardinality Analysis - Categorical Features

**Cardinality Categories:**
- **High** (>50% unique): 0 features
- **Medium** (10-50% unique): 17 features
- **Low** (<10% unique): 67 features

---

### Key Findings

1. **Data Quality**: Needs attention - 100.00% completeness, 172,710 missing values, 27,843,090 duplicates
2. **Data Types**: 1 unique data types - 84 categorical, 0 numeric
3. **Class Distribution**: 1 classes found in 'Label'
4. **High Cardinality**: 0 features with >90% unique values

### Suggested Next Steps

1. **Data Type Conversion**: Convert numeric features from string to appropriate numeric types
2. **Feature Engineering**: Remove constant features, consider dimensionality reduction for high-cardinality features
3. **Data Loading**: Investigate if additional data needs to be loaded
4. **Temporal Analysis**: Analyze patterns over time using timestamp features
5. **Preprocessing**: Prepare data for modeling with appropriate encoding strategies

---

## Appendix: Dataset Information

- **Dataset**: CIC_IoT_DIAD_2024
- **Sample Size**: 55,619,998 records
- **Total Features**: 84
- **Database Size**: 53576.82 MB
- **Analysis Date**: 2026-02-10 08:24:21
- **Database**: SQLite (`../data/sqlite/data.db`)

---

*Report generated from dataset_analysis.ipynb notebook*
