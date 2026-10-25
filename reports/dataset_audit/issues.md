# Findings ranked by severity

Severity reflects impact if the material were used unchanged. Candidate matches are explicitly distinguished from confirmed defects. All references are 1-based JSONL lines; sensitive values are redacted.

## High — sensitive material and unresolved code rights

Review private-key/token/credential candidates before admitting affected source groups to a training manifest. Test keys and placeholders may be deliberate fixtures; a pattern match does not establish a live credential. No key or token was tested against a service. Excerpts are omitted for these findings.

| Dataset | Private-key records | Known-token-pattern records | Credential-assignment records | Email-like records | Confidentiality markers |
|---|---:|---:|---:|---:|---:|
| `datasets/code/cpp.jsonl` | 0 | 0 | 0 | 105 | 0 |
| `datasets/code/java.jsonl` | 0 | 1 | 10 | 184 | 10 |
| `datasets/code/javascript.jsonl` | 0 | 5 | 16 | 80 | 0 |
| `datasets/code/python.jsonl` | 1 | 2 | 27 | 173 | 3 |
| `datasets/code/rust.jsonl` | 0 | 0 | 1 | 65 | 2 |
| `datasets/curated/gren_dataset.jsonl` | 0 | 0 | 0 | 0 | 0 |
| `datasets/curated/peregrine_general_32180.jsonl` | 0 | 0 | 0 | 0 | 0 |
| `datasets/curated/peregrine_ml_ai_pretrain_text.jsonl` | 0 | 0 | 0 | 0 | 0 |
| `datasets/general/fineweb.jsonl` | 0 | 0 | 2 | 130 | 22 |
| `src/dataset_generator/code.jsonl` | 0 | 0 | 0 | 0 | 0 |
| `src/dataset_generator/general.jsonl` | 0 | 0 | 0 | 0 | 0 |

Examples of sensitive-pattern references:

- `datasets/code/java.jsonl` — known_token_pattern, lines 2951: **[REDACTED]**.
- `datasets/code/java.jsonl` — credential_assignment, lines 579, 815, 856, 1155, 2218, 2519, 2536, 2882, 3067, 3280: **[REDACTED]**.
- `datasets/code/javascript.jsonl` — known_token_pattern, lines 351, 450, 1252, 1971, 2024: **[REDACTED]**.
- `datasets/code/javascript.jsonl` — credential_assignment, lines 51, 204, 370, 447, 450, 508, 875, 955, 1150, 1760, 1851, 2058: **[REDACTED]**.
- `datasets/code/python.jsonl` — private_key_block, lines 630: **[REDACTED]**.
- `datasets/code/python.jsonl` — known_token_pattern, lines 1675, 1952: **[REDACTED]**.
- `datasets/code/python.jsonl` — credential_assignment, lines 157, 210, 271, 292, 326, 414, 675, 828, 856, 1041, 1086, 1262: **[REDACTED]**.
- `datasets/code/rust.jsonl` — credential_assignment, lines 547: **[REDACTED]**.
- `datasets/general/fineweb.jsonl` — credential_assignment, lines 7982, 10885: **[REDACTED]**.

The code files contain only `text` and `language`: no repository IDs, paths, revisions, SPDX licenses, acquisition revision or opt-out trail. FineWeb contains only `text`; curated collections contain only text or QA. Recover provenance in a sidecar manifest. At `datasets/code/javascript.jsonl:81` the header explicitly says **Elastic License**; this warrants rights review rather than assuming an upstream permissive filter is infallible. GPL-family headers and other notices are counted below. Header matches do not establish the effective license or a legal prohibition on training. The root Apache license does not settle these questions.

