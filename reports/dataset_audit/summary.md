# Project Peregrine dataset audit

Audit date: **2026-10-23, America/Phoenix**. Physical record references are **1-based JSONL line numbers**. This audit writes reports only; it does not preprocess, convert, delete, train, or execute dataset code.

**Readiness: suitable raw material for pipeline pilots and a balanced tokenizer-development corpus, after targeted review; not a production-ready foundation-model training release.** Inspected all **11 JSONL files**, **60,078 parsed records**, **171,130,422 file bytes** (171.13 decimal MB). Found **0 invalid records**. All source SHA-256, sizes and mtimes remained unchanged: **True**.

Decoded training fields contain **164,285,370 characters** and **164,855,355 UTF-8 payload bytes**. The rough character-based estimate is **32.86–54.76 million tokens** (midpoint convention: 41.07M). These are heuristics, **not tokenized counts or statistical bounds**; code, Unicode and obfuscated strings may fall outside this range. JSON serialization bytes are never treated as tokens.

No dataset receives an unconditional **READY** verdict for production use. This does not mean every record is poor. Code is mostly recognizable source, FineWeb contains useful educational text, and many synthetic QA examples are mechanically correct. The unresolved issues are provenance/rights, sensitive material candidates, distribution, evaluation isolation, and selected extraction defects.

## Per-dataset inventory and decisions

| Dataset | Bytes | Records | Schema | Verdict | Intended stage |
|---|---:|---:|---|---|---|
| `datasets/code/cpp.jsonl` | 20,939,769 | 1,569 | language,text | **REVIEW REQUIRED** | coding pretraining; balanced tokenizer component |
| `datasets/code/java.jsonl` | 21,016,283 | 3,584 | language,text | **REVIEW REQUIRED** | coding pretraining; balanced tokenizer component |
| `datasets/code/javascript.jsonl` | 21,101,322 | 2,663 | language,text | **REVIEW REQUIRED** | coding pretraining; balanced tokenizer component |
| `datasets/code/python.jsonl` | 20,909,200 | 2,731 | language,text | **REVIEW REQUIRED** | coding pretraining; balanced tokenizer component |
| `datasets/code/rust.jsonl` | 20,868,506 | 2,709 | language,text | **REVIEW REQUIRED** | coding pretraining; balanced tokenizer component |
| `datasets/curated/gren_dataset.jsonl` | 454,677 | 2,138 | answer,question | **REVIEW REQUIRED** | instruction tuning after validation; small optional tokenizer supplement |
| `datasets/curated/peregrine_general_32180.jsonl` | 4,782,389 | 32,180 | answer,question | **NEEDS IMPROVEMENT** | instruction tuning after validation; small optional tokenizer supplement |
| `datasets/curated/peregrine_ml_ai_pretrain_text.jsonl` | 210,356 | 502 | text | **REVIEW REQUIRED** | small technical-text supplement after review; contains QA-style headings and code |
| `datasets/general/fineweb.jsonl` | 60,845,389 | 12,000 | text | **NEEDS IMPROVEMENT** | general pretraining; natural-language tokenizer component |
| `src/dataset_generator/code.jsonl` | 0 | 0 | empty | **NOT SUITABLE** | none (empty) |
| `src/dataset_generator/general.jsonl` | 2,531 | 2 | answer,question | **REVIEW REQUIRED** | instruction tuning after validation; small optional tokenizer supplement |

### Evidence for each verdict

