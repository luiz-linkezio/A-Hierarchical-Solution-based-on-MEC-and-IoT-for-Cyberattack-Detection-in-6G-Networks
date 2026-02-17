# Dataset Analysis Report
## Exploratory Dataset Analysis

This report presents a complete exploratory analysis of the CIC_IoT_DIAD_2024 dataset.

**Analysis Date**: 2026-02-17 19:07:52
**Dataset**: CIC_IoT_DIAD_2024
**Sample Size**: 55,619,998 records

---

## 1. Initial Dataset Characterization

### Dataset Dimensions
- **Rows**: 55,619,998
- **Columns**: 84

### Database Storage Size
- **Total database size**: 36565.76 MB
- **Average size per row**: ~689.36 bytes

### Data Types
- **string**: 5 columns
- **int**: 34 columns
- **float**: 45 columns

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

### Missing values visualization

![Missing values per column and completeness distribution](../images/CIC_IoT_DIAD_2024_missing_values.png)

### Duplicate Analysis

- **Duplicate records**: 27,843,090
- **Duplicate percentage**: 50.06%
- **Unique records**: 27,776,908

⚠️ **Warning**: 50.06% of records are duplicates

---

## 3. Descriptive Statistics

### Feature Classification
- **Numeric**: 79
- **Categorical**: 5

### Descriptive Statistics - Numeric-Like Features (Mean, Std, Min, Max)