| Dataset | Header/license hints by family (overlap possible) |
|---|---|
| `datasets/code/cpp.jsonl` | `{"MIT": 110, "any_license_hint_records": 472, "Apache": 222, "BSD": 95, "GPL_or_LGPL_or_AGPL": 39, "Unlicense_or_CC0": 8, "Elastic": 1}` |
| `datasets/code/java.jsonl` | `{"Apache": 970, "any_license_hint_records": 1133, "MIT": 83, "GPL_or_LGPL_or_AGPL": 44, "BSD": 37, "Elastic": 2, "Unlicense_or_CC0": 2}` |
| `datasets/code/javascript.jsonl` | `{"Apache": 66, "any_license_hint_records": 173, "BSD": 22, "MIT": 63, "Elastic": 1, "GPL_or_LGPL_or_AGPL": 8, "Unlicense_or_CC0": 15, "MPL": 1}` |
| `datasets/code/python.jsonl` | `{"MIT": 89, "any_license_hint_records": 394, "BSD": 25, "Apache": 256, "GPL_or_LGPL_or_AGPL": 19, "Unlicense_or_CC0": 8}` |
| `datasets/code/rust.jsonl` | `{"Apache": 219, "MIT": 108, "any_license_hint_records": 293, "BSD": 7, "Unlicense_or_CC0": 8, "GPL_or_LGPL_or_AGPL": 9, "MPL": 1}` |

**Context qualification:** Python line 630 contains two apparently deliberate RSA unit-test fixtures, not a demonstrated live deployment key. Python line 1952 explicitly labels its AWS-shaped string as an example. Python line 1675 assigns a Google-key-shaped identifier to `_CELLSET_ID`, so it may be a noncredential identifier. Java line 2951 uses a hardcoded Google geocoding key variable; the five JavaScript token-pattern records use Google/Firebase service URLs or configuration. Their validity and access restrictions are unknown. Do not conflate these categories or automatically delete useful cryptographic test source. No live credential exposure was confirmed.

## High — corpus scale and stage control

All JSONL training fields together yield only 32.86–54.76M **rough** tokens before eligibility decisions. Only one natural-language web file is present. The 32,180-record general QA collection is not a broad general pretraining corpus. No independent evaluation split or nonempty budget/mixture configuration exists. This is a material limitation for the intended high-quality from-scratch model, while permitting deliberately small pilots.

A recursive `text`-only loader would ignore QA; a loader concatenating arbitrary fields could train on questions/answers without an intentional SFT policy. Directory naming alone does not enforce the general→code curriculum. No active loader exists here to demonstrate an accidental mix, so accidental mixing is a **risk**, not a confirmed training event.

## High — configured tokenizer input is unrepresentative; C++ extraction changes structure

The trainer reads only the 654,873-byte starter, not the full audited text/code pools. The starter opens with repeated variants of the same astronomy paragraph, followed by similarly regular study-note and code patterns. Examples of recurring source lines occur 54 times; repeated braces alone are expected. This biases frequency learning toward a small designed sample. No trained model exists to establish actual damage or vocabulary efficiency.

Whole-file hashes confirm `extracted_texts.txt` is exactly the C++ text concatenation after `LF → CRLF` expansion. It is not byte-identical to the decoded source. The 38,585 original CRLF sequences become CRCRLF. There are 214 C++ records without a terminal newline; the helper inserts no record separator. These defects affect the derivative tokenizer input, not the intact code JSONL. `tokenizer_dataset.py` opens a normal Windows text stream and writes `text_content` directly.

## Medium — binary-like asset payload in a JavaScript bundle

`datasets/code/javascript.jsonl:1525` contains 47,304 decoded characters, including 12,227 U+FFFD characters and 9,820 unusual controls. It has a JavaScript bundle wrapper and a source-map reference around a binary-like payload, so a source-language cue alone does not establish useful source content. The payload appears lossy or binary-like; no claim is made that the wrapper fails JavaScript parsing. Retain the immutable original but review/exclude this record from a future source-code/tokenizer manifest unless that asset representation is wanted. It affects approximately 0.24% of JavaScript character mass.

Contrast legitimate controls: JavaScript line 1609 maps DEL/ESC key codes; Rust line 234 intentionally tests malformed input, line 1292 documents U+FFFD encoding, and line 2016 explains replacement-character semantics. These are acceptable code/test cases and should not be discarded merely for sharing a Unicode flag. C++ line 1274 and several Java/FineWeb examples show likely lost text in comments or prose, a smaller and more localized problem.

## Medium — narrow synthetic distributions and future split leakage

