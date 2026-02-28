# Dataset Analysis Report
## Exploratory Dataset Analysis

This report presents a complete exploratory analysis of the CIC_APT_IIoT_2024 dataset.

**Analysis Date**: 2026-02-17 20:39:49
**Dataset**: CIC_APT_IIoT_2024
**Sample Size**: 43,198,438 records

---

## 1. Initial Dataset Characterization

### Dataset Dimensions
- **Rows**: 43,198,438
- **Columns**: 70

### Data Types
- **float**: 19 columns
- **int**: 48 columns
- **string**: 3 columns

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

### Missing values visualization

![Missing values per column and completeness distribution](../images/CIC_APT_IIoT_2024_missing_values.png)

### Duplicate Analysis

- **Duplicate records**: 21,599,219
- **Duplicate percentage**: 50.00%
- **Unique records**: 21,599,219

⚠️ **Warning**: 50.00% of records are duplicates

---

## 3. Descriptive Statistics

### Feature Classification
- **Numeric**: 67
- **Categorical**: 3

### Descriptive Statistics - Numeric-Like Features (Mean, Std, Min, Max)

| Column | Count | Mean | Std | Min | Max |
|--------|-------|------|-----|-----|-----|
| ts | 43,198,438 | 1701427156.7717 | 177757.2738 | 1701118660.778 | 1701728424.5637 |
| CoAP | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| psh_flag_number | 43,198,438 | 0.3472 | 0.4761 | 0.0 | 1.0 |
| Tot size | 43,198,438 | 94.0283 | 159.4453 | 54.0 | 1514.0 |
| ARP | 43,198,438 | 0.0064 | 0.0797 | 0.0 | 1.0 |
| IGMP | 43,198,438 | 0.0 | 0.0014 | 0.0 | 1.0 |
| subLabel | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| UDP | 43,198,438 | 0.0556 | 0.2291 | 0.0 | 1.0 |
| DNS | 43,198,438 | 0.0363 | 0.1871 | 0.0 | 1.0 |
| Source Port | 43,198,438 | 26196.5838 | 24333.9947 | 0.0 | 65515.0 |
| Drate | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| min_duration | 43,198,438 | 1701422122.0757 | 2769666.6609 | 0.0 | 1701728422.6759 |
| flow_idle_time | 43,198,438 | 26017395.3714 | 208781930.8561 | 0.0 | 1701728422.6759 |
| urg_flag_number | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| Min | 43,198,438 | 72.0452 | 72.4545 | 54.0 | 1514.0 |
| Max | 43,198,438 | 117.1454 | 208.0085 | 54.0 | 1514.0 |
| Sequence number | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| Destination Port | 43,198,438 | 24227.5604 | 25347.5766 | 0.0 | 64422.0 |
| cwr_flag_number | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| TCP | 43,198,438 | 0.9378 | 0.2415 | 0.0 | 1.0 |
| IRC | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| fin_flag_number | 43,198,438 | 0.1122 | 0.3156 | 0.0 | 1.0 |
| Radius | 43,198,438 | 27.0743 | 124.0741 | 0.0 | 1032.3759 |
| Weight | 43,198,438 | 141.542 | 120.8824 | 1.0 | 361.0 |
| Rate | 43,198,438 | 446.657 | 1696.7682 | 0.0 | 2097152.0 |
| std_duration | 43,198,438 | 161.5396 | 257.1921 | 0.0 | 1554.0341 |
| MAC | 43,198,438 | 803279.173 | 64436.1008 | 0.0 | 808448.0 |
| SMTP | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| IAT | 43,198,438 | 85081208.4424 | 370837792.2794 | 0.0 | 1701728423.5682 |
| HTTP | 43,198,438 | 0.0155 | 0.1235 | 0.0 | 1.0 |
| ack_flag_number | 43,198,438 | 0.8765 | 0.329 | 0.0 | 1.0 |
| Number | 43,198,438 | 9.4997 | 5.7662 | 0.0 | 19.0 |
| Covariance | 43,198,438 | 8063.7045 | 58086.5452 | 0.0 | 532900.0 |
| Duration | 43,198,438 | 63.2853 | 11.8875 | 0.0 | 255.0 |
| rst_count | 43,198,438 | 6113.4147 | 10311.8783 | 0.0 | 38219.0 |
| Header_Length | 43,198,438 | 541935.805 | 1025846.1411 | 0.0 | 9778788.0 |
| DHCP | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| IPv | 43,198,438 | 0.9936 | 0.0797 | 0.0 | 1.0 |
| Std | 43,198,438 | 19.155 | 87.7473 | 0.0 | 730.0 |
| Fragments | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| DS status | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| flow_duration | 43,198,438 | 537.4956 | 863.6241 | 0.0 | 3140.7259 |
| Srate | 43,198,438 | 446.657 | 1696.7682 | 0.0 | 2097152.0 |
| label | 43,198,438 | 0.0 | 0.0068 | 0.0 | 1.0 |
| subLabelCat | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| syn_count | 43,198,438 | 4.4833 | 4.6861 | 0.0 | 78.0 |
| max_duration | 43,198,438 | 1701422667.1161 | 2769666.5145 | 0.0 | 1701728424.5637 |
| Tot sum | 43,198,438 | 987.2794 | 1606.1494 | 54.0 | 30280.0 |
| ece_flag_number | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| urg_count | 43,198,438 | 3988.4839 | 6807.8228 | 0.0 | 25250.0 |
| ack_count | 43,198,438 | 1.1761 | 2.774 | 0.0 | 32.0 |
| sum_duration | 43,198,438 | 10573332563198.977 | 17617766453301.305 | 0.0 | 65025605596224.01 |
| flow_active_time | 43,198,438 | 537.4956 | 863.6241 | 0.0 | 3140.7259 |
| Telnet | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| Variance | 43,198,438 | 0.8052 | 0.3961 | 0.0 | 1.0 |
| ICMP | 43,198,438 | 0.0002 | 0.0135 | 0.0 | 1.0 |
| LLC | 43,198,438 | 0.9936 | 0.0797 | 0.0 | 1.0 |
| Magnitue | 43,198,438 | 12.9038 | 4.6419 | 10.3923 | 55.0273 |
| average_duration | 43,198,438 | 1701422389.3056 | 2769666.5661 | 0.0 | 1701728422.7393 |
| syn_flag_number | 43,198,438 | 0.1173 | 0.3218 | 0.0 | 1.0 |
| Protocol Type | 43,198,438 | 6.5723 | 2.5757 | 0.0 | 17.0 |
| fin_count | 43,198,438 | 0.0007 | 0.1432 | 0.0 | 77.0 |
| rst_flag_number | 43,198,438 | 0.0001 | 0.0117 | 0.0 | 1.0 |
| SSH | 43,198,438 | 0.0005 | 0.0234 | 0.0 | 1.0 |
| Protocol Version | 43,198,438 | 0.0 | 0.0 | 0.0 | 0.0 |
| AVG | 43,198,438 | 94.027 | 131.713 | 54.0 | 1514.0 |
| HTTPS | 43,198,438 | 0.0026 | 0.0511 | 0.0 | 1.0 |

