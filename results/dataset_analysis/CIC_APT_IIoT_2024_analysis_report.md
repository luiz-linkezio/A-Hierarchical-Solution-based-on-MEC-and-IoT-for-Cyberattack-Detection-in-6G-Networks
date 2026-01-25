# Dataset Analysis Report
## Exploratory Dataset Analysis

This report presents a complete exploratory analysis of the CIC_APT_IIoT_2024 dataset.

**Analysis Date**: 2026-01-25 20:37:10
**Dataset**: CIC_APT_IIoT_2024
**Sample Size**: 43,198,438 records

---

## 1. Initial Dataset Characterization

### Dataset Dimensions
- **Rows**: 43,198,438
- **Columns**: 70

### Database Storage Size
- **Total database size**: 34865.78 MB
- **Average size per row**: ~846.31 bytes

### Data Types
- **string**: 70 columns

### Column Names
Total: 70 features

1. ts
2. flow_duration
3. Header_Length
4. Source IP
5. Destination IP
6. Source Port
7. Destination Port
8. Protocol Type
9. Protocol_name
10. Duration
11. Rate
12. Srate
13. Drate
14. fin_flag_number
15. syn_flag_number
16. rst_flag_number
17. psh_flag_number
18. ack_flag_number
19. urg_flag_number
20. ece_flag_number
21. cwr_flag_number
22. ack_count
23. syn_count
24. fin_count
25. urg_count
26. rst_count
27. max_duration
28. min_duration
29. sum_duration
30. average_duration
31. std_duration
32. CoAP
33. HTTP
34. HTTPS
35. DNS
36. Telnet
37. SMTP
38. SSH
39. IRC
40. TCP
41. UDP
42. DHCP
43. ARP
44. ICMP
45. IGMP
46. IPv
47. LLC
48. Tot sum
49. Min
50. Max
51. AVG
52. Std
53. Tot size
54. IAT
55. Number
56. MAC
57. Magnitue
58. Radius
59. Covariance
60. Variance
61. Weight
62. DS status
63. Fragments
64. Sequence number
65. Protocol Version
66. flow_idle_time
67. flow_active_time
68. label
69. subLabel
70. subLabelCat

---

## 2. Data Quality Analysis

### General Summary
- **Columns with missing values**: 0
- **Total missing values**: 0
- **Average completeness percentage**: 100.00%

### Duplicate Analysis

- **Duplicate records**: 21,599,219
- **Duplicate percentage**: 50.00%
- **Unique records**: 21,599,219

⚠️ **Warning**: 50.00% of records are duplicates

---

## 3. Descriptive Statistics

### Feature Classification
- **Numeric**: 0
- **Categorical**: 70

### Descriptive Statistics - Categorical Features

| Column | Unique_Values | Mode | Mode_Frequency | Mode_Percent |
|--------|---------------|------|----------------|-------------|
| ts | 21355529 | 1701170814.58724 | 10 | 0.00% |
| flow_duration | 9031748 | 0.0 | 947,104 | 2.19% |
| Header_Length | 2711560 | 148 | 581,870 | 1.35% |
| Source IP | 64 | 172.16.64.128 | 24,347,546 | 56.36% |
| Destination IP | 87 | 172.16.64.128 | 14,827,732 | 34.32% |
| Source Port | 28068 | 1883 | 9,716,246 | 22.49% |
| Destination Port | 14810 | 502 | 14,510,184 | 33.59% |
| Protocol Type | 5 | 6 | 40,512,664 | 93.78% |
| Protocol_name | 5 | TCP | 40,512,664 | 93.78% |
| Duration | 8 | 64 | 39,585,448 | 91.64% |
| Rate | 10609545 | 941.58805702099 | 398,610 | 0.92% |
| Srate | 10609545 | 941.58805702099 | 398,610 | 0.92% |
| Drate | 1 | 0.0 | 43,198,438 | 100.00% |
| fin_flag_number | 2 | 0 | 38,351,990 | 88.78% |
| syn_flag_number | 2 | 0 | 38,130,536 | 88.27% |
| rst_flag_number | 2 | 0 | 43,192,522 | 99.99% |
| psh_flag_number | 2 | 0 | 28,198,012 | 65.28% |
| ack_flag_number | 2 | 1 | 37,863,214 | 87.65% |
| urg_flag_number | 1 | 0 | 43,198,438 | 100.00% |
| ece_flag_number | 1 | 0 | 43,198,438 | 100.00% |