| QA file | Records | Distinct normalized question templates | Distinct answers | Repeated answer occurrences |
|---|---:|---:|---:|---:|
| `datasets/curated/gren_dataset.jsonl` | 2138 | 401 | 1480 | 658 |
| `datasets/curated/peregrine_general_32180.jsonl` | 32180 | 7798 | 20522 | 11658 |
| `src/dataset_generator/general.jsonl` | 2 | 2 | 2 | 0 |

Template collapse deliberately hides numbers and quoted/code spans; it diagnoses repeated structure, not semantic equivalence. For example, general line 18448 asks `438 + 700` and correctly answers `1138`; a different pair of operands remains a useful different task. Gren line 457 uses a repeated API-description phrasing. Repeated short correct answers such as numbers, booleans and weekdays are normal. The harm comes from overweighting these families and leaking nearly identical task generators into evaluation, not from shortness alone.

## Medium — selected web factual, formatting and extraction defects

- `datasets/general/fineweb.jsonl:9111`: claims Cyrus and Darius invaded northwest India together in **520 BC**. The British Museum dates Cyrus’s reign to **559–530 BC**, contradicting that joint date. This is one confirmed contradiction, not a measured factual-error rate. [Museum description](https://artsandculture.google.com/asset/cyrus-cylinder/4wHjbQnYhZgzVQ?hl=en).
- `fineweb.jsonl:2977`: starts `Sign In / Sign Out` and `Navigation for Entire University` before useful sediment/rock material. The navigation is removable boilerplate in a future derived view; the geology content is not thereby worthless.
- `fineweb.jsonl:3557`: lesson-plan catalogue with access prompts, view/download counts and unrelated suggested lessons; `:7119` advertises a printable teaching product. Educational-topic scoring does not guarantee substantive document quality.
- `fineweb.jsonl:692`: `os.pipe()` tutorial has Python 2 code flattened into prose (`os.close(w) r = os.fdopen(r) print ...`). This teaches poor code formatting if admitted as a coding example; an English educational page may still retain some value.
- `fineweb.jsonl:3010`: mathematical powers appear as flattened `x5`, `x-3` and `x8`, creating ambiguity with identifiers or subtraction. Some text formats use this convention, so review rather than deleting every such page.
- `fineweb.jsonl:8088`: instructions require listening to omitted audio examples; `:862` asks the reader to inspect an unavailable image; `:11978` begins mid-sentence. These are incomplete or modality-dependent examples, not invalid JSON.
- `fineweb.jsonl:81`: explains CT absorption solely using atomic “size”; flag for technical review as an oversimplification. This audit did not independently certify all medical claims and is not using that example to estimate prevalence.

Representative positive controls: general lines 739, 2382, 3125, 3480, 3776, 5147 and 19977 are consistent with their arithmetic/date/format tasks in manual review. Narrow mechanical tests found no mismatches in their recognized subset. ML/AI line 96 explicitly notes that top-k ties can retain more than k elements; line 66 acknowledges that its optimizer example is not an AMP/distributed recipe. Gren String.count, String.replace, String.split and Dict operations were checked selectively against official core 7.0.0 docs. No claim is made that every technical explanation or citation was verified. [String](https://packages.gren-lang.org/package/gren-lang/core/version/7.0.0/module/String), [Dict](https://packages.gren-lang.org/package/gren-lang/core/version/7.0.0/module/Dict).

## Medium — generated, bundled, obfuscated and historical code

| Dataset | Generated cues | Vendor/bundle cues | Lock/build cues | >80% comment-like lines | Minified/large-line candidates | Missing expected source cue |
|---|---:|---:|---:|---:|---:|---:|
| `datasets/code/cpp.jsonl` | 48 | 1 | 0 | 20 | 2 | 17 |
| `datasets/code/java.jsonl` | 218 | 2 | 0 | 65 | 4 | 35 |
| `datasets/code/javascript.jsonl` | 131 | 91 | 0 | 15 | 135 | 92 |
| `datasets/code/python.jsonl` | 120 | 1 | 0 | 6 | 5 | 97 |
| `datasets/code/rust.jsonl` | 137 | 1 | 0 | 24 | 1 | 68 |

- `datasets/code/javascript.jsonl:2218`: 24,971-character krpano plugin record dominated by an encoded/obfuscated string. Low source-learning value and an unresolved source/license context make it a strong review candidate.
- `datasets/code/rust.jsonl:2002`: uses `extern mod`, `~str` and `ret`, clearly historical Rust syntax. Such source is real code; contemporary compiler failure would not imply storage corruption. Downweight only if the target is modern Rust.
- `datasets/code/python.jsonl:457`: includes `Tkinter`, `tkFileDialog` and a `raw_input` comment; other records contain Python 2 syntax. Keep language-version context when interpreting AST rejection.
- `datasets/code/java.jsonl:278`: a 133-character empty entity class is a legitimate short source file. `python.jsonl:685` contains small exception definitions. Neither should be removed by a blanket length rule.
- `datasets/code/rust.jsonl:81`: standard-library iterator implementation with substantial documentation. Repeated libraries and generated register interfaces can dominate a small coding corpus, but source context and comments can be useful.

In the full JavaScript scan, 135 minified/large-line candidate records account for **4,132,861 decoded characters (20.78%)**. Vendor/bundle cues cover 16.25% and generated cues 17.01% of JavaScript characters; these sets overlap. Generated cues cover 20.96% of Rust characters. This is a meaningful distribution concern in a small code corpus, not proof that all flagged source is useless. Full per-file candidate character masses are in the JSON and summary.

Content heuristics can flag strings that merely mention generation, vendor paths or confidential material. Lock/build counts are lower bounds because source paths were discarded; no complete vendored-dependency or artifact classification is possible. Code comment ratios are approximate line-prefix counts and include preprocessor directives in C++, so they do not justify automatic comment removal.

## Medium/low — exact/near duplicates, controls and benchmark uncertainty

Complete exact redundant records: 11; whitespace-normalized redundant records: 11. Sampled near matches and cross-file examples are in the summary/JSON. Common license blocks and declarations are explicitly separated from document duplication. Preserve required notices even when balancing duplicate source families.

| Dataset | Web boilerplate cues | Promotion cues | Repetitive lines (>50%) | Low word diversity | Explicit truncation markers | Benchmark references |
|---|---:|---:|---:|---:|---:|---:|
| `datasets/code/cpp.jsonl` | 315 | 0 | 76 | 8 | 0 | 0 |
| `datasets/code/java.jsonl` | 245 | 0 | 120 | 10 | 1 | 0 |
| `datasets/code/javascript.jsonl` | 86 | 1 | 110 | 5 | 0 | 0 |
| `datasets/code/python.jsonl` | 146 | 0 | 53 | 6 | 1 | 9 |
| `datasets/code/rust.jsonl` | 62 | 0 | 167 | 22 | 0 | 2 |
| `datasets/curated/gren_dataset.jsonl` | 0 | 0 | 0 | 0 | 0 | 0 |
| `datasets/curated/peregrine_general_32180.jsonl` | 0 | 0 | 0 | 0 | 0 | 0 |
| `datasets/curated/peregrine_ml_ai_pretrain_text.jsonl` | 0 | 0 | 0 | 0 | 0 | 0 |
| `datasets/general/fineweb.jsonl` | 184 | 8 | 0 | 0 | 0 | 0 |
| `src/dataset_generator/code.jsonl` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/dataset_generator/general.jsonl` | 0 | 0 | 0 | 0 | 0 | 0 |

A privacy/copyright banner in code is not scraped navigation; a benchmark name in a technical explanation is not proof of a leaked benchmark item. Keyword absence cannot establish cleanliness. No local evaluation set or external test corpora were available for actual train/eval matching.

The JSON records unusual controls, replacement characters, surrogates and mojibake candidates with references. Interpret them in source context: escape-related tests and terminal output are valid code. A final missing newline, external imports, a snippet or unbalanced braces in a string do not prove truncation. No blanket sanitization or source deletion was performed.

## Low — empty/prototype files

`src/dataset_generator/code.jsonl` is empty: **NOT SUITABLE** as training data. `src/dataset_generator/general.jsonl` has two plausible QA examples, useful only as a prototype pending origin/rights and SFT validation. Neither meaningfully expands the pretraining pool.