| Column | Count | Mean | Std | Min | Max |
|--------|-------|------|-----|-----|-----|
| Fwd Seg Size Min | 55,619,998 | 19.0849 | 7.7025 | 0.0 | 60.0 |
| Flow Packets/s | 55,619,998 | inf |  | -16.2454 | inf |
| Packet Length Variance | 55,619,998 | 31257.634 | 153143.9764 | 0.0 | 21761681.5714 |
| Bwd Packet/Bulk Avg | 55,619,998 | 8.6522 | 101.4626 | 0.0 | 80559.0 |
| Flow IAT Std | 55,619,998 | 2493531.0933 | 4771304.807 | 0.0 | 84848211.1843 |
| Fwd Header Length | 55,619,998 | 242.0608 | 1801.1296 | 0.0 | 4317472.0 |
| Flow Duration | 55,619,998 | 61731415.491 | 48007036.3948 | -123420.0 | 120000000.0 |
| CWR Flag Count | 55,619,998 | 0.0004 | 0.024 | 0.0 | 20.0 |
| Down/Up Ratio | 55,619,998 | 0.6682 | 27.9493 | 0.0 | 95656.0 |
| Flow IAT Mean | 55,619,998 | 8839243.7521 | 16433568.7423 | -123420.0 | 119999999.0 |
| Src Port | 55,619,998 | 31910.455 | 20263.114 | 0.0 | 65535.0 |
| Total Fwd Packet | 55,619,998 | 46.7984 | 3171.354 | 1.0 | 1499573.0 |
| Bwd Header Length | 55,619,998 | 31.4543 | 1130.3724 | 0.0 | 2577856.0 |
| Idle Mean | 55,619,998 | 10227109.7187 | 17065057.0541 | 0.0 | 119999999.0 |
| ECE Flag Count | 55,619,998 | 0.001 | 0.0818 | 0.0 | 17.0 |
| Flow Bytes/s | 55,447,288 | inf |  | -1551.4328 | inf |
| PSH Flag Count | 55,619,998 | 0.2494 | 21.5206 | 0.0 | 68028.0 |
| Bwd PSH Flags | 55,619,998 | 0.0 | 0.0 | 0.0 | 0.0 |
| Fwd IAT Total | 55,619,998 | 58725094.6074 | 49652391.7566 | 0.0 | 120000000.0 |
| Fwd Packet Length Std | 55,619,998 | 9.9562 | 83.9286 | 0.0 | 7229.9365 |
| FIN Flag Count | 55,619,998 | 0.0405 | 0.2399 | 0.0 | 3.0 |
| URG Flag Count | 55,619,998 | 0.0 | 0.0 | 0.0 | 0.0 |
| Idle Max | 55,619,998 | 13270185.632 | 18444955.7622 | 0.0 | 119999999.0 |
| Active Min | 55,619,998 | 2357616.8821 | 5407580.7004 | 0.0 | 114839331.0 |
| Total Bwd packets | 55,619,998 | 4.1767 | 1094.5849 | 0.0 | 1209556.0 |
| Fwd IAT Max | 55,619,998 | 13130434.3142 | 19151099.7989 | 0.0 | 119999999.0 |
| Fwd URG Flags | 55,619,998 | 0.0 | 0.0 | 0.0 | 0.0 |
| Fwd Packet Length Mean | 55,619,998 | 122.6381 | 365.1262 | 0.0 | 5544.0 |
| Fwd Bytes/Bulk Avg | 55,619,998 | 0.0 | 0.0 | 0.0 | 0.0 |
| Packet Length Mean | 55,619,998 | 126.0542 | 346.9324 | 0.0 | 4199.3333 |
| Packet Length Min | 55,619,998 | 93.8412 | 323.6447 | 0.0 | 2896.0 |
| Total Length of Bwd Packet | 55,619,998 | 194.4957 | 50904.4448 | 0.0 | 116437870.0 |
| Bwd Packet Length Mean | 55,619,998 | 37.308 | 215.3298 | 0.0 | 4516.5333 |
| Fwd Act Data Pkts | 55,619,998 | 10.5237 | 96.5932 | 0.0 | 28653.0 |
| Subflow Bwd Packets | 55,619,998 | 1.3966 | 619.7247 | 0.0 | 1185560.0 |
| Fwd Segment Size Avg | 55,619,998 | 122.6381 | 365.1262 | 0.0 | 5544.0 |
| Subflow Bwd Bytes | 55,619,998 | 31.911 | 11885.3906 | 0.0 | 35545889.0 |
| Bwd IAT Min | 55,619,998 | 583645.6048 | 4709690.5109 | -517965.0 | 119969935.0 |
| Bwd Bulk Rate Avg | 55,619,998 | 11685.235 | 1603880.8869 | 0.0 | 1792000000.0 |
| Bwd IAT Mean | 55,619,998 | 1041476.9807 | 5177591.7568 | -172654.6667 | 119969935.0 |
| Fwd Packet/Bulk Avg | 55,619,998 | 0.0 | 0.0 | 0.0 | 0.0 |
| Bwd Segment Size Avg | 55,619,998 | 37.308 | 215.3298 | 0.0 | 4516.5333 |
| Bwd IAT Std | 55,619,998 | 427603.8404 | 2203035.8213 | 0.0 | 84756709.4455 |
| Subflow Fwd Packets | 55,619,998 | 11.9243 | 1746.3943 | 0.0 | 1499573.0 |
| ACK Flag Count | 55,619,998 | 1.3957 | 73.9743 | 0.0 | 180786.0 |
| Flow IAT Min | 55,619,998 | 6461760.1804 | 16549954.9489 | -517965.0 | 119999999.0 |
| Fwd IAT Std | 55,619,998 | 2016629.3078 | 4375611.6324 | 0.0 | 84848211.1843 |
| Fwd IAT Min | 55,619,998 | 7377579.3224 | 17537362.2656 | -5.0 | 119999999.0 |
| SYN Flag Count | 55,619,998 | 7.1093 | 8.4782 | 0.0 | 40.0 |
| Fwd PSH Flags | 55,619,998 | 0.0064 | 0.0796 | 0.0 | 1.0 |
| Active Mean | 55,619,998 | 3925398.9335 | 7920220.2659 | 0.0 | 114839331.0 |
| Dst Port | 55,619,998 | 13031.0522 | 18001.1103 | 0.0 | 65535.0 |
| Bwd URG Flags | 55,619,998 | 0.0 | 0.0 | 0.0 | 0.0 |
| Bwd Packet Length Max | 55,619,998 | 48.7345 | 276.0483 | 0.0 | 34752.0 |
| Bwd Packet Length Min | 55,619,998 | 33.6634 | 209.6387 | 0.0 | 4344.0 |
| Bwd Packet Length Std | 55,619,998 | 5.6928 | 64.2322 | 0.0 | 4231.443 |
| Idle Min | 55,619,998 | 8737987.4919 | 16942995.0827 | 0.0 | 119999999.0 |
| Bwd Bytes/Bulk Avg | 55,619,998 | 468.7271 | 56540.2559 | 0.0 | 116439320.0 |
| Bwd Packets/s | 55,619,998 | 52.244 | 6835.4134 | 0.0 | 3000000.0 |
| Bwd Init Win Bytes | 55,619,998 | 4992.3145 | 14884.688 | 0.0 | 65535.0 |
| Fwd Packets/s | 55,619,998 | 3587.9535 | 80058.7846 | 0.0 | 8000000.0 |
| Fwd Packet Length Max | 55,619,998 | 141.7459 | 441.1321 | 0.0 | 52128.0 |
| Protocol | 55,619,998 | 8.4554 | 4.6008 | 0.0 | 17.0 |
| Subflow Fwd Bytes | 55,619,998 | 231.796 | 8571.355 | 0.0 | 22073212.0 |
| Active Std | 55,619,998 | 1917845.1622 | 5018097.733 | 0.0 | 74600223.6204 |
| Packet Length Max | 55,619,998 | 182.0637 | 500.8267 | 0.0 | 52128.0 |
| Active Max | 55,619,998 | 5949897.1737 | 12235597.0222 | 0.0 | 114839331.0 |
| Idle Std | 55,619,998 | 1822208.0057 | 4324687.898 | 0.0 | 77751011.5343 |
| Fwd IAT Mean | 55,619,998 | 9229202.891 | 17493084.3968 | 0.0 | 119999999.0 |
| Total Length of Fwd Packet | 55,619,998 | 869.3578 | 37444.5237 | 0.0 | 57073142.0 |
| Bwd IAT Total | 55,619,998 | 4283750.6326 | 16359008.2311 | -517964.0 | 119999966.0 |
| RST Flag Count | 55,619,998 | 0.369 | 0.5119 | 0.0 | 2.0 |
| Bwd IAT Max | 55,619,998 | 1569573.0342 | 6766850.4489 | 0.0 | 119969935.0 |
| Flow IAT Max | 55,619,998 | 13412014.0982 | 18352497.3543 | -123420.0 | 119999999.0 |
| FWD Init Win Bytes | 55,619,998 | 7821.5722 | 18080.0852 | 0.0 | 65535.0 |
| Fwd Bulk Rate Avg | 55,619,998 | 0.0 | 0.0 | 0.0 | 0.0 |
| Packet Length Std | 55,619,998 | 40.8627 | 172.0113 | 0.0 | 4664.9418 |
| Fwd Packet Length Min | 55,619,998 | 114.497 | 358.16 | 0.0 | 5544.0 |
| Average Packet Size | 55,619,998 | 177.6888 | 512.9727 | 0.0 | 6299.0 |

