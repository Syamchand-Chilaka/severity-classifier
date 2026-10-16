# severity-classifier (CBOPS-1427)

Baseline model that reads a consumer complaint narrative and suggests
high / medium / low severity so reviewers can work the queue in risk order.
The reviewer remains the decision-maker; the model only orders the queue.

## Data
Public CFPB consumer complaints (credit card, with narratives), from the
CFPB FOIA narratives archive (May-July 2026 monthly exports; the live
database stopped publishing narratives on Aug 14, 2026). 5,000 rows.

## Labeling rules (weak supervision)
No human severity labels exist, so labels are derived from Issue/Sub-issue
categories. Test applied per category: what happened to the customer?
- STOLEN (money/identity): fraud charge sub-issue, fraud alerts/security
  freezes, improper use of report, credit monitoring/identity theft -> high
- WRONG (money/records): billing disputes, fees/interest, payment problems,
  incorrect report info, investigation problems, struggling to pay -> medium
- SERVICE: getting a card, closing account, features, marketing, trouble
  using card -> low
Limitation: categories are coarse; sampled narratives show mixed stories
within one category. Labels are rule-based proxies, not ground truth.

## Class imbalance (and why accuracy alone is rejected)
Distribution: high 415 (8.3%) / medium 2,551 / low 2,034. A model that never
predicts "high" scores ~92% accuracy with 0% fraud recall - the exact
failure rejected last quarter. Evaluation is therefore per-class P/R/F1.

## Results (TF-IDF + logistic regression, 80/20 stratified split)
| metric          | before (no weighting) | after (class_weight=balanced) |
|-----------------|-----------------------|-------------------------------|
| high recall     | 0.19 (16/83)          | 0.64 (53/83)                  |
| high precision  | 0.53                  | 0.40                          |
| accuracy        | 0.77                  | 0.75                          |

Trade accepted: a missed fraud complaint costs far more (customer harm,
trust, regulatory exposure) than a reviewer seeing a false alarm early.
Known gap: 30/83 high cases still missed. Next steps: better labels, more
high-class data, threshold tuning, transformer baseline (CBOPS-1431).

## How to run
    python3 src/extract_data.py    # CFPB archives -> data/credit_card_narratives.csv
    python3 src/prepare_data.py    # apply labeling rules -> data/labeled_complaints.csv
    python3 src/train.py           # TF-IDF + logistic regression -> models/baseline.joblib
    python3 src/evaluate.py        # per-class P/R/F1 + confusion matrix