### Descriptive Statistics - Categorical Features

| Column | Count | Unique_Values | Mode | Mode_% |
|--------|-------|---------------|------|-------|
| Source IP | 43198438 | 64 | 172.16.64.128 | 56.36% |
| Destination IP | 43198438 | 87 | 172.16.64.128 | 34.32% |
| Protocol_name | 43198438 | 5 | TCP | 93.78% |

### Numeric features - Distributions and boxplots

![Numeric features distributions](../images/CIC_APT_IIoT_2024_numeric_distributions.png)

![Boxplots - outlier detection](../images/CIC_APT_IIoT_2024_boxplots.png)

---

## 4. Class Distribution Analysis

### Number of classification columns (label column):

- **label**
- **subLabel**
- **subLabelCat**

#### Distribution of column 'label'

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

#### Distribution of column 'subLabel'

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

#### Distribution of column 'subLabelCat'

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

### Class distribution - Bar and pie charts

![Class distribution - bar](../images/CIC_APT_IIoT_2024_class_distribution_bar.png)

![Class distribution - pie](../images/CIC_APT_IIoT_2024_class_distribution_pie.png)

---

## 5. Feature Analysis and Correlations

### Correlation matrix

![Correlation heatmap](../images/CIC_APT_IIoT_2024_correlation_heatmap.png)

![Strong correlations](../images/CIC_APT_IIoT_2024_strong_correlations.png)

### Cardinality Analysis - Categorical Features

**Cardinality Categories:**
- **High** (>50% unique): 0 features
- **Medium** (10-50% unique): 0 features
- **Low** (<10% unique): 3 features

---

### Key Findings

1. **Data Quality**: Needs attention - 100.00% completeness, 0 missing values, 21,599,219 duplicates
2. **Data Types**: 3 unique data types - 3 categorical, 67 numeric
3. **Class Distribution**: 2 classes found in 'label'
4. **High Cardinality**: 0 features with >90% unique values
## Appendix: Dataset Information

- **Dataset**: CIC_APT_IIoT_2024
- **Sample Size**: 43,198,438 records
- **Total Features**: 70
- **Database Size**: 36565.76 MB
- **Analysis Date**: 2026-02-17 20:40:40
- **Database**: SQLite---

*Report generated from dataset_analysis.ipynb notebook*
