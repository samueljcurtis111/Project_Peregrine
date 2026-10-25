import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input=r"C:\Users\stuar\OneDrive\Documents\Project_Peregrine\src\tokenizer\peregrine_tokenizer_starter.txt",
    model_prefix="peregrine",
    vocab_size=32000,
    model_type="bpe",
    character_coverage=0.9995,
    byte_fallback=True,
    normalization_rule_name="identity",
    remove_extra_whitespaces=False,
    hard_vocab_limit=False,
    unk_id=0,
    bos_id=1,
    eos_id=2,
    pad_id=3
)