### Descriptive Statistics - Categorical Features

| Column | Count | Unique_Values | Mode | Mode_% |
|--------|-------|---------------|------|-------|
| Flow ID | 55619998 | 7902693 | 8.6.0.1-8.0.6.4-0-0-0 | 0.01% |
| Src IP | 55619998 | 7129 | 192.168.137.182 | 33.43% |
| Dst IP | 55619998 | 12142 | 192.168.137.182 | 6.77% |
| Timestamp | 55619998 | 374033 | 10/08/2022 10:16:07 AM | 0.08% |
| Label | 55619998 | 1 | NeedManualLabel | 100.00% |

### Numeric features - Distributions and boxplots

![Numeric features distributions](../images/CIC_IoT_DIAD_2024_numeric_distributions.png)

![Boxplots - outlier detection](../images/CIC_IoT_DIAD_2024_boxplots.png)

---

## 4. Class Distribution Analysis

### Number of classification columns (label column):

- **label**
- **subLabel**
- **subLabelCat**

#### Distribution of column 'label'

| Class | Count | Percent |
|-------|-------|----------|
| NeedManualLabel | 55,619,998 | 100.00% |

**Summary:**
- **Total classes**: 1
- **Most frequent class**: NeedManualLabel (100.00%)
- **Least frequent class**: NeedManualLabel (100.00%)
- **Imbalance ratio**: 1.00:1

✓ **Relatively balanced dataset**

#### Distribution of column 'subLabel'

| Class | Count | Percent |
|-------|-------|----------|
| subLabel | 55,619,998 | 100.00% |

**Summary:**
- **Total classes**: 1
- **Most frequent class**: subLabel (100.00%)
- **Least frequent class**: subLabel (100.00%)
- **Imbalance ratio**: 1.00:1

✓ **Relatively balanced dataset**

#### Distribution of column 'subLabelCat'

| Class | Count | Percent |
|-------|-------|----------|
| subLabelCat | 55,619,998 | 100.00% |

**Summary:**
- **Total classes**: 1
- **Most frequent class**: subLabelCat (100.00%)
- **Least frequent class**: subLabelCat (100.00%)
- **Imbalance ratio**: 1.00:1

✓ **Relatively balanced dataset**

### Class distribution - Bar and pie charts

![Class distribution - bar](../images/CIC_IoT_DIAD_2024_class_distribution_bar.png)

![Class distribution - pie](../images/CIC_IoT_DIAD_2024_class_distribution_pie.png)

---

## 5. Feature Analysis and Correlations

⚠️ **Correlation analysis requires loading numeric data into memory**

**Note**: Since all features are stored as strings in SQLite, correlation analysis requires type conversion to numeric format first. This would require loading data into memory.

### Cardinality Analysis - Categorical Features

---

### Key Findings

1. **Data Quality**: Needs attention - 100.00% completeness, 172,710 missing values, 27,843,090 duplicates
2. **Data Types**: 3 unique data types - 5 categorical, 79 numeric
3. **Class Distribution**: 1 classes found in 'label'
4. **High Cardinality**: 0 features with >90% unique values
## Appendix: Dataset Information

- **Dataset**: CIC_IoT_DIAD_2024
- **Sample Size**: 55,619,998 records
- **Total Features**: 84
- **Database Size**: 36565.76 MB
- **Analysis Date**: 2026-02-17 19:09:01
- **Database**: SQLite---

*Report generated from dataset_analysis.ipynb notebook*
