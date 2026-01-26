# Dataset Analysis Report
## Exploratory Dataset Analysis

This report presents a complete exploratory analysis of the CIC_IoT_DIAD_2024 dataset.

**Analysis Date**: 2026-01-25 23:10:36
**Dataset**: CIC_IoT_DIAD_2024
**Sample Size**: 27,809,999 records

---

## 1. Initial Dataset Characterization

### Dataset Dimensions
- **Rows**: 27,809,999
- **Columns**: 84

### Database Storage Size
- **Total database size**: 34865.78 MB
- **Average size per row**: ~1314.61 bytes

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
- **Total missing values**: 86,355
- **Average completeness percentage**: 100.00%

### Duplicate Analysis

- **Duplicate records**: 33,091
- **Duplicate percentage**: 0.12%
- **Unique records**: 27,776,908

⚠️ **Warning**: 0.12% of records are duplicates

---

## 3. Descriptive Statistics

### Feature Classification
- **Numeric**: 0
- **Categorical**: 84

### Descriptive Statistics - Categorical Features

| Column | Unique_Values | Mode | Mode_Frequency | Mode_Percent |
|--------|---------------|------|----------------|-------------|
| Flow ID | 7902693 | 8.6.0.1-8.0.6.4-0-0-0 | 3,547 | 0.01% |
| Src IP | 7129 | 192.168.137.182 | 9,298,034 | 33.43% |
| Src Port | 65536 | 4070 | 1,250,807 | 4.50% |
| Dst IP | 12142 | 192.168.137.182 | 1,881,736 | 6.77% |
| Dst Port | 65536 | 6668 | 6,207,399 | 22.32% |
| Protocol | 3 | 6 | 21,523,401 | 77.39% |
| Timestamp | 374033 | 10/08/2022 10:16:07 AM | 21,011 | 0.08% |
| Flow Duration | 11429977 | 0 | 89,733 | 0.32% |
| Total Fwd Packet | 9133 | 1 | 5,433,609 | 19.54% |
| Total Bwd packets | 2729 | 0 | 16,665,529 | 59.93% |
| Total Length of Fwd Packet | 50570 | 0.0 | 19,908,727 | 71.59% |
| Total Length of Bwd Packet | 22861 | 0.0 | 25,208,314 | 90.64% |
| Fwd Packet Length Max | 4108 | 0.0 | 19,908,727 | 71.59% |
| Fwd Packet Length Min | 1418 | 0.0 | 20,858,444 | 75.00% |
| Fwd Packet Length Mean | 125464 | 0.0 | 19,908,727 | 71.59% |
| Fwd Packet Length Std | 203937 | 0.0 | 26,701,031 | 96.01% |
| Bwd Packet Length Max | 3244 | 0.0 | 25,202,594 | 90.62% |
| Bwd Packet Length Min | 1134 | 0.0 | 25,791,212 | 92.74% |
| Bwd Packet Length Mean | 62393 | 0.0 | 25,202,594 | 90.62% |
| Bwd Packet Length Std | 94523 | 0.0 | 27,128,128 | 97.55% |

*Showing top 20 of 84 categorical features*

---

## 4. Class Distribution Analysis

### Distribution of column 'Label'

| Class | Count | Percent |
|-------|-------|----------|
| NeedManualLabel | 27,809,999 | 100.00% |

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
- **High** (>50% unique): 3 features
- **Medium** (10-50% unique): 19 features
- **Low** (<10% unique): 62 features

---

### Key Findings

1. **Data Quality**: Needs attention - 100.00% completeness, 86,355 missing values, 33,091 duplicates
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
- **Sample Size**: 27,809,999 records
- **Total Features**: 84
- **Database Size**: 34865.78 MB
- **Analysis Date**: 2026-01-25 23:10:59
- **Database**: SQLite (`../data/sqlite/data.db`)

---

*Report generated from dataset_analysis.ipynb notebook*
