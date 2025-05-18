# 🧾 Data Quality Report
Generated: 2025-05-18 21:12:11

## 🗂 Dataset Overview
- Rows: 5
- Columns: 4

## 📊 Summary Statistics
|        |        id | name   | email             |   age |
|:-------|----------:|:-------|:------------------|------:|
| count  |   5       | 4      | 4                 |     4 |
| unique | nan       | 4      | 4                 |     4 |
| top    | nan       | Alice  | alice@example.com |    30 |
| freq   | nan       | 1      | 1                 |     1 |
| mean   |   3       | nan    | nan               |   nan |
| std    |   1.58114 | nan    | nan               |   nan |
| min    |   1       | nan    | nan               |   nan |
| 25%    |   2       | nan    | nan               |   nan |
| 50%    |   3       | nan    | nan               |   nan |
| 75%    |   4       | nan    | nan               |   nan |
| max    |   5       | nan    | nan               |   nan |

## 🔎 Missing Values
|       |   0 |
|:------|----:|
| id    |   0 |
| name  |   1 |
| email |   1 |
| age   |   1 |

## ⚠️ Detected Issues
- Row 3: 'age' is not a number
- Row 4: 'name' is missing

## 🤖 AI Insights
The 'email' field contains 20% missing values. Consider applying a format validator.
'age' should be normalized and strictly numeric. Missing values may require imputation or filtering.

## ✅ Recommendations
- Standardize formats (e.g., dates, numeric fields)
- Handle missing values (impute or drop)
- Validate field types and business rules