*Showing top 20 of 70 categorical features*

---

## 4. Class Distribution Analysis

### Distribution of column 'label'

| Class | Count | Percent |
|-------|-------|----------|
| 0 | 43,196,430 | 100.00% |
| 1 | 2,008 | 0.00% |

**Summary:**
- **Total classes**: 2
- **Most frequent class**: 0 (100.00%)
- **Least frequent class**: 1 (0.00%)
- **Imbalance ratio**: 21512.17:1

⚠️ **Highly imbalanced dataset!**

### Distribution of column 'subLabel'

| Class | Count | Percent |
|-------|-------|----------|
| 0 | 43,196,430 | 100.00% |
| collection | 920 | 0.00% |
| cleanup | 384 | 0.00% |
| discovery | 276 | 0.00% |
| credential access | 116 | 0.00% |
| command and control | 112 | 0.00% |
| persistence | 88 | 0.00% |
| exfiltration | 84 | 0.00% |
| lateral movement | 28 | 0.00% |

**Summary:**
- **Total classes**: 9
- **Most frequent class**: 0 (100.00%)
- **Least frequent class**: lateral movement (0.00%)
- **Imbalance ratio**: 1542729.64:1

⚠️ **Highly imbalanced dataset!**

### Distribution of column 'subLabelCat'

| Class | Count | Percent |
|-------|-------|----------|
| 0 | 43,196,430 | 100.00% |
| find files | 512 | 0.00% |
| create staging directory | 392 | 0.00% |
| stage sensitive files | 240 | 0.00% |
| create a new user in linux | 88 | 0.00% |
| advanced file search and stager | 84 | 0.00% |
| dump credentials from firefox browser | 60 | 0.00% |
| linux download file and run | 56 | 0.00% |
| compress staged directory | 56 | 0.00% |
| scan wifi networks | 52 | 0.00% |
| capture linux desktop | 48 | 0.00% |
| system owner/user discovery | 28 | 0.00% |
| start sandcat | 28 | 0.00% |
| permission groups discovery | 28 | 0.00% |
| network interface configuration | 28 | 0.00% |
| list os information | 28 | 0.00% |
| list directory | 28 | 0.00% |
| find local users | 28 | 0.00% |
| extract password with grep | 28 | 0.00% |
| exfil staged directory | 28 | 0.00% |
| dump history | 28 | 0.00% |
| download sandcat and lazagne | 28 | 0.00% |
| collect arp details | 28 | 0.00% |
| check python | 28 | 0.00% |
| add or copy content to clipboard | 28 | 0.00% |
| add command | 28 | 0.00% |

**Summary:**
- **Total classes**: 26
- **Most frequent class**: 0 (100.00%)
- **Least frequent class**: add command (0.00%)
- **Imbalance ratio**: 1542729.64:1

⚠️ **Highly imbalanced dataset!**

---

## 5. Feature Analysis and Correlations

⚠️ **Less than 2 numeric features found for correlation analysis**

### Cardinality Analysis - Categorical Features

---

### Key Findings

1. **Data Quality**: Needs attention - 100.00% completeness, 0 missing values, 21,599,219 duplicates
2. **Data Types**: 1 unique data types - 70 categorical, 0 numeric
3. **Class Distribution**: 2 classes found in 'label'
4. **High Cardinality**: 0 features with >90% unique values

### Suggested Next Steps

1. **Data Type Conversion**: Convert numeric features from string to appropriate numeric types
2. **Feature Engineering**: Remove constant features, consider dimensionality reduction for high-cardinality features
3. **Data Loading**: Investigate if additional data needs to be loaded
4. **Temporal Analysis**: Analyze patterns over time using timestamp features
5. **Preprocessing**: Prepare data for modeling with appropriate encoding strategies

---

## Appendix: Dataset Information

- **Dataset**: CIC_APT_IIoT_2024
- **Sample Size**: 43,198,438 records
- **Total Features**: 70
- **Database Size**: 34865.78 MB
- **Analysis Date**: 2026-01-25 20:38:10
- **Database**: SQLite (`../data/sqlite/data.db`)

---

*Report generated from dataset_analysis.ipynb notebook*