- **datasets/code/cpp.jsonl — REVIEW REQUIRED:** source/revision/path/license metadata absent; sensitive and generated-code candidates require review.
- **datasets/code/java.jsonl — REVIEW REQUIRED:** source/revision/path/license metadata absent; sensitive and generated-code candidates require review.
- **datasets/code/javascript.jsonl — REVIEW REQUIRED:** source/revision/path/license metadata absent; sensitive and generated-code candidates require review.
- **datasets/code/python.jsonl — REVIEW REQUIRED:** source/revision/path/license metadata absent; sensitive and generated-code candidates require review.
- **datasets/code/rust.jsonl — REVIEW REQUIRED:** source/revision/path/license metadata absent; sensitive and generated-code candidates require review.
- **datasets/curated/gren_dataset.jsonl — REVIEW REQUIRED:** niche templated QA; pin Gren version and validate code semantics; origin/license absent.
- **datasets/curated/peregrine_general_32180.jsonl — NEEDS IMPROVEMENT:** short templated QA; reserve for SFT and group related tasks before splitting.
- **datasets/curated/peregrine_ml_ai_pretrain_text.jsonl — REVIEW REQUIRED:** small QA-style technical supplement; provenance and unverified technical examples need review.
- **datasets/general/fineweb.jsonl — NEEDS IMPROVEMENT:** educational prose with extraction, factual and boilerplate defects; source metadata absent.
- **src/dataset_generator/code.jsonl — NOT SUITABLE:** Empty file: no training signal.
- **src/dataset_generator/general.jsonl — REVIEW REQUIRED:** only two prototype synthetic SFT examples; generation and rights metadata absent.

## Format, lengths and Unicode

All nonempty files use consistent top-level string fields: `text`; `text, language`; or `question, answer`. JSON escapes were decoded before inspecting source code. Tabs, LF and CRLF are legitimate code whitespace. Missing/null/empty fields are measured independently in the CSV and JSON. No one-schema assumption or conversion was applied.

| Dataset | Text chars | Min / median / p99 / max chars | <80 chars | >100K chars |
|---|---:|---|---:|---:|
| `datasets/code/cpp.jsonl` | 19,981,585 | 115 / 4201 / 147876 / 438399 | 0 | 30 |
| `datasets/code/java.jsonl` | 19,923,277 | 102 / 2518 / 51050 / 348996 | 0 | 12 |
| `datasets/code/javascript.jsonl` | 19,892,716 | 101 / 1518 / 121780 / 453574 | 0 | 31 |
| `datasets/code/python.jsonl` | 19,919,154 | 101 / 2632 / 72182 / 412069 | 0 | 13 |
| `datasets/code/rust.jsonl` | 19,999,402 | 101 / 3022 / 61043 / 417750 | 0 | 14 |
| `datasets/curated/gren_dataset.jsonl` | 383,012 | 58 / 185 / 313 / 370 | 8 | 0 |
| `datasets/curated/peregrine_general_32180.jsonl` | 3,853,770 | 16 / 98 / 386 / 424 | 13,067 | 0 |
| `datasets/curated/peregrine_ml_ai_pretrain_text.jsonl` | 202,337 | 285 / 365 / 785 / 1464 | 0 | 0 |
| `datasets/general/fineweb.jsonl` | 60,127,697 | 500 / 3022 / 37316 / 550904 | 0 | 11 |
| `src/dataset_generator/code.jsonl` | 0 | None / None / None / None | 0 | 0 |
| `src/dataset_generator/general.jsonl` | 2,420 | 806 / 806 / 806 / 1614 | 0 | 0 |

Short correct QA, exception classes, headers and small snippets can be useful. Length flags are inspection thresholds, not rejection rules. Long code can be valid; packing/chunking must respect the future context budget and document boundaries.

