# Prioritized recommendations

These are proposed next steps. The audit performed none of the preprocessing, exclusion, acquisition, training, or retraining actions below. Preserve source files and implement later decisions as versioned manifests/derived artifacts.

## 1. Resolve sensitive candidates and provenance before a production run

Review private-key blocks, recognized-token patterns and nontrivial credential assignments at the redacted references in `quality_metrics.json`. Classify test fixtures/placeholders versus material that needs removal from the eligible training view. Keep any sensitive review local; do not validate credentials against remote services. A regex hit alone does not justify rotating an owner’s key or rejecting a whole dataset.

Recover source dataset revision, repository/path/commit or source URL, license evidence, attribution requirements, acquisition date and removal/opt-out status into a separate sidecar keyed by document hash. Review the Elastic-license and GPL-family header candidates. Record the curated datasets’ authorship, generating model/version, generation settings, validation and applicable terms. The repository license does not settle acquired-data permissions. This is the first production eligibility gate.

## 2. Define frozen general, code, SFT and evaluation manifests

Use FineWeb as the primary general pool and the five language-labeled source datasets as the coding pool after eligibility review. Keep the 32,180 general QA pairs, Gren QA and generator examples in a separate SFT pool. Admit the ML/AI text as a small explicitly weighted supplement if reviewed; it contains QA headings and code. Specify schema adapters and whether input/prompt loss is masked for SFT. Do not infer stage membership from a recursive glob alone.

Pin independent evaluation sources and keep them out of both tokenizer training and model-training pools where practical. Split by repository/source/document and synthetic task family, not just rows. Compare exact/normalized hashes, long matching substrings and near duplicates to actual benchmark versions. Preserve all identified overlap as an auditable manifest decision rather than editing originals.

## 3. Repair the proposed tokenizer input pipeline before training a model

Design a representative sample weighted by decoded character/token mass and intended training mixture, not record count. Cap repeated source/template families without removing normal code syntax. Include natural long-form English, science/technical text, mathematics/LaTeX, all five existing code languages and any additional languages Peregrine is expected to support.

Replace the C++-only derivative-input approach in a future implementation: preserve LF, CRLF, tabs, blank lines and trailing whitespace explicitly, prevent document-boundary fusion, and avoid Windows text newline expansion. The configured starter is too small and templated to establish a production vocabulary distribution. Decide how a line-based SentencePiece input represents newlines/documents and handle lines exceeding the trainer’s configured maximum length.

Before freezing a 32K tokenizer, run byte-for-byte encode→decode probes and held-out corpus tests for each language and topic. Measure tokens/UTF-8 byte, bytes/token, unknown and byte-fallback rates, identifier fragmentation, indentation cost, math/Unicode cost, achieved vocabulary size and vocabulary stability across samples. Include spaces/tabs/LF/CRLF, empty/blank lines, emoji, combining marks and literal U+2581. Set acceptance criteria by intended use and compare against a reference tokenizer. No trained Peregrine model exists here to evaluate yet.

## 4. Improve distribution and selected content, with conservative review

Review FineWeb navigation/catalogues and pages with missing code/math/audio/image context. The named factual contradiction warrants source-level review; a few such pages do not justify discarding all educational text. Prefer better extraction or source-aware eligibility rules for future acquisitions. Do not globally strip Unicode, math symbols, comments, headers, short records, tests or incomplete but useful snippets.

Prioritize the corrupted/binary-like `datasets/code/javascript.jsonl:1525` for exclusion from a future derived training manifest. Preserve legitimate control-character fixtures, including JavaScript key-code tables and Rust Unicode decoder tests. Treat the separate obfuscated plugin at line 2218 as its own review decision.

Limit obfuscated JS, repetitive generated bindings and duplicated library families when they consume a disproportionate training share. Keep examples needed for the intended tasks. Identify source/revision and language era rather than labeling Python 2 or historical Rust as corrupt. Python AST failures need classification, not automatic rejection; validate executable SFT code in isolated pinned environments only as a separately authorized future task.

General QA is useful for short task execution but narrow as knowledge pretraining. Add validated diverse multi-turn SFT and non-template instruction tasks if conversational behavior is a goal. Pin Gren/compiler/package versions and compile representative examples later; String/Dict spot checks cannot validate every module. Maintain factual review by topic and risk, with explicit pass/fail evidence rather than trusting synthetic fluency.

## 5. Expand unique text to a stated experimental budget

Current corpus: 32.86–54.76M rough tokens before exclusions, with no model-token counts. Write the model parameter count, unique-token target, total tokens/epochs, general/code ratio and stage boundaries into the presently empty strategy/budget/methodology documents before deciding this is sufficient. Keep small loader/tokenizer pilots separate from claims about a capable 14B foundation model.

Collect broader independently sourced natural writing and technical/math material with retained metadata. Add code languages according to intended capability rather than treating five balanced byte quotas as universal language coverage. The collector takes the first accepted streaming records, so use a reproducible upstream shuffle/stratified acquisition strategy in a future dataset version; this audit did not verify that the existing prefix is representative of its upstream source.

For sequential-vs-mixed experiments, keep the **same frozen eligible document pool, tokenizer, actual total token budget, evaluation tasks and seed policy** across schedules. Log stage-specific language/token distributions and repeated exposure counts. Use multiple seeds and held-out loss/behavior; otherwise data selection or repeated-template exposure can masquerade as a curriculum effect.

## Audit operation

Rerun `audit.py` after new acquisitions. Every run must discover files again, hash sources, report full versus sampled coverage, preserve source bytes and report privacy candidates only with redaction. Review new datasets rather than treating this snapshot’s qualitative conclusions as permanent certification. The optional SQLite index contains hashes/signatures/offsets only and is temporary unless `--keep-index` is used. Reports and their line references should be versioned with the acquisition manifest.
