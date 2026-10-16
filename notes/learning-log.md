# Learning Log — severity-classifier

## Day 7 (Oct 15) — Ticket CBOPS-1427: data acquisition + severity labels

### What the ticket asks
Baseline text classifier that reads a consumer complaint narrative and suggests
high / medium / low severity, so ops reviewers work the queue in risk order.
Reviewer stays the decision-maker; the model only sorts the line.
Pipeline: prepare_data -> train -> evaluate, per-class P/R/F1, imbalance handled.

### What I built today
- `src/extract_data.py` — reads CFPB monthly archive zips in 100k-row chunks,
  keeps credit card rows that have a narrative, saved 5,000 rows.
- `src/prepare_data.py` — weak-supervision labeling: maps Issue/Sub-issue
  categories to severity using my documented rulebook.
- `play_api_probe.py` — experiment proving the CFPB search API and detail
  endpoint do NOT return narratives (kept as a record).
- Output: `data/labeled_complaints.csv` — 5,000 rows of (text, severity).

### The data hunt (4 failures before success)
1. CSV export from the search API: no narrative column at all.
2. JSON API (search + detail endpoints): returns 15 metadata fields, narrative
   missing in all 2,000 records — proved with a key-union check, not assumed.
3. Full bulk download (338MB): no narrative column either.
4. Root cause: CFPB STOPPED publishing complaint narratives on Aug 14, 2026
   (policy change). Not my code, not my request — the source itself changed.
5. Fix: CFPB's FOIA reading room hosts archived monthly exports WITH
   narratives. Downloaded May/June/July 2026, got my 5,000 rows.

### Labeling rulebook (weak supervision)
Test for every category: what happened to the customer?
- Money/identity STOLEN -> high (fraud sub-issue "charged for something you
  did not purchase", fraud alerts/security freezes, improper use of report,
  credit monitoring/identity theft)
- Money WRONG -> medium (billing disputes, fees/interest, payment problems,
  incorrect info on report, investigation problems, struggling to pay)
- SERVICE matter -> low (getting a card, closing account, features, marketing,
  trouble using card)
Known limitation (for README): Issue categories are coarse — reading sample
narratives showed mixed stories inside one category. Labels are rules-based
proxies, not human ground truth.

### The imbalance (the trap from the ticket, now live in my data)
high 415 (8.3%) / medium 2,551 (51%) / low 2,034 (41%).
A model that never predicts "high" is right 91.7% of the time on accuracy —
exactly the failure the reviewer rejected last quarter. This is why per-class
precision/recall/F1 is required, not aggregate accuracy.

### Errors I debugged today (and the decode for each)
- 23B / 167B "downloads": tiny file = an error message wearing a .json
  costume. cat it first. curl -o saves error bodies silently — use curl -f.
- "upstream connect error / Connection refused": gateway error = THEIR server,
  not my request. Retry is legitimate.
- "No such file or directory" twice: I ran a script before creating the file,
  then created it in the WRONG project (docqa-service instead of
  severity-classifier). VS Code sidebar title = which house I'm editing in;
  terminal prompt = which house I'm running in. They must match.
- SSL CERTIFICATE_VERIFY_FAILED: Mac python.org Python ships without linking
  its trusted-CA list. One-time fix: Install Certificates.command. In stacked
  tracebacks the real error is the FIRST traceback's last line.
- KeyError 'Consumer complaint narrative': I guessed a column name instead of
  asking the file. nrows=0 + repr() shows real column names cheaply.
- Ran unchanged code after a failed edit: grep first, confirm the fix landed
  on disk, THEN run. Edit lekunda re-run = same error, guaranteed.
- KeyError 'severity' while "Severity" printed fine: Python is case-sensitive;
  my paste capitalized one name. sed fixed every occurrence at once.

### Estimation lesson
My guess for credit-card-with-narrative rows per 100k: 15-20k. Actual: ~1k.
I forgot funnels multiply: product share (~4%) x narrative consent (~35%)
= ~1.4%. Estimate every stage, then multiply.

### Remember
- Data pipeline fails for 3 reasons: my code, my request, or the source
  changed. Today was the third — and only measuring proved it.
- Big file = read in buckets (chunked), never all at once.
- Weak supervision = labels from rules when nobody hand-labeled; document the
  rules AND their limitation.
- 8.3% minority class is where the whole evaluation fight will happen.

### Next (Day 7 part 2 — due Oct 16)
TF-IDF + logistic regression from zero, train/test split, per-class P/R/F1,
class imbalance handling with before/after evidence, README.

## Day 7 part 2 (Oct 16) — train, evaluate, and the accuracy trap settled

### What I built
- `play_tfidf.py` — saw TF-IDF scores with my own eyes: "stole" 0.46 vs
  "card" 0.27. Twist: in a 3-sentence corpus even "from" looks rare —
  TF-IDF's power comes from corpus size.
- `src/train.py` — 80/20 stratified split (hide the exam), TF-IDF
  (vocab: 13,727 — my guess was 3-5k; real text is messier), logistic
  regression (per-word weighted voting, one scoreboard per class).
- `src/evaluate.py` — per-class P/R/F1 + confusion matrix on the held-out
  1,000.
- `README.md` — labeling rules, before/after table, trade-off reasoning.

### The before/after (the whole point of the ticket)
BEFORE (no imbalance handling): accuracy 0.77, high recall 0.19 —
16 of 83 fraud complaints caught, 67 sitting behind billing questions.
A good report card on a dangerous model. The 91% trap, live.
AFTER (class_weight="balanced" — bigger fine for each rare-class mistake;
deep learning twin: weighted cross-entropy): accuracy 0.75, high recall
0.64 — 53 of 83 caught. Accuracy went DOWN, model got BETTER.

### The trade and why it's right
Price paid: high precision 0.53 -> 0.40 (more false alarms), medium recall
0.85 -> 0.73 (59 mediums now flagged high — I predicted medium would pay).
A missed fraud costs money, trust, and regulatory pain; a false alarm costs
a reviewer a few minutes. In this business, recall on high wins.
Still honest: 30 of 83 missed. Baseline, not a victory lap.

### Remember
- Accuracy is a report card that can hide a dangerous model; per-class
  recall on the minority class is where the truth lives.
- Class weights = bigger fines for rare-class mistakes. Same idea as
  weighted cross-entropy in deep learning.
- Train/test split = hide the exam; stratify = same class mix in the exam.
- touch creates an EMPTY file; creating a file is not filling it. wc first.
- My predictions are getting better: accuracy "below 75" (actual 75-77),
  high recall "30%" (actual 19%), "medium will pay the price" (it did).