| Dataset | Non-ASCII records | Controls | U+FFFD | Surrogates | Bidi controls | Mojibake candidates |
|---|---:|---:|---:|---:|---:|---:|
| `datasets/code/cpp.jsonl` | 103 | 0 | 2 | 0 | 0 | 0 |
| `datasets/code/java.jsonl` | 524 | 0 | 3 | 0 | 0 | 0 |
| `datasets/code/javascript.jsonl` | 360 | 7 | 2 | 0 | 0 | 1 |
| `datasets/code/python.jsonl` | 259 | 1 | 0 | 0 | 0 | 0 |
| `datasets/code/rust.jsonl` | 161 | 1 | 3 | 0 | 0 | 0 |
| `datasets/curated/gren_dataset.jsonl` | 3 | 0 | 0 | 0 | 0 | 0 |
| `datasets/curated/peregrine_general_32180.jsonl` | 5185 | 0 | 0 | 0 | 0 | 0 |
| `datasets/curated/peregrine_ml_ai_pretrain_text.jsonl` | 5 | 0 | 0 | 0 | 0 | 0 |
| `datasets/general/fineweb.jsonl` | 8132 | 0 | 7 | 0 | 0 | 19 |
| `src/dataset_generator/code.jsonl` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/dataset_generator/general.jsonl` | 1 | 0 | 0 | 0 | 0 | 0 |

Controls and apparent mojibake can occur intentionally in regexes, test fixtures, string literals or terminal examples. CJK comments and mathematical symbols are valuable coverage, not corrupt text. Review flagged references in context.

## Code corpus

| Language | Records | Payload bytes | Share of code characters | Newline records | Tab records | CRLF records | Generated cues | Bundle/vendor cues | Minified/long-line candidates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cpp | 1,569 | 20,012,628 | 20.04% | 1569 | 422 | 117 | 48 | 1 | 2 |
| java | 3,584 | 20,017,463 | 19.98% | 3580 | 848 | 241 | 218 | 2 | 4 |
| javascript | 2,663 | 20,000,478 | 19.95% | 2595 | 320 | 117 | 131 | 91 | 135 |
| python | 2,731 | 20,001,137 | 19.98% | 2731 | 137 | 134 | 120 | 1 | 5 |
| rust | 2,709 | 20,014,532 | 20.06% | 2709 | 119 | 23 | 137 | 1 | 1 |

Candidate **character mass** helps interpret record counts:

| Code file | Generated-cue character share | Bundle/vendor-cue character share | Minified/large-line character share |
|---|---:|---:|---:|
| `datasets/code/cpp.jsonl` | 7.36% | 0.04% | 0.64% |
| `datasets/code/java.jsonl` | 16.76% | 0.05% | 0.43% |
| `datasets/code/javascript.jsonl` | 17.01% | 16.25% | 20.78% |
| `datasets/code/python.jsonl` | 10.28% | 0.35% | 0.56% |
| `datasets/code/rust.jsonl` | 20.96% | 0.03% | 0.04% |

These categories overlap and are heuristic. JavaScript has a materially larger minified/large-line candidate share than the other language files; do not add shares or interpret them as a measured rejection rate. Useful generated interfaces and bundled libraries may still be retained at deliberate weights.


Python 3 AST parsing accepted **2,610** and rejected **121** records using Python 3.14.4. Rejections include historical Python 2, snippets, intentional negative tests and real syntax defects. They are not a compile/run failure rate. Other languages were checked with source cues and manual excerpts, not compilers. No dependencies were imported from dataset source and no dataset code was executed.

The code files carry the declared Python, C++, Rust, Java and JavaScript labels. Cue counts in the JSON are overlapping and heuristic, not an independent language classifier. Modern C++ and JavaScript may embed other languages; C++ also includes C-like headers. There are no dedicated C, Go, TypeScript, C#, shell or SQL datasets. Gren appears in a separate small QA collection.

Generated register bindings, repeated libraries and bundles consume vocabulary and training budget when dominant. Useful tests, documentation, comments and short files should remain available. Do not strip all comments or license notices. An obfuscated JavaScript string at `datasets/code/javascript.jsonl:2218` is a strong review/exclusion candidate for a future derived training manifest; ordinary punctuation-heavy code is not.

## Duplication and overlap

Complete document hash scans found **11 exact redundant records** in 11 groups, and **11 whitespace-normalized redundant records** in 11 groups. These are separate totals; do not add them. SHA-256 hashes cover all extracted document text; QA documents preserve ordered field boundaries. No Unicode/case folding was applied.

Cross-dataset shared unique document counts: exact `{}`; whitespace-normalized `{}`. These tests do not establish the absence of copied paragraphs, library fragments or task-family overlap.

| Dataset | Exact redundant | Whitespace-normalized redundant | Near-positive anchors / sampled anchors | Detector-positive 95% interval |
|---|---:|---:|---|---|
| `datasets/code/cpp.jsonl` | 0 | 0 | 0 / 400 | [0, 0.009513] |
| `datasets/code/java.jsonl` | 0 | 0 | 0 / 400 | [0, 0.009513] |
| `datasets/code/javascript.jsonl` | 0 | 0 | 0 / 400 | [0, 0.009513] |
| `datasets/code/python.jsonl` | 0 | 0 | 0 / 400 | [0, 0.009513] |
| `datasets/code/rust.jsonl` | 0 | 0 | 0 / 400 | [0, 0.009513] |
| `datasets/curated/gren_dataset.jsonl` | 0 | 0 | 9 / 400 | [0.011881, 0.042203] |
| `datasets/curated/peregrine_general_32180.jsonl` | 0 | 0 | 0 / 400 | [0, 0.009513] |
| `datasets/curated/peregrine_ml_ai_pretrain_text.jsonl` | 0 | 0 | 0 / 400 | [0, 0.009513] |
| `datasets/general/fineweb.jsonl` | 11 | 11 | 0 / 400 | [0, 0.009513] |
| `src/dataset_generator/code.jsonl` | 0 | 0 | 0 / 0 | [None, None] |
| `src/dataset_generator/general.jsonl` | 0 | 0 | 0 / 2 | [0, 0.657628] |

64 deterministic minhash-like salted uint64 minima over case-sensitive lexical 5-token shingles; 16 bands x 4; >=10 lexical tokens; feature cap 8192 for signatures; >=0.65 signature equality shortlist; exact full-shingle Jaccard >=0.80 verification. Full-corpus hash index with seeded uniform per-file anchor samples. Normalized exact matches excluded.

Detector recall is uncalibrated; intervals describe detector-positive anchor rate, not a proven corpus near-duplicate rate. No near search on <10 lexical token anchors. Caps and skipped buckets are recorded; partial/translated/renamed-code matches may be missed. No claim of exhaustive pairwise near scan.

The near scan indexes the full corpus but queries up to 400 seeded uniform anchors per file. A positive means an anchor has at least one detected nonexact partner anywhere in the corpus. Wilson intervals apply to the detector-positive rate; unknown recall and anchor dependence limit interpretation. These figures are not counts of all duplicate pairs or precise removable corpus mass. Shorter-than-10-lexical-token anchors are not eligible. Caps/skips, exact matches excluded, verified pair counts and example pairs are recorded per dataset.

The full blank-line block scan found **2,600 repeated block hashes**, including legitimate license text and common declarations. The short QA collections also repeat task families and answers; exact document uniqueness does not imply diverse information. Per-file template and answer statistics are in the JSON.

## Actual content and factual review

Qualitative review covered 128 seeded excerpts across all 10 nonempty files, plus initial peeks and targeted issues. Exact reviewed line references and the sampling algorithms are in `quality_metrics.json.manual_review`. Longer code/web records were reviewed through excerpts, not every full document. This review cannot estimate a corpus-wide factual-error rate.

The general QA collection covers arithmetic, date arithmetic, formatting, short transformations and simple Python tasks. Its narrow validators checked 1,210 integer arithmetic answers, 240 weekdays and 413 literal JSON arrays, with no mismatches. All other answers remain outside these validators. The Gren examples checked against official core 7.0.0 String and Dict documentation were plausible; other modules and compilability remain unverified. The ML/AI examples include sensible caveats around top-k ties, mean loss reduction, mixed precision and deterministic splits, but no runtime/semantic certification was performed.

Selected meaningful defects include a historical contradiction in FineWeb line 9111, navigation at 2977, product/catalogue boilerplate at 3557 and 7119, flattened Python at 692, degraded superscripts at 3010, and a mid-sentence opening at 11978. These support targeted review, not a claim that the whole web file is unusable. The structured synthetic style of curated collections is visible, but the audit cannot establish their generating model or authorship.

## Tokenizer suitability

**No trained tokenizer model or vocabulary artifact was found.** Round-trip fidelity, unknown/fallback rates, identifier fragmentation, compression and actual token counts therefore could not be measured. Installing SentencePiece does not supply a Peregrine tokenizer. The audit did not train one.

The available JSONL payloads offer useful natural English, educational/scientific vocabulary, the five code languages, indentation and some mathematics/Unicode. They can support an initial 32K tokenizer experiment after provenance, privacy and representative sampling decisions. Tokenizer readiness remains unproven: educational English dominates the prose; long-form diverse writing, rigorous mathematical notation, additional code languages and rare Unicode need deliberate holdouts and possibly additional sources. Character tables in the JSON describe coverage, not compression.

`src/tokenizer/tokenizer.py` requests BPE, 32,000 pieces, byte fallback, identity normalization, 0.9995 character coverage and `remove_extra_whitespaces=False`. `hard_vocab_limit=False` permits fewer than 32,000 pieces. These settings are not round-trip test results. Test spaces, tabs, LF, CRLF, blank lines, trailing whitespace, literal U+2581, emoji and mathematical text after a model exists. The line-based text input also needs explicit handling for document/newline representation.

`src/tokenizer/peregrine_tokenizer_starter.txt` is the configured input and contains repeated prose variants and recurring code structures. The C++ extract is a separate input and is not referenced by the trainer. Its Windows newline expansion and concatenated boundaries are confirmed by whole-file hashes; see `tokenizer.cpp_extract_check`. Do not use either uncritically as the final representative training corpus.

| Existing plain-text tokenizer input | Bytes | Nonempty lines / distinct normalized lines | Longest line bytes | Lines >4192 bytes |
|---|---:|---|---:|---:|
| `src/tokenizer/extracted_texts.txt` | 20,582,085 | 488179 / 282616 | 44447 | 5 |
| `src/tokenizer/peregrine_tokenizer_starter.txt` | 654,873 | 11376 / 2712 | 481 | 0 |

Repeated braces and ordinary syntax naturally inflate line-duplicate statistics; the starter review additionally found repeated semantic prose variants. A future trainer must account for its maximum input sentence length rather than silently losing long source lines. [SentencePiece options](https://github.com/google/sentencepiece/blob/master/doc/options.md) describe the relevant controls.

## Pretraining stages and experimental scale

The five code datasets provide 99,716,134 decoded characters (roughly 19.94–33.24M heuristic tokens); FineWeb provides 60,127,697 characters (roughly 12.03–20.04M). These are the primary coding and general pools. Curated QA should be held separately for SFT; the 502-record technical text file is a small supplement, not a broad scientific corpus.

The repository has no usable token-budget/model-size experiment configuration: `src/main.py`, compute-budget, methodology, dataset-strategy, roadmap, decisions and research-question documents are empty. The README describes small experiments and an eventual 14B model. The present unique text is enough for tokenizer/data-loader pilots and deliberately data-limited tiny experiments; it is far too little to support a high-quality 14B foundation model from scratch. Repeated epochs do not create new information. A specific experimental sufficiency decision requires parameter count, unique-token budget, epochs, mixture and held-out tasks.

As scale context only, 20 tokens per parameter would be 10B tokens for 500M parameters and 280B for 14B—hundreds to thousands of times this corpus. This is an illustrative rule of thumb, not a mandatory budget or a quality guarantee; [Hoffmann et al.](https://arxiv.org/abs/2203.15556) studied joint parameter/data scaling.

Files are separated by directory, but no active MaxText loader was found to verify actual stage mixing. Recursive loading of all JSONL would mix source code, plain text and QA and would silently change the curriculum. General QA contains Python examples, and the ML/AI text contains code fences; these are expected mixed-content supplements, not evidence that the general collector accidentally appended a code dataset. The general collector references Wikipedia, but **no local Wikipedia JSONL exists**.

## Privacy, rights and evaluation boundaries

Full extracted-text regex scans returned these **record-level candidates**, not confirmed exposures: `{"email_like": 737, "street_address_like": 86, "ipv4_like": 274, "phone_like": 123, "credential_assignment": 56, "known_token_pattern": 8, "private_key_block": 1, "ssn_like": 7}`. Pattern families overlap. Complete matched credentials, email addresses, phone-like numbers and private-key bodies are not included in reports. Context classifications and redacted record references are in the JSON. Unknown/obfuscated formats and arbitrary PII may be missed; no remote credential checks were made.

All nonempty JSONL schemas lack explicit source URL/repository path/revision/license/generator metadata. Collector code suggests FineWeb-Edu and The Stack-dedup, but it is not a signed acquisition manifest and drops upstream metadata. The Stack requires attention to original licenses and attribution, version/removal handling, and redistribution terms; its card acknowledges license-detector errors. FineWeb-Edu declares ODC-By and Common Crawl terms. The project Apache-2.0 license does not automatically relicense collected documents. Curated/synthetic origins and generating-model terms remain unknown. License headers are hints for review, not legal determinations. [The Stack card](https://huggingface.co/datasets/bigcode/the-stack-dedup/blob/main/README.md), [FineWeb-Edu card](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu/blob/main/README.md).

No local evaluation/validation JSONL or split metadata was found, and no external benchmark corpora were supplied. Keyword references were scanned, but **benchmark decontamination was not performed**. Repeated templates and source families can contaminate future random record splits even without exact duplicates. Treat benchmark cleanliness as unknown. Pin independent evaluation sources first, then compare hashes, normalized prompts, long shared substrings and source/task groups before training.

## Reproduction and limitations

Run from the project root:

```powershell
python reports/dataset_audit/audit.py
```

If `python` resolves to the inert Windows system entry, invoke the installed Python executable directly. The scan uses the standard library; an already-installed NumPy accelerates signatures and is optional. SentencePiece is only used if an existing `.model` is found. No package installation is needed here. Progress is printed by file/record count with no training text.

Full-corpus tests: discovery, raw SHA-256/size, strict parsing, field/schema/null/empty counts, decoded-text lengths/Unicode, heuristic content/code/privacy/license signals, exact/whitespace document hashes, normalized QA component hashes, numeric/quoted-literal template hashes, blank-line block hashes and narrow QA validators. Sampled tests: near-duplicate anchors and qualitative excerpt review. Unperformed tests: full semantic verification, general language identification, all-language compilation, execution, exhaustive PII/legal review, external benchmark matching and model tokenization.

No heuristic signal alone authorizes deletion. See `issues.md` for severity and examples, `recommendations.md` for the ordered work plan, `dataset_inventory.csv` for every file, and `quality_metrics.json` for full definitions, counts, source fingerprints, references and limitations.

## Targeted follow-up findings

`datasets/code/javascript.jsonl:1525` is a **strong source-training exclusion candidate**: 47,304 decoded characters include 12,227 U+FFFD replacement characters and 9,820 unusual controls. A JavaScript bundle wrapper and source-map reference surround a binary-like payload; this is materially different from ordinary source syntax or a few deliberate control-character tests. The wrapper was not compiled and is not claimed to be syntactically invalid. This record is only 0.24% of JavaScript character mass; do not generalize it to the entire file.

Sensitive-context review found two RSA key blocks in Python line 630 in apparent unit-test fixtures; the AWS-shaped value in Python line 1952 is explicitly an example, and the Google-key-shaped identifier at 1675 is named `_CELLSET_ID`. Java line 2951 and JavaScript lines 351, 450, 1252, 1971 and 2024 contain Google-service/API-key-shaped values worth provenance/restriction review. **No live credential exposure was established.** Public attribution emails and test/private-network IPs also occur; regex totals are not a count of confirmed privacy violations.

The full normalized QA consistency check found **0** repeated-question groups with differing normalized answers. Different wording or differently expressed equivalent answers are beyond this check. The largest QA collection accounts for 53.56% of records but only 2.35% of decoded characters, illustrating why record-weighted tokenizer sampling would overrepresent short synthetic tasks.
