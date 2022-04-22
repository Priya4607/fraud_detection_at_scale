# FRAUD DETECTION AT SCALE
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)

Anomaly detection models rely on sifting through a massive amount of historical data to identify patterns based on how fraudsters typically behave. Here, we focus more on the users spending patterns (the rate at which transactions occur differs from the usual spending patterns) within a specific window. What makes it fraudulent behavior depends on the average number of back-to-back transactions made using the same card within a short window. We do some feature engineering to select a set of features relevant to users spending patterns. We use these features to train an XGBoost model to pick unusual behavior in financial transactions.

---
## DATA GENERATION
Since we only analyze the spending patterns of user's card transactions, we generate fake data based on this [notebook](https://github.com/aws-samples/amazon-sagemaker-feature-store-streaming-aggregation/blob/main/notebooks/0_prepare_transactions_dataset.ipynb). However, the simulated data differ in terms of the number of records (over 6M historical transactions in this case) spread over a period of six months. [This script](./data_generation.py) simulates fake credit card transactions. Including the [dropbox link](https://www.dropbox.com/s/24dw7mc2wmrpuqp/transactions.csv?dl=0), just in case you choose to use the dataset directly.


To the run the file,

```
python generate_transactions.py
```

A sample dataset consist of the following headers, omitted some additional features like shipping/billing address, ZIP code etc for simplicity.
<center>

|Features|Description                              |
|:-------|:----------------------------------------|
| txn_id | Transaction ID                          |
| cc_num | Credit card numbers (10k unique numbers)| 
| ts     | Transaction timestamp                   | 
| amt    | Transanction amount                     | 
| label  | 0-genuine, 1-fraud                      |

</center>

---
## MODEL PERFORMANCE
This pipeline uses Apache's Spark MLlib and XGBoost (Extreme Gradient Boosting) model. Additionally, MLflow eases the process of tracking parameters/metrics and thus, helps in refining the model performance. Also, the pipeline implements k-fold cross-validation of the model to ensure the best fit. Utilized Area under the ROC curve (AUC) metric to evaluate the performance of the model.

To run the notebook, it is suggested to use analytic platforms such as Databricks (used community edition here).

Databricks cluster specification:
- Databricks run time - 10.4 LTS ML
- Apache spark version - 3.2.1


**_Note_**: The model has been trained on unbalanced dataset


Results are tabulated below:
<center>

|Dataset | Results (AUC) |
|:-------|---------------:
|   Train| 0.786         |
|   Test | 0.787         |

</center>

---
## EXPERIMENTAL FEATURES
An attempt to store ML features in a centralized repository using [Feast: An open-source feature store](https://feast.dev/). [This folder](./experiments/feature_store) consists of appropriate feature store configuration files and a script to create online feature stores.
`cc_weekly` and `cc_latest` are the two feature stores consisting of a weekly and recent (say in the past 10 min) aggregation of the raw dataset generated in the previous step grouped by credit card number.

<div style="text-align:center">
  <figure>
    <img src=./asset/architecture.png>
  <figure>
</div>
<center> Fig: Intended architecture </center>

**__TODO__**:
1. Integrate Kafka to ingest streaming data
---

## ATTRIBUTION
List of references used:
- [AWS samples](https://github.com/aws-samples/amazon-sagemaker-feature-store-streaming-aggregation) demonstrates the implementation of streaming feature aggregation using AWS SageMaker Feature Store.
- [MLflow](https://docs.databricks.com/applications/mlflow/) documentation.
