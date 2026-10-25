#!/usr/bin/env python3
"""Read-only Project Peregrine JSONL audit. Standard library; Python >=3.10.

All writes are confined to --out (default reports/dataset_audit). Source files
are opened rb only. No dataset processing/cleaning or model training occurs.
Use --peek for a small redacted initial inspection; default runs the full audit.
"""
from __future__ import annotations
import argparse
import ast
import collections
import csv
import datetime as dt
import hashlib
import heapq
import itertools
import json
import math
import os
from pathlib import Path
import random
import re
import sqlite3
import statistics
import sys
import time
import tokenize
import io
import unicodedata
import struct
import zlib
import warnings

warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import numpy as np
except ImportError:
    np = None

SEED = 20261023
# Qualitative conclusions below apply only to this immutable reviewed snapshot.
REVIEWED_SHA256 = {
 'datasets/code/cpp.jsonl':'cb6e6805e0e7c17b401326029c7134dd1ffdc22c7b44989c53ecb23cceafbec6',
 'datasets/code/java.jsonl':'ebebddcb4fb35948199248e667636827f2473e703ba183d4427a933468435518',
 'datasets/code/javascript.jsonl':'0d2693df2cd9e1de8ab6456a94685374a99e73cad4245f7d9eaab3ad21e42b05',
 'datasets/code/python.jsonl':'cdadddb3e8f82a5eef1372fdc0010f99ffce73f8307333632d4f96c7014dcbae',
 'datasets/code/rust.jsonl':'c61234b028db0ac5ad520855c175d0473cc73d0499a72396fea4aa54f394dd5e',
 'datasets/curated/gren_dataset.jsonl':'3b68a01f7bf015f983ec3adb78fcf1859f2b9af6394ac1796c834b51e3b54690',
 'datasets/curated/peregrine_general_32180.jsonl':'c5ec3b6225cb76ff4da98a4dce7d219e86fb848ca68bde62fc14ad5394a9803d',
 'datasets/curated/peregrine_ml_ai_pretrain_text.jsonl':'a9f827b71e25bbea5e6b7b70d9f20608fce4f7208e1762a0d912dffe43cfd886',
 'datasets/general/fineweb.jsonl':'8afa91a92a611dc54c3a063c2c29f1228e3115709ab79261b026915ff86204ad',
 'src/dataset_generator/code.jsonl':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
 'src/dataset_generator/general.jsonl':'a658e5494d6b51397862d4d3dc7e8f8888c5648bdba148fed5840841fd20fb4f',
}
EMAIL = re.compile(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}@[A-Z0-9.-]{1,253}\.[A-Z]{2,24}", re.I)
URL = re.compile(r"https?://[^\s<>\"')]+", re.I)
KEY = re.compile(r"(?is)-----BEGIN (?:[A-Z0-9 ]*PRIVATE KEY|OPENSSH PRIVATE KEY)-----.*?(?:-----END [A-Z0-9 ]*PRIVATE KEY-----|$)")
TOKEN = re.compile(r"\b(?:AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b")
ASSIGN = re.compile(r"(?i)(\b(?:password|passwd|pwd|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|secret[_-]?key)\b\s*[:=]\s*)([\"'])([^\r\n\"']{4,})\2")
PHONE = re.compile(r"(?<!\w)(?:\+\d[\d ()-]{8,}\d|\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4})(?!\w)")
IP = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
ADDRESS = re.compile(r"(?i)\b\d{1,6}\s+(?:[A-Za-z]+\s+){1,5}(?:street|st\.|road|rd\.|avenue|ave\.|boulevard|blvd\.|lane|drive)\b[^\r\n]{0,40}")
SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")

def redact(s):
    s = KEY.sub('[REDACTED PRIVATE KEY BLOCK]', str(s))
    s = TOKEN.sub('[REDACTED TOKEN]', s)
    s = ASSIGN.sub(lambda m: m[1] + m[2] + '[REDACTED VALUE]' + m[2], s)
    s = EMAIL.sub('[REDACTED EMAIL]', s)
    s = URL.sub('[REDACTED URL]', s)
    s = SSN.sub('[REDACTED IDENTIFIER]', s)
    s = PHONE.sub('[REDACTED PHONE-LIKE]', s)
    s = IP.sub('[REDACTED IP-LIKE]', s)
    s = ADDRESS.sub('[REDACTED ADDRESS-LIKE]', s)
    s = re.sub(r'(?im)^([^\n]*(?:@author|written by|copyright\s+(?:\(c\)\s*)?\d{4})[^\n]*)$', '[REDACTED ATTRIBUTION LINE]', s)
    s = re.sub(r'(?im)^.*\bauthors?(?:_email)?\s*[:=].*$', '[REDACTED AUTHOR LINE]', s)
    s = re.sub(r'(?i)(?:[A-Z]:\\Users\\|/home/|/Users/)[^/\\\s]+', '[REDACTED USER PATH]', s)
    return s.encode('utf-8', 'backslashreplace').decode('utf-8')

def excerpt(s, limit=360):
    # Bound work before running redactors. Also redact incomplete assignments.
    s = str(s)[:max(4096, limit * 2)]
    s = re.sub(r"(?i)(\b(?:password|passwd|pwd|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|secret[_-]?key)\b\s*[:=]\s*)[\"'][^\r\n]*", r'\1[REDACTED VALUE]', s)
    return redact(s)[:limit].replace('\x00', '\\x00')

def walk_jsonl(root, out):
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != '.git' and not (Path(current) / d).is_symlink()
                         and (Path(current) / d).resolve() != out.resolve())
        for f in sorted(files):
            p = Path(current) / f
            if p.suffix.lower() == '.jsonl' and not p.is_symlink():
                yield p

def parts_of(obj):
    """Explicit schema adapters; metadata is never silently used as training text."""
    if isinstance(obj, str):
        return [('text', obj)], 'json_string'
    if not isinstance(obj, dict):
        return [], 'unsupported'
    if isinstance(obj.get('messages'), list) or isinstance(obj.get('conversations'), list):
        key = 'messages' if isinstance(obj.get('messages'), list) else 'conversations'
        parts = []
        for m in obj[key]:
            if isinstance(m, dict):
                content = m.get('content', m.get('value'))
                if isinstance(content, str):
                    parts.append((str(m.get('role', m.get('from', 'unknown'))), content))
        return parts, 'chat'
    for q, a in [('question','answer'), ('instruction','output'), ('prompt','completion'), ('prompt','response')]:
        if q in obj or a in obj:
            keys = [q] + (['input'] if q == 'instruction' and 'input' in obj else []) + [a]
            return [(k, obj[k]) for k in keys if isinstance(obj.get(k), str)], 'instruction_pair'
    for k in ['text', 'content', 'code', 'document', 'body']:
        if isinstance(obj.get(k), str):
            return [(k, obj[k])], k
    return [], 'unsupported'

def peek(root, out):
    for p in walk_jsonl(root, out):
        rng = random.Random(SEED)
        samples = []
        n = invalid = 0
        with p.open('rb') as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line.decode('utf-8'))
                except (UnicodeError, ValueError):
                    invalid += 1
                    continue
                n += 1
                parts, kind = parts_of(obj)
                j = len(samples) if len(samples) < 4 else rng.randrange(n)
                if j < 4:
                    item = {'line': line_no, 'keys': list(obj) if isinstance(obj, dict) else type(obj).__name__,
                            'kind': kind, 'chars': sum(len(t) for _,t in parts),
                            'excerpt': excerpt('\n'.join(t for _,t in parts), 650)}
                    if len(samples) < 4:
                        samples.append(item)
                    else:
                        samples[j] = item
        print(json.dumps({'file': p.relative_to(root).as_posix(), 'bytes':p.stat().st_size,
                          'valid_records':n, 'invalid':invalid, 'samples':samples}, ensure_ascii=True), flush=True)

LEX = re.compile(r'\w+|[^\w\s]', re.UNICODE)
CONTROL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')
SURROGATE = re.compile(r'[\ud800-\udfff]')
BIDI = re.compile('[\u202a-\u202e\u2066-\u2069]')
REPEAT = re.compile(r'([^\s])\1{39,}')
PATTERNS = {
    'web_boilerplate': re.compile(r'(?i)\b(?:accept all cookies|cookie policy|privacy policy|all rights reserved|subscribe to our newsletter|skip to (?:main )?content|sign up for our newsletter|enable javascript|terms of (?:use|service))\b'),
    'promotion': re.compile(r'(?i)\b(?:buy now|limited time offer|free shipping|best price|click here to (?:buy|order)|promo code|casino bonus|payday loans)\b'),
    'explicit_truncation_marker': re.compile(r'(?i)(?:\[.{0,5}truncated.{0,30}\]|\bcontent (?:has been )?truncated\b|\bfile (?:has been )?truncated\b)'),
    'assistant_filler': re.compile(r'(?i)\b(?:as an ai (?:language )?model|in today.s (?:rapidly |ever.evolving )?(?:world|digital)|let.s delve|tapestry of|i hope this (?:helps|answers))\b'),
    'generated_code': re.compile(r'(?i)(?:auto.?generated|automatically generated|generated (?:by|from)|do not edit|DO NOT MODIFY|@generated|svd2rust|protobuf|sourceMappingURL=)'),
    'vendor_or_bundle': re.compile(r'(?i)(?:node_modules[/\\]|bower_components[/\\]|webpackBootstrap|webpackJsonp|__webpack_require__|jquery v\d|jquery javascript library|lodash (?:v|<|\d)|third.party (?:library|libraries)|vendor[/\\])'),
    'lock_or_build': re.compile(r'(?i)(?:"lockfileVersion"\s*:|"integrity"\s*:\s*"sha512|"resolved"\s*:\s*"https?://registry|^# This file is automatically @generated by Cargo)'),
    'benchmark_reference': re.compile(r'(?i)\b(?:HumanEval|MBPP|MMLU|GSM8K|MATH benchmark|HellaSwag|ARC.challenge|WinoGrande|Big.Bench|SWE.bench)\b|\b(?:test|train|validation)_(?:split|set)\b'),
    'confidentiality_marker': re.compile(r'(?i)\b(?:confidential|internal use only|trade secret|not for (?:public |external )?distribution|proprietary and confidential)\b'),
}
LICENSE_PATTERNS = {
    'Apache': r'Apache (?:License|Software License)|SPDX-License-Identifier:\s*Apache',
    'MIT': r'MIT License|Permission is hereby granted, free of charge',
    'BSD': r'BSD (?:License|license)|Redistribution and use in source and binary forms',
    'GPL_or_LGPL_or_AGPL': r'GNU (?:A?ffero )?(?:Lesser )?General Public License|SPDX-License-Identifier:\s*(?:A?GPL|LGPL)',
    'MPL': r'Mozilla Public License|SPDX-License-Identifier:\s*MPL',
    'Elastic': r'Elastic License',
    'Unlicense_or_CC0': r'Unlicense|Creative Commons Zero|CC0',
}
LICENSE_PATTERNS = {k:re.compile(v, re.I) for k,v in LICENSE_PATTERNS.items()}
CODE_CUES = {
    'python': re.compile(r'(?m)^\s*(?:async def |def \w+\(|from [\w.]+ import |import \w|class \w|if __name__\s*==)'),
    'cpp': re.compile(r'#\s*include\s*[<"]|\b(?:std::|template\s*<|namespace\s+\w+|public:|nullptr)'),
    'rust': re.compile(r'\b(?:pub\s+(?:fn|struct|mod|enum)|fn\s+\w+\s*[<(]|impl\s|use\s+(?:crate|std|super)::|let\s+mut\s)'),
    'java': re.compile(r'(?m)^\s*(?:package [\w.]+;|import (?:static )?[\w.*]+;|public (?:class|interface|enum)|@Override)'),
    'javascript': re.compile(r'\b(?:function\s*\w*\s*\(|(?:const|let|var)\s+\w+\s*=|module\.exports|export (?:default|function|const)|require\s*\()|=>'),
}

def digest(s):
    return hashlib.sha256(s.encode('utf-8','surrogatepass')).digest()

def normalized(s):
    return ' '.join(s.split())

def canonical(parts):
    if len(parts) == 1:
        return parts[0][1]
    return json.dumps(parts, ensure_ascii=True, separators=(',',':'))

def strict_pairs(pairs):
    obj = {}
    for k,v in pairs:
        if k in obj:
            raise ValueError('duplicate_json_key')
        obj[k] = v
    return obj

def refuse_constant(_):
    raise ValueError('nonfinite_json_number')

def load_strict(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=strict_pairs, parse_constant=refuse_constant)

def nested_fields(obj, prefix='', depth=0):
    if depth > 8:
        return
    if isinstance(obj, dict):
        for key,value in obj.items():
            p = prefix + '/' + key.replace('~','~0').replace('/','~1')
            yield p, value
            yield from nested_fields(value,p,depth+1)
    elif isinstance(obj, list):
        for value in obj:
            p = prefix + '/*'
            yield p,value
            yield from nested_fields(value,p,depth+1)

def template_of(s):
    # Diagnostic only: deliberately collapses literals to expose synthetic templates.
    s = s.lower()
    s = re.sub(r'`[^`\n]{0,300}`', '`<code>`', s)
    s = re.sub(r'"[^"\n]{0,100}"|\x27[^\x27\n]{0,100}\x27', '<quoted>', s)
    s = re.sub(r'(?<![a-z])[-+]?\d+(?:\.\d+)?', '<n>', s)
    return normalized(s)

def shingles(s):
    tokens = LEX.findall(s)
    if len(tokens) < 5:
        return {digest(s)[:8]}
    return {hashlib.blake2b('\x1f'.join(tokens[i:i+5]).encode('utf-8','surrogatepass'),digest_size=8).digest()
            for i in range(len(tokens)-4)}

def signature(s):
    features = shingles(s)
    # Deterministic bottom-hash feature cap bounds work for unusually large files.
    if len(features) > 8192:
        features = heapq.nsmallest(8192, features)
    vals = [int.from_bytes(x,'little') for x in features]
    if np is not None:
        a = np.asarray(vals, dtype=np.uint64)
        salts = np.array([int.from_bytes(hashlib.sha256(f'{SEED}:{i}'.encode()).digest()[:8],'little') for i in range(64)],dtype=np.uint64)
        mult = np.uint64(0x9E3779B185EBCA87)
        with np.errstate(over='ignore'):
            sig = ((a[:,None] ^ salts[None,:]) * mult).min(axis=0)
        return sig.astype('<u8').tobytes()
    salts = [int.from_bytes(hashlib.sha256(f'{SEED}:{i}'.encode()).digest()[:8],'little') for i in range(64)]
    return struct.pack('<64Q',*(min(((v^salt)*0x9E3779B185EBCA87)&((1<<64)-1) for v in vals) for salt in salts))

def reservoir_add(items, item, n, capacity, rng):
    if len(items) < capacity:
        items.append(item)
    else:
        j = rng.randrange(n)
        if j < capacity:
            items[j] = item

def new_stats(path, root):
    return {'path':path.relative_to(root).as_posix(), 'bytes':path.stat().st_size,
            'mtime_ns_before':path.stat().st_mtime_ns,'sha256_before':'',
            'physical_lines':0,'blank_lines':0,'parsed_records':0,'invalid_records':0,
            'object_records':0,'text_records':0,'text_chars':0,'text_utf8_bytes':0,'whitespace_words':0,
            'schema':collections.Counter(),'formats':collections.Counter(),'field_types':{},
            'field_present':collections.Counter(),'null_fields':collections.Counter(),'empty_fields':collections.Counter(),
            'nested_field_types':{}, 'nested_nulls':collections.Counter(),
            'length_bins':collections.Counter(),'signals':collections.Counter(),
            'signal_examples':{},'languages_declared':collections.Counter(),'code_cues':collections.Counter(),
            'unicode':collections.Counter(),'unicode_characters':collections.Counter(),
            'script_characters':collections.Counter(),'license_hints':collections.Counter(),
            'privacy':collections.Counter(),'privacy_occurrences':collections.Counter(),'privacy_refs':{},
            'code_lines':collections.Counter(),'python3_ast':collections.Counter(),
            'python3_ast_examples':{}, 'sample_refs':[], 'content_review_refs':[],
            'estimated_tokens':{}, 'errors':[]}

def flag(st, name, line, text, n=1):
    st['signals'][name] += n
    refs = st['signal_examples'].setdefault(name,[])
    if len(refs) < 5:
        refs.append({'line':line,'excerpt':excerpt(text,280)})

def scan_content(st, text, obj, kind, line):
    size = len(text)
    words = text.split()
    st['text_records'] += 1
    st['text_chars'] += size
    st['text_utf8_bytes'] += len(text.encode('utf-8','surrogatepass'))
    st['whitespace_words'] += len(words)
    bin_name = next((name for lim,name in [(0,'empty'),(19,'1-19'),(79,'20-79'),(199,'80-199'),(999,'200-999'),(9999,'1000-9999'),(99999,'10000-99999'),(499999,'100000-499999')] if size <= lim), '500000+')
    st['length_bins'][bin_name] += 1
    if not text.strip(): flag(st,'empty_text',line,text)
    if size < 20: flag(st,'under_20_chars',line,text)
    if size < 80: flag(st,'under_80_chars',line,text)
    if size > 100000: flag(st,'over_100000_chars',line,text)
    if size > 500000: flag(st,'over_500000_chars',line,text)
    if len(set(text)) < 10 and size >= 80: flag(st,'low_character_diversity',line,text)
    for name,pat in PATTERNS.items():
        match = pat.search(text)
        if match:
            flag(st,name,line,text[max(0,match.start()-60):match.end()+220])
    counts = collections.Counter(text)
    nonascii = sum(v for k,v in counts.items() if ord(k)>127)
    st['unicode']['nonascii_chars'] += nonascii
    if nonascii: st['unicode']['records_with_nonascii'] += 1
    for ch,count in counts.items():
        if ord(ch)>127:
            st['unicode_characters'][f'U+{ord(ch):04X} {unicodedata.name(ch,"UNNAMED")}'] += count
        code = ord(ch)
        script = ('ascii' if code<128 else 'cjk' if 0x3400<=code<=0x9fff else 'cyrillic' if 0x400<=code<=0x52f else 'greek' if 0x370<=code<=0x3ff else 'arabic' if 0x600<=code<=0x6ff else 'math_symbol' if unicodedata.category(ch)=='Sm' else 'other_nonascii')
        st['script_characters'][script] += count
    for name,pat in [('unusual_control',CONTROL),('escaped_surrogate',SURROGATE),('bidi_control',BIDI)]:
        matches = list(pat.finditer(text))
        if matches:
            st['unicode'][name+'_records'] += 1
            st['unicode'][name+'_occurrences'] += len(matches)
            m = matches[0]
            flag(st,name,line,text[max(0,m.start()-50):m.end()+120])
    if '\ufffd' in text:
        st['unicode']['replacement_character_records'] += 1
        flag(st,'replacement_character',line,text)
    # Ambiguous Latin sequences are a review signal, never automatic corruption.
    if re.search(r'(?:\u00c3[\u0080-\u00bf]|\u00c2[\u0080-\u00bf]|\u00e2\u20ac[\u0090-\u00ff\u2010-\u203f])',text):
        flag(st,'possible_mojibake',line,text)
    lines = text.splitlines()
    nonempty = [x for x in lines if x.strip()]
    if REPEAT.search(text): flag(st,'long_repeated_character_run',line,text)
    if len(nonempty)>=10:
        repeats = 1-len(set(x.strip() for x in nonempty))/len(nonempty)
        if repeats > .5: flag(st,'over_half_repeated_lines',line,text)
    if len(words)>=100 and len(set(w.lower() for w in words))/len(words)<.12:
        flag(st,'low_word_diversity',line,text)
    if text.count('```')%2: flag(st,'unbalanced_markdown_fences',line,text)
    for name,pat in LICENSE_PATTERNS.items():
        if pat.search(text): st['license_hints'][name] += 1
    if any(pat.search(text) for pat in LICENSE_PATTERNS.values()):
        st['license_hints']['any_license_hint_records'] += 1
    checks = [('email_like',EMAIL if '@' in text else None),('phone_like',PHONE),('ssn_like',SSN),
              ('ipv4_like',IP),('street_address_like',ADDRESS),('known_token_pattern',TOKEN),
              ('private_key_block',re.compile(r'-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----')),
              ('credential_assignment',ASSIGN)]
    for name,pat in checks:
        if pat is None: continue
        found = list(pat.finditer(text))
        if found:
            st['privacy'][name] += 1
            st['privacy_occurrences'][name] += len(found)
            refs = st['privacy_refs'].setdefault(name,[])
            if len(refs)<12:
                # Never put matched values in persistent reports.
                refs.append({'line':line,'value':'[REDACTED]', 'occurrences_in_record':len(found)})
    language = str(obj.get('language','')).lower() if isinstance(obj,dict) else ''
    if language: st['languages_declared'][language] += 1
    cues = [k for k,p in CODE_CUES.items() if p.search(text)]
    for k in cues: st['code_cues'][k] += 1
    if '```' in text: st['code_cues']['markdown_fence_records'] += 1
    is_code = '/code/' in st['path'] or language in CODE_CUES
    if is_code:
        if language not in cues: flag(st,'no_expected_language_cue',line,text)
        st['code_lines']['records_with_newlines'] += int('\n' in text or '\r' in text)
        st['code_lines']['records_with_tabs'] += int('\t' in text)
        st['code_lines']['records_with_crlf'] += int('\r\n' in text)
        st['code_lines']['records_with_leading_indentation'] += int(bool(re.search(r'(?m)^[ \t]+\S',text)))
        st['code_lines']['records_without_final_newline'] += int(not text.endswith(('\n','\r')))
        st['code_lines']['lines'] += len(lines)
        st['code_lines']['nonempty_lines'] += len(nonempty)
        st['code_lines']['indented_lines'] += sum(bool(re.match(r'[ \t]+\S',x)) for x in lines)
        comment_lines = sum(bool(re.match(r'\s*(?:#|//|/\*|\*|\*/)',x)) for x in nonempty)
        st['code_lines']['comment_like_lines'] += comment_lines
        if len(nonempty)>=10 and comment_lines/len(nonempty)>.8:
            flag(st,'over_80pct_comment_like_lines',line,text)
        max_line = max(map(len,lines),default=0)
        if max_line>2000 and (max_line/max(1,size)>.4 or len(lines)<10):
            flag(st,'minified_or_large_single_line',line,text)
        if language=='python':
            try:
                ast.parse(text)
                st['python3_ast']['accepted'] += 1
            except (SyntaxError,ValueError,RecursionError) as e:
                reason = type(e).__name__ + ': ' + str(getattr(e,'msg','parse failure'))
                st['python3_ast']['rejected'] += 1
                st['python3_ast'][reason] += 1
                st['python3_ast_examples'].setdefault(reason,[])
                if len(st['python3_ast_examples'][reason])<3:
                    st['python3_ast_examples'][reason].append({'record_line':line,'source_line':getattr(e,'lineno',None)})
    if kind=='instruction_pair':
        for q,a in [('question','answer'),('instruction','output'),('prompt','completion'),('prompt','response')]:
            if q in obj or a in obj:
                if not all(isinstance(obj.get(k),str) and obj[k].strip() for k in (q,a)):
                    flag(st,'incomplete_instruction_pair',line,text)
                break

def init_db(out):
    # Reusable cache contains hashes, offsets and signatures, never source text.
    db = sqlite3.connect(out / 'audit_index.sqlite')
    db.executescript('''PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA temp_store=FILE;
      DROP TABLE IF EXISTS docs; DROP TABLE IF EXISTS bands; DROP TABLE IF EXISTS templates; DROP TABLE IF EXISTS components;
      CREATE TABLE docs(id INTEGER PRIMARY KEY, file_id INT, line INT, offset INT, raw_bytes INT, chars INT, words INT, exact BLOB, norm BLOB, sig BLOB);
      CREATE TABLE bands(band INT, value BLOB, doc INT);
      CREATE TABLE templates(file_id INT, hash BLOB, line INT);
      CREATE TABLE components(file_id INT, role TEXT, hash BLOB, line INT);
    ''')
    return db

def scan_file(path, root, db, file_id, anchors=400):
    st = new_stats(path,root)
    rng = random.Random(SEED+file_id)
    review_rng = random.Random(SEED+100000+file_id)
    hasher = hashlib.sha256()
    start = time.monotonic()
    last_progress = start
    with path.open('rb') as f:
        while True:
            offset=f.tell()
            raw=f.readline()
            if not raw: break
            hasher.update(raw)
            st['physical_lines'] += 1
            line=st['physical_lines']
            if not raw.strip():
                st['blank_lines'] += 1
                continue
            try:
                obj = load_strict(raw)
            except (ValueError,UnicodeError,RecursionError) as e:
                st['invalid_records'] += 1
                if isinstance(e,UnicodeDecodeError): st['signals']['invalid_utf8']+=1
                if raw.startswith(b'\xef\xbb\xbf'): st['signals']['utf8_bom']+=1
                if len(st['errors'])<15:
                    st['errors'].append({'line':line,'error_type':type(e).__name__,
                                         'reason':getattr(e,'msg',str(e).split(':')[0])})
                continue
            st['parsed_records'] += 1
            if isinstance(obj,dict):
                st['object_records'] += 1
                st['schema'][','.join(sorted(obj))] += 1
                for key,value in obj.items():
                    st['field_present'][key] += 1
                    st['field_types'].setdefault(key,collections.Counter())[type(value).__name__] += 1
                    if value is None: st['null_fields'][key] += 1
                    if isinstance(value,str) and not value.strip(): st['empty_fields'][key] += 1
                for key,value in nested_fields(obj):
                    st['nested_field_types'].setdefault(key,collections.Counter())[type(value).__name__] += 1
                    if value is None: st['nested_nulls'][key] += 1
            else:
                st['schema'][type(obj).__name__] += 1
            parts,kind = parts_of(obj)
            st['formats'][kind] += 1
            if not parts:
                flag(st,'no_extractable_text',line,'')
                continue
            text='\n'.join(t for _,t in parts)
            scan_content(st,text,obj,kind,line)
            exact=canonical(parts)
            norm=canonical([(k,normalized(t)) for k,t in parts])
            # Single text field uses the same canonical normalization as plain text.
            if len(parts)==1: norm=normalized(parts[0][1])
            sig=signature(normalized(text)) if len(LEX.findall(text))>=10 else None
            cur=db.execute('INSERT INTO docs(file_id,line,offset,raw_bytes,chars,words,exact,norm,sig) VALUES (?,?,?,?,?,?,?,?,?)',
                           (file_id,line,offset,len(raw),len(text),len(text.split()),digest(exact),digest(norm),sig))
            doc_id=cur.lastrowid
            if sig:
                db.executemany('INSERT INTO bands VALUES (?,?,?)',[(i,sig[i*32:i*32+32],doc_id) for i in range(16)])
            if kind=='instruction_pair':
                q=parts[0][1]
                db.execute('INSERT INTO templates VALUES (?,?,?)',(file_id,digest(template_of(q)),line))
                for role,t in parts:
                    db.execute('INSERT INTO components VALUES (?,?,?,?)',(file_id,role,digest(normalized(t)),line))
            reservoir_add(st['sample_refs'],{'doc':doc_id,'line':line},st['text_records'],anchors,rng)
            reservoir_add(st['content_review_refs'],{'doc':doc_id,'line':line},st['text_records'],40,review_rng)
            now=time.monotonic()
            if line%2000==0 or now-last_progress>20:
                print(f"SCAN {st['path']}: lines={line:,}, text_records={st['text_records']:,}, read={f.tell()/1e6:.1f} MB, elapsed={now-start:.1f}s",flush=True)
                db.commit()
                last_progress=now
    db.commit()
    st['sha256_before']=hasher.hexdigest()
    st['field_missing']={key:st['object_records']-n for key,n in st['field_present'].items()}
    lengths=[r[0] for r in db.execute('SELECT chars FROM docs WHERE file_id=? ORDER BY chars',(file_id,))]
    st['length_chars']={k:(lengths[min(len(lengths)-1,int((len(lengths)-1)*q))] if lengths else None)
                        for k,q in [('min',0),('p10',.1),('p50',.5),('p90',.9),('p95',.95),('p99',.99),('max',1)]}
    st['length_chars']['mean']=st['text_chars']/max(1,st['text_records'])
    # Explicitly rough character-based interval; UTF-8 file bytes are not tokens.
    st['estimated_tokens']={'method':'decoded text characters / [5, 3]; not model token counts',
                            'low':round(st['text_chars']/5),'mid':round(st['text_chars']/4),'high':round(st['text_chars']/3)}
    st['scan_seconds']=round(time.monotonic()-start,3)
    print(f"DONE {st['path']}: {st['parsed_records']:,} valid, {st['invalid_records']:,} invalid",flush=True)
    return st

def duplicate_metrics(db, stats):
    result={}
    for column in ['exact','norm']:
        groups=db.execute(f'SELECT COUNT(*),SUM(n-1),SUM(n),MAX(n) FROM (SELECT COUNT(*) n FROM docs GROUP BY {column} HAVING n>1)').fetchone()
        cross={}
        for f1,f2,n in db.execute(f'''SELECT a.file_id,b.file_id,COUNT(*) FROM
            (SELECT DISTINCT file_id,{column} h FROM docs) a JOIN
            (SELECT DISTINCT file_id,{column} h FROM docs) b ON a.h=b.h AND a.file_id<b.file_id
            GROUP BY a.file_id,b.file_id'''):
            cross[stats[f1]['path']+' <> '+stats[f2]['path']]=n
        result[column]={'duplicate_groups':groups[0], 'redundant_records':groups[1] or 0,
                        'records_in_duplicate_groups':groups[2] or 0,'largest_group':groups[3] or 0,
                        'cross_dataset_shared_unique_documents':cross}
        for i,st in enumerate(stats):
            row=db.execute(f'SELECT COUNT(*),SUM(n-1),SUM(n),MAX(n) FROM (SELECT COUNT(*) n FROM docs WHERE file_id=? GROUP BY {column} HAVING n>1)',(i,)).fetchone()
            st[column+'_duplicates']={'groups':row[0],'redundant_records':row[1] or 0,'participating_records':row[2] or 0,'max_copies':row[3] or 0}
    for i,st in enumerate(stats):
        top=[]
        for n,line,h in db.execute('SELECT COUNT(*) n,MIN(line),hash FROM templates WHERE file_id=? GROUP BY hash ORDER BY n DESC LIMIT 12',(i,)):
            top.append({'count':n,'first_line':line,'template_hash':h.hex()})
        st['question_template_groups']={'method':'lowercase; replace quoted/backtick spans and numeric literals; collapse whitespace',
            'distinct':db.execute('SELECT COUNT(DISTINCT hash) FROM templates WHERE file_id=?',(i,)).fetchone()[0],
            'top':top}
        st['component_duplicates']={}
        for role, in db.execute('SELECT DISTINCT role FROM components WHERE file_id=?',(i,)):
            n,unique=db.execute('SELECT COUNT(*),COUNT(DISTINCT hash) FROM components WHERE file_id=? AND role=?',(i,role)).fetchone()
            st['component_duplicates'][role]={'records':n,'distinct':unique,'redundant_records':n-unique}
    return result

def read_text(db, doc, stats, root, cache):
    row=db.execute('SELECT file_id,line,offset,raw_bytes,norm FROM docs WHERE id=?',(doc,)).fetchone()
    fid,line,offset,length,nhash=row
    if fid not in cache: cache[fid]=(root/stats[fid]['path']).open('rb')
    f=cache[fid]
    f.seek(offset)
    parts,_=parts_of(load_strict(f.read(length)))
    return '\n'.join(t for _,t in parts),row

def wilson(k,n):
    if not n: return [None,None]
    z=1.96;p=k/n;den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [round(max(0,mid-half),6),round(min(1,mid+half),6)]

def near_scan(db, stats, root):
    cache={}; results=[]; all_examples=[]
    # Disk-backed LSH: full corpus index; uniform anchors per dataset.
    # Buckets >5000 and candidate lists >10000 are bounded and explicitly counted.
    for fid,st in enumerate(stats):
        n=eligible=hits=cross_hits=exact_excluded=skipped_buckets=capped=0
        pairs_checked=0; examples=[]; start=time.monotonic()
        for ref in st['sample_refs']:
            n+=1;doc=ref['doc']
            sig,nhash=db.execute('SELECT sig,norm FROM docs WHERE id=?',(doc,)).fetchone()
            if not sig: continue
            eligible+=1
            candidates=set()
            for band in range(16):
                rows=db.execute('SELECT doc FROM bands WHERE band=? AND value=? LIMIT 5001',(band,sig[band*32:band*32+32])).fetchall()
                if len(rows)>5000:
                    skipped_buckets+=1
                    continue
                candidates.update(r[0] for r in rows if r[0]!=doc)
            if len(candidates)>10000:
                capped+=1
                candidates=set(random.Random(SEED+doc).sample(sorted(candidates),10000))
            anchor_features=None; matched=False; cross=False
            for other in sorted(candidates):
                other_sig,other_hash,other_fid=db.execute('SELECT sig,norm,file_id FROM docs WHERE id=?',(other,)).fetchone()
                if other_hash==nhash:
                    exact_excluded+=1
                    continue
                equal=sum(sig[i:i+8]==other_sig[i:i+8] for i in range(0,512,8))/64
                if equal<.65: continue
                if anchor_features is None:
                    text,_=read_text(db,doc,stats,root,cache)
                    anchor_features=shingles(normalized(text))
                other_text,row=read_text(db,other,stats,root,cache)
                other_features=shingles(normalized(other_text))
                similarity=len(anchor_features&other_features)/max(1,len(anchor_features|other_features))
                pairs_checked+=1
                if similarity>=.8:
                    matched=True
                    cross |= other_fid!=fid
                    if len(examples)<15:
                        examples.append({'file':st['path'],'line':ref['line'],'other_file':stats[other_fid]['path'],
                                         'other_line':row[1],'five_token_shingle_jaccard':round(similarity,6)})
            hits+=matched;cross_hits+=cross
            if n%100==0:
                print(f"NEAR {st['path']}: anchors={n}/{len(st['sample_refs'])}, matches={hits}, elapsed={time.monotonic()-start:.1f}s",flush=True)
        result={'path':st['path'],'population':st['text_records'],'random_anchors':n,'eligible_anchors_10plus_lexical_tokens':eligible,
                'anchors_with_detected_nonexact_near_duplicate':hits,'rate_over_all_anchors':hits/max(1,n),
                'wilson_95pct_for_detector_positive_rate':wilson(hits,n),
                'anchors_with_cross_dataset_near_duplicate':cross_hits,'candidate_pairs_verified':pairs_checked,
                'normalized_equal_candidates_excluded':exact_excluded,'oversized_buckets_skipped':skipped_buckets,
                'anchors_with_candidate_cap':capped,'examples':examples}
        results.append(result);st['near_duplicates']=result
    for f in cache.values(): f.close()
    return {'method':'64 deterministic minhash-like salted uint64 minima over case-sensitive lexical 5-token shingles; 16 bands x 4; >=10 lexical tokens; feature cap 8192 for signatures; >=0.65 signature equality shortlist; exact full-shingle Jaccard >=0.80 verification. Full-corpus hash index with seeded uniform per-file anchor samples. Normalized exact matches excluded.',
            'limitations':'Detector recall is uncalibrated; intervals describe detector-positive anchor rate, not a proven corpus near-duplicate rate. No near search on <10 lexical token anchors. Caps and skipped buckets are recorded; partial/translated/renamed-code matches may be missed. No claim of exhaustive pairwise near scan.',
            'datasets':results}

def verify_simple_qa(path):
    """Narrow, deterministic validators; no eval(), dataset execution or fact claims."""
    result={'scope':'Only exactly recognized simple integer arithmetic, ISO-date weekdays, and explicitly requested JSON-array structure. Other answers are unverified.',
            'checked':collections.Counter(),'failed':collections.Counter(),'failures':[]}
    with path.open('rb') as f:
        for line,raw in enumerate(f,1):
            try: obj=load_strict(raw)
            except (ValueError,UnicodeError): continue
            if not isinstance(obj,dict): continue
            q,a=obj.get('question'),obj.get('answer')
            if not isinstance(q,str) or not isinstance(a,str): continue
            # Require an explicit calculation prompt and a whole-answer integer.
            m=re.fullmatch(r'(?:Calculate|Compute|Evaluate(?: the expression)?|What is)\s*:?\s*(-?\d+)\s*([+*\u00d7\u2212-])\s*(-?\d+)\s*[?.]?',q,re.I)
            if m and re.fullmatch(r'\s*`?(-?\d+)`?[.]?\s*',a):
                x,op,y=int(m[1]),m[2],int(m[3]); expected=x+y if op=='+' else x-y if op in ['-','\u2212'] else x*y
                actual=int(re.fullmatch(r'\s*`?(-?\d+)`?[.]?\s*',a)[1])
                result['checked']['integer_arithmetic']+=1
                if expected!=actual:
                    result['failed']['integer_arithmetic']+=1
                    if len(result['failures'])<20: result['failures'].append({'line':line,'question':excerpt(q),'answer':excerpt(a),'expected':expected})
            m=re.fullmatch(r'What day of the week was (\d{4}-\d{2}-\d{2})\?',q)
            if m:
                try: expected=dt.date.fromisoformat(m[1]).strftime('%A')
                except ValueError: continue
                result['checked']['iso_weekday']+=1
                if a.strip().strip('`.')!=expected:
                    result['failed']['iso_weekday']+=1
                    if len(result['failures'])<20: result['failures'].append({'line':line,'question':q,'answer':excerpt(a),'expected':expected})
            m=re.fullmatch(r'Produce a JSON array containing exactly these words in order: (.+)\.',q)
            if m:
                expected=m[1].split(', ')
                result['checked']['literal_json_array']+=1
                try: actual=json.loads(a)
                except ValueError: actual=None
                if actual!=expected:
                    result['failed']['literal_json_array']+=1
                    if len(result['failures'])<20: result['failures'].append({'line':line,'question':excerpt(q),'answer':excerpt(a),'expected':expected})
    return result

def profile_tokenizer_inputs(root):
    result={'trained_models':[], 'training_scripts':[], 'plain_text_inputs':[]}
    for current,dirs,files in os.walk(root):
        dirs[:]=[d for d in dirs if d not in ['.git','reports'] and not (Path(current)/d).is_symlink()]
        for name in files:
            p=Path(current)/name
            if p.suffix.lower() in ['.model','.vocab'] or name in ['tokenizer.json','tokenizer_config.json','spiece.model','tokenizer.model']:
                result['trained_models'].append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size})
    for p in sorted((root/'src/tokenizer').glob('*.py')):
        result['training_scripts'].append({'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    for p in sorted((root/'src/tokenizer').glob('*.txt')):
        chars=lines=blank=0; scripts=collections.Counter(); head=[]; h=hashlib.sha256()
        with p.open('rb') as f:
            for raw in f:
                h.update(raw);text=raw.decode('utf-8','replace');chars+=len(text);lines+=1;blank+=not text.strip()
                if len(head)<8: head.append(excerpt(text.strip(),150))
                for ch,n in collections.Counter(text).items():
                    scripts['ascii' if ord(ch)<128 else 'math_symbols' if unicodedata.category(ch)=='Sm' else 'other_nonascii']+=n
        result['plain_text_inputs'].append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'chars':chars,
                'physical_lines':lines,'blank_lines':blank,'sha256':h.hexdigest(),'script_characters':scripts,
                'initial_redacted_lines':head})
    result['model_tests']={'status':'NOT RUN: no trained tokenizer artifacts found' if not result['trained_models'] else 'Review trained_models; automatic tests only supported for SentencePiece .model files',
                            'round_trip':None,'tokens_per_byte':None,'full_corpus_model_token_counts':None}
    # Never train a tokenizer. Only load already existing SentencePiece models.
    for item in result['trained_models']:
        if not item['path'].endswith('.model'): continue
        try:
            import sentencepiece as spm
            model=spm.SentencePieceProcessor(model_file=str(root/item['path']))
            tests=[]
            samples=['Natural English: punctuation, contractions, and caf\u00e9.',
                     'def f(x):\n\treturn x + 1\n', '    four spaces\n\nend\n',
                     '#include <vector>\nstd::vector<int> xs{1,2};\n',
                     'fn main() {\n    let mut x = 1;\n}\n','\u2200 x \u2208 \u211d: x\u00b2 \u2265 0; \u03b1 + \u03b2 = \u03b3\n']
            for s in samples:
                ids=model.encode(s);decoded=model.decode(ids)
                tests.append({'chars':len(s),'bytes':len(s.encode()),'tokens':len(ids),'round_trip_equal':decoded==s,'contains_unk_id':model.unk_id() in ids})
            item['sentencepiece_tests']={'vocab_size':model.vocab_size(),'controlled_probe_results':tests,
                    'limitation':'Controlled probes only; corpus compression is not measured by this branch.'}
        except Exception as e:
            item['load_error']=type(e).__name__
    return result

def stage(st):
    path=st['path']
    if '/code/' in path: return 'coding pretraining; balanced tokenizer component'
    if path.endswith('fineweb.jsonl'): return 'general pretraining; natural-language tokenizer component'
    if path.endswith('peregrine_ml_ai_pretrain_text.jsonl'): return 'small technical-text supplement after review; contains QA-style headings and code'
    if st['formats'].get('instruction_pair'): return 'instruction tuning after validation; small optional tokenizer supplement'
    return 'none (empty)' if not st['parsed_records'] else 'review schema and content'

def verdict(st):
    if not st['parsed_records']: return 'NOT SUITABLE'
    if st['invalid_records'] or st['signals'].get('no_extractable_text') or st['privacy'].get('private_key_block') or st['privacy'].get('known_token_pattern'):
        return 'REVIEW REQUIRED'
    if '/code/' in st['path'] or st['path'].endswith('gren_dataset.jsonl'):
        return 'REVIEW REQUIRED'
    if st['path'].endswith('peregrine_ml_ai_pretrain_text.jsonl') or st['path'].endswith('src/dataset_generator/general.jsonl'):
        return 'REVIEW REQUIRED'
    return 'NEEDS IMPROVEMENT'

def write_inventory(out,stats):
    columns=['path','bytes','physical_lines','blank_lines','parsed_records','invalid_records','schema','field_types','missing_fields','null_fields','empty_fields','formats','text_chars','text_utf8_bytes','length_min','length_p50','length_p99','length_max','rough_tokens_low','rough_tokens_mid','rough_tokens_high','exact_redundant_records','whitespace_normalized_redundant_records','intended_use','verdict','sha256','unchanged_after_audit']
    with (out/'dataset_inventory.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        for st in stats:
            writer.writerow({'path':st['path'],'bytes':st['bytes'],'physical_lines':st['physical_lines'],'blank_lines':st['blank_lines'],
                'parsed_records':st['parsed_records'],'invalid_records':st['invalid_records'],'schema':json.dumps(st['schema']),
                'field_types':json.dumps(st['field_types']),'missing_fields':json.dumps(st['field_missing']),
                'null_fields':json.dumps(st['null_fields']),'empty_fields':json.dumps(st['empty_fields']),'formats':json.dumps(st['formats']),
                'text_chars':st['text_chars'],'text_utf8_bytes':st['text_utf8_bytes'],
                **{'length_'+x:st['length_chars'][x] for x in ['min','p50','p99','max']},
                **{'rough_tokens_'+x:st['estimated_tokens'][x] for x in ['low','mid','high']},
                'exact_redundant_records':st['exact_duplicates']['redundant_records'],
                'whitespace_normalized_redundant_records':st['norm_duplicates']['redundant_records'],
                'intended_use':st['intended_use'],'verdict':st['verdict'],'sha256':st['sha256_before'],'unchanged_after_audit':st['unchanged_after_audit']})

def save_metrics(out, report):
    (out/'quality_metrics.json').write_text(json.dumps(report,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')

def supplemental_checks(root,out,report):
    """Additional bounded streaming checks; also usable on an existing full scan."""
    print('SUPPLEMENT paragraphs, credential context, historical syntax and tokenizer inputs',flush=True)
    db=sqlite3.connect(out/'audit_index.sqlite')
    db.executescript('DROP TABLE IF EXISTS blocks; CREATE TABLE blocks(file_id INT,line INT,hash BLOB,chars INT);')
    for fid,st in enumerate(report['datasets']):
        st.pop('signal_chars',None)
        context=collections.Counter(); credential_refs=[]; historic=collections.Counter(); keys=[]
        with (root/st['path']).open('rb') as f:
            for line,raw in enumerate(f,1):
                try: obj=load_strict(raw)
                except (ValueError,UnicodeError): continue
                parts,kind=parts_of(obj);text='\n'.join(t for _,t in parts)
                if not text: continue
                for block in re.split(r'\n\s*\n',text):
                    norm=normalized(block)
                    if len(norm)>=120:
                        db.execute('INSERT INTO blocks VALUES (?,?,?,?)',(fid,line,digest(norm),len(norm)))
                for match in ASSIGN.finditer(text):
                    value=match[3].strip()
                    placeholder=bool(re.fullmatch(r'(?i)(?:password\d*|passwd|test\w*|example\w*|dummy\w*|changeme|change_me|your[_ -].*|secret|admin|root|foo|bar|123\d*|x{4,}|\*{4,}|[<{$].*|token|none|null|abcd\w*)',value))
                    name='obvious_placeholder_or_example_assignment' if placeholder else 'nontrivial_credential_assignment_candidate'
                    context[name]+=1
                    if len(credential_refs)<20:
                        credential_refs.append({'line':line,'classification':name,'value':'[REDACTED]',
                            'test_context_hint':bool(re.search(r'(?i)\b(?:test|fixture|mock|example|sample|dummy)\b',text[max(0,match.start()-500):match.end()+500]))})
                if re.search(r'(?m)^\s*print\s+(?!\()[^\n]+|\bexcept\s+\w+\s*,\s*\w+\s*:|\bxrange\s*\(',text):
                    historic['python2_syntax_cue_records']+=1
                if re.search(r'\bextern mod\b|\bret\s+|~str\b|\bint\b\s*\{',text) and st['path'].endswith('rust.jsonl'):
                    historic['historical_rust_syntax_cue_records']+=1
                if kind=='text' and st['path'].endswith('fineweb.jsonl'):
                    if text and text[0].islower():historic['starts_lowercase_review_signal']+=1
                    if re.search(r'(?i)sign in\s*/\s*sign out|navigation for entire|join to access all|\d+ views \d+ downloads|no prep.{0,30}print',text):
                        historic['navigation_or_catalogue_review_signal']+=1
                for match in re.finditer(r'-----BEGIN ([A-Z0-9 ]*PRIVATE KEY)-----',text):
                    end=text.find('-----END ',match.end())
                    body=text[match.end():end if end>=0 else match.end()+400]
                    material=bool(re.search(r'[A-Za-z0-9+/=]{60,}',body))
                    keys.append({'line':line,'key_type':match[1],'end_marker_present':end>=0,'base64_material_like':material,
                                 'value':'[REDACTED PRIVATE KEY MATERIAL]',
                                 'test_context_hint':bool(re.search(r'(?i)\b(?:test|fixture|mock|example|sample|dummy)\b',text[:2000]))})
        st['credential_context']=dict(context);st['credential_context_refs']=credential_refs
        st['private_key_review']=keys;st['historical_or_fragment_cues']=dict(historic)
        # Avoid publishing bulk source excerpts; targeted safe evidence is in issues.md.
        for examples in st['signal_examples'].values():
            for item in examples: item.pop('excerpt',None)
        db.commit()
        print(f"SUPPLEMENT {st['path']}: complete",flush=True)
    db.executescript('CREATE INDEX blocks_idx ON blocks(hash); CREATE INDEX blocks_file_idx ON blocks(file_id);')
    groups,excess,chars=db.execute('SELECT COUNT(*),SUM(n-1),SUM((n-1)*size) FROM (SELECT COUNT(*) n,MIN(chars) size FROM blocks GROUP BY hash HAVING n>1)').fetchone()
    top=[]
    for h,n,size in db.execute('SELECT hash,COUNT(*) n,MIN(chars) size FROM blocks GROUP BY hash HAVING COUNT(*)>1 ORDER BY n DESC LIMIT 20'):
        refs=[{'file':report['datasets'][fid]['path'],'line':line} for fid,line in db.execute('SELECT file_id,line FROM blocks WHERE hash=? LIMIT 6',(h,))]
        top.append({'hash':h.hex(),'occurrences':n,'normalized_chars':size,'examples':refs})
    report['repeated_blocks']={'method':'Full corpus: split on blank-line boundaries, collapse whitespace, hash blocks >=120 normalized characters. Counts occurrences, including repeated blocks inside a record; may include licenses and legitimate shared declarations. Not a semantic duplicate count.',
        'groups':groups,'redundant_block_occurrences':excess or 0,'rough_redundant_normalized_chars':chars or 0,'top':top}
    for fid,st in enumerate(report['datasets']):
        g,n=db.execute('SELECT COUNT(*),SUM(n-1) FROM (SELECT COUNT(*) n FROM blocks WHERE file_id=? GROUP BY hash HAVING n>1)',(fid,)).fetchone()
        st['repeated_blocks']={'groups':g,'redundant_block_occurrences':n or 0}
    # Reproduce the observed helper output without writing an extract.
    cpp=root/'datasets/code/cpp.jsonl';extract=root/'src/tokenizer/extracted_texts.txt'
    if cpp.exists() and extract.exists():
        native=hashlib.sha256();windows=hashlib.sha256();n=missing=crlf=0
        with cpp.open('rb') as f:
            for raw in f:
                try:obj=load_strict(raw)
                except (ValueError,UnicodeError):continue
                text=obj.get('text')
                if not isinstance(text,str):continue
                n+=1;missing+=not text.endswith(('\n','\r'));crlf+=text.count('\r\n')
                native.update(text.encode('utf-8'));windows.update(text.replace('\n','\r\n').encode('utf-8'))
        h=hashlib.sha256()
        with extract.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        report['tokenizer']['cpp_extract_check']={'cpp_records':n,'records_without_terminal_newline':missing,
            'source_crlf_sequences':crlf,'matches_native_concatenation':h.hexdigest()==native.hexdigest(),
            'matches_windows_newline_expanded_concatenation':h.hexdigest()==windows.hexdigest(),
            'consequence':'CRLF source sequences become CRCRLF; missing terminal newlines permit joined document boundaries. Source JSONL text itself remains unchanged.'}
    for item in report['tokenizer']['plain_text_inputs']:
        p=root/item['path'];c=collections.Counter();total=max_line=too_long=0;hints=collections.Counter()
        with p.open('rb') as f:
            for raw in f:
                text=raw.decode('utf-8','replace').rstrip('\r\n');norm=normalized(text)
                max_line=max(max_line,len(raw.rstrip(b'\r\n')));too_long+=len(raw.rstrip(b'\r\n'))>4192
                if norm:c[digest(norm)]+=1;total+=1
                for lang,pat in CODE_CUES.items():
                    if pat.search(text):hints[lang]+=1
        item['normalized_nonempty_line_repetition']={'nonempty_lines':total,'distinct':len(c),'redundant_occurrences':sum(x-1 for x in c.values()),'max_copies':max(c.values(),default=0),
            'interpretation':'Line repetition is diagnostic; repeated braces and common syntax are expected and must not be indiscriminately removed.'}
        item['line_bytes_max']=max_line;item['lines_over_default_sentencepiece_max_sentence_length_4192_bytes']=too_long
        item['line_level_code_cues']=dict(hints)
        item.pop('initial_redacted_lines',None)
    report['manual_review']={'review_type':'Qualitative review of redacted excerpts; not all full documents and not a factual-error prevalence estimate.',
        'seed_and_sampling':'Algorithm R; reservoir 22 per curated file with seed 20261023; 8 per code file and 20 FineWeb with seed 4401; all 2 generator examples. Earlier 4-record peeks and targeted issue examples additional, not counted.',
        'core_sample_count':128,'reviewed_on':'2026-10-23 America/Phoenix',
        'refs':{
          'datasets/curated/peregrine_general_32180.jsonl':[66,392,721,739,2382,3125,3480,3776,5147,5282,9131,10231,15480,18002,18466,19977,23238,26301,27060,27363,27929,29172],
          'datasets/curated/gren_dataset.jsonl':[66,96,174,293,392,400,480,553,564,691,721,739,810,859,941,1029,1110,1114,1298,1367,1739,2051],
          'datasets/curated/peregrine_ml_ai_pretrain_text.jsonl':[16,60,66,96,115,150,162,174,192,230,235,247,293,306,356,382,388,392,400,477,480,499],
          'datasets/code/cpp.jsonl':[66,74,321,613,630,685,1199,1345],
          'datasets/code/java.jsonl':[74,630,685,1199,2002,2010,2818,3002],
          'datasets/code/javascript.jsonl':[74,613,630,685,1199,2002,2010,2218],
          'datasets/code/python.jsonl':[74,613,630,685,1199,2002,2010,2218],
          'datasets/code/rust.jsonl':[74,613,630,685,1199,2002,2010,2010,2218],
          'datasets/general/fineweb.jsonl':[526,692,862,1989,2015,2826,2977,3010,3176,3557,3709,4029,4924,5040,7119,8088,9129,10432,11353,11978],
          'src/dataset_generator/general.jsonl':[1,2]},
        'technical_accuracy':'1,863 narrowly recognized QA answers checked deterministically (see per-file results); selected Gren String and Dict APIs checked against core 7.0.0 official documentation; a FineWeb history contradiction confirmed against British Museum content. Other claims not exhaustively verified. No dataset code executed.'}
    # Correct the Rust sample's eight distinct Algorithm-R references.
    report['manual_review']['refs']['datasets/code/rust.jsonl']=[74,613,630,685,1199,2002,2010,2218]
    reviewed={s['path']:s['sha256_before'] for s in report['datasets']}==REVIEWED_SHA256
    reviewed = reviewed and not report['tokenizer']['trained_models']
    expected_tokenizer_files={
      'src/tokenizer/tokenizer.py':'2d75b70dee0afe919155ebd5adec48f322e28d19fe88fe02b86782e99f4acee8',
      'src/tokenizer/tokenizer_dataset.py':'d888a7ffc87a7666fa028fafbe2b0dcdfc7823197b8ebeb6acf461a86c906a51',
      'src/tokenizer/peregrine_tokenizer_starter.txt':'d9dae778a98e2af961f1e6a7035200b7bf89852b4b9c3ca1b5a0192df78dae06',
      'src/tokenizer/extracted_texts.txt':'09d907e1124d0e41e3b4a0691098f35e7d1e6307bcbc2e58e9cd9ff66f705b83'}
    tokenizer_fingerprints={x['path']:x['sha256'] for key in ['training_scripts','plain_text_inputs'] for x in report['tokenizer'][key]}
    reviewed=reviewed and tokenizer_fingerprints==expected_tokenizer_files
    report['audit']['qualitative_review_snapshot_matches']=reviewed
    if not reviewed:
        report['manual_review']={'status':'NOT PERFORMED on this changed corpus. Prior qualitative conclusions and line references withheld; new manual review required.'}
    report['sources']=[
      {'title':'The Stack dataset card and terms','url':'https://huggingface.co/datasets/bigcode/the-stack-dedup/blob/main/README.md','supports':'upstream attribution/provenance, versioning, license-detection limits and removal terms'},
      {'title':'FineWeb-Edu dataset card','url':'https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu/blob/main/README.md','supports':'ODC-By and Common Crawl terms, educational selection bias; upstream metadata'},
      {'title':'Gren core 7.0.0 String','url':'https://packages.gren-lang.org/package/gren-lang/core/version/7.0.0/module/String','supports':'String.count code-point semantics; String.replace and String.split signatures'},
      {'title':'Gren core 7.0.0 Dict','url':'https://packages.gren-lang.org/package/gren-lang/core/version/7.0.0/module/Dict','supports':'Dict.set/member/get/values behavior'},
      {'title':'British Museum Cyrus cylinder description','url':'https://artsandculture.google.com/asset/cyrus-cylinder/4wHjbQnYhZgzVQ?hl=en','supports':'Cyrus reign 559-530 BCE contradicts joint invasion in 520 BCE'},
      {'title':'SentencePiece official options','url':'https://github.com/google/sentencepiece/blob/master/doc/options.md','supports':'normalization, whitespace handling, max_sentence_length and vocabulary options'},
      {'title':'Training Compute-Optimal Large Language Models','url':'https://arxiv.org/abs/2203.15556','supports':'illustrative scaling context; not a required Peregrine budget'}]
    db.close()
    return report

def pct(k,n):
    return f'{100*k/max(1,n):.2f}%'

def refine_results(root,out,r):
    db=sqlite3.connect(out/'audit_index.sqlite')
    db.execute('CREATE INDEX IF NOT EXISTS components_pair_idx ON components(file_id,line,role)')
    r['qa_consistency']={'coverage':'Full corpus normalized question/answer hashes; only records with both question and answer components.',
        'conflicting_question_groups':0,'examples':[]}
    rows=db.execute('''SELECT q.hash,COUNT(DISTINCT a.hash),MIN(q.file_id),MIN(q.line)
      FROM components q JOIN components a ON q.file_id=a.file_id AND q.line=a.line
      WHERE q.role='question' AND a.role='answer' GROUP BY q.hash HAVING COUNT(DISTINCT a.hash)>1''').fetchall()
    r['qa_consistency']['conflicting_question_groups']=len(rows)
    for h,n,fid,line in rows[:20]:
        r['qa_consistency']['examples'].append({'file':r['datasets'][fid]['path'],'line':line,'distinct_normalized_answers':n})
    cross=[]
    for f1,f2,n in db.execute('''SELECT a.file_id,b.file_id,COUNT(*) FROM
       (SELECT DISTINCT file_id,hash FROM blocks) a JOIN
       (SELECT DISTINCT file_id,hash FROM blocks) b ON a.hash=b.hash AND a.file_id<b.file_id
       GROUP BY a.file_id,b.file_id'''):
        cross.append({'file_a':r['datasets'][f1]['path'],'file_b':r['datasets'][f2]['path'],'shared_unique_blocks':n})
    r['repeated_blocks']['cross_dataset_shared_unique_blocks']=cross
    r['audit']['length_quantile_definition']='sorted decoded-character lengths at floor((n-1)*q); lower order statistic, no interpolation'
    for st in r['datasets']:st.pop('signal_chars',None)
    for st in r['datasets']:
        if '/code/' not in st['path']:continue
        mass={k:{'records':0,'decoded_chars':0} for k in ['generated_code','vendor_or_bundle','minified_or_large_single_line']}
        with (root/st['path']).open('rb') as f:
            for raw in f:
                try:text=load_strict(raw)['text']
                except (ValueError,UnicodeError,KeyError,TypeError):continue
                for key in ['generated_code','vendor_or_bundle']:
                    if PATTERNS[key].search(text):
                        mass[key]['records']+=1;mass[key]['decoded_chars']+=len(text)
                lines=text.splitlines();longest=max(map(len,lines),default=0)
                if longest>2000 and (longest/max(1,len(text))>.4 or len(lines)<10):
                    mass['minified_or_large_single_line']['records']+=1
                    mass['minified_or_large_single_line']['decoded_chars']+=len(text)
        for item in mass.values():item['share_of_dataset_chars']=item['decoded_chars']/max(1,st['text_chars'])
        st['code_artifact_candidate_mass']={'categories':mass,'limitation':'Full code corpus; heuristic document flags, with overlapping categories. Character mass is not token mass or a confirmed rejection fraction.'}
    if r['audit'].get('qualitative_review_snapshot_matches'):
        p=root/'datasets/code/javascript.jsonl'
        with p.open('rb') as f:
            for line,raw in enumerate(f,1):
                if line!=1525:continue
                text=load_strict(raw)['text']
                r['targeted_content_review']={'javascript_binary_like_record':{
                    'file':'datasets/code/javascript.jsonl','line':1525,'chars':len(text),
                    'replacement_characters':text.count('\ufffd'),'unusual_control_characters':len(CONTROL.findall(text)),
                    'expected_javascript_cue':bool(CODE_CUES['javascript'].search(text)),
                    'assessment':'JavaScript bundle/wrapper contains a heavily binary-like replacement-character payload; strong review/exclusion candidate for a source-code training view. JavaScript cues and sourceMappingURL are present; no claim that the wrapper is syntactically invalid. JSON and UTF-8 are valid.'},
                    'sensitive_context_review':{
                       'python_630':'Two RSA private-key blocks in authentication unit-test source; apparently test fixtures, no live/private deployment established.',
                       'python_1952':'AWS-shaped access-key string is explicitly labelled an example in a configuration comment.',
                       'python_1675':'Google-key-shaped string is assigned to _CELLSET_ID; shape alone does not prove a credential.',
                       'java_2951':'Hardcoded GOOGLE_MAPS_GEOCODING_API_KEY candidate; validity/scope not tested.',
                       'javascript_351_450_1252_1971_2024':'Google-service/Firebase/API-key-shaped values in URLs/configuration. Some client keys may be public identifiers; review access restrictions and provenance.'}}
                break
        r['manual_review']['targeted_additional_refs']=['datasets/code/javascript.jsonl:1525','datasets/code/python.jsonl:630','datasets/code/python.jsonl:1675','datasets/code/python.jsonl:1952','datasets/code/java.jsonl:2951','datasets/code/javascript.jsonl:351,450,1252,1971,2024']
    db.close()
    return r

def write_reports(out,r):
    if not r['audit'].get('qualitative_review_snapshot_matches'):
        write_generic_reports(out,r)
        return
    data=r['datasets'];by={s['path']:s for s in data};t=r['totals']
    code=[s for s in data if '/code/' in s['path']]
    web=by.get('datasets/general/fineweb.jsonl',{})
    qa=by.get('datasets/curated/peregrine_general_32180.jsonl',{})
    def stat(s,k):return s.get('signals',{}).get(k,0)
    def j(x):return json.dumps(x,ensure_ascii=True)
    def refs(s,k):return ', '.join(str(x['line']) for x in s.get('signal_examples',{}).get(k,[])) or 'none'
    def reason(s):
        if not s['parsed_records']:return 'Empty file: no training signal.'
        notes=[]
        if s['invalid_records']:notes.append(f"{s['invalid_records']} invalid JSON/encoding records")
        if '/code/' in s['path']:notes.append('source/revision/path/license metadata absent; sensitive and generated-code candidates require review')
        elif s['path'].endswith('fineweb.jsonl'):notes.append('educational prose with extraction, factual and boilerplate defects; source metadata absent')
        elif s['path'].endswith('peregrine_general_32180.jsonl'):notes.append('short templated QA; reserve for SFT and group related tasks before splitting')
        elif s['path'].endswith('gren_dataset.jsonl'):notes.append('niche templated QA; pin Gren version and validate code semantics; origin/license absent')
        elif s['path'].endswith('peregrine_ml_ai_pretrain_text.jsonl'):notes.append('small QA-style technical supplement; provenance and unverified technical examples need review')
        else:notes.append('only two prototype synthetic SFT examples; generation and rights metadata absent')
        return '; '.join(notes)+'.'
    for s in data:s['verdict_reason']=reason(s)
    total_priv=collections.Counter()
    for s in data:total_priv.update(s['privacy'])
    exact=r['duplicates']['exact'];norm=r['duplicates']['norm']
    lines=[
      '# Project Peregrine dataset audit', '',
      'Audit date: **2026-10-23, America/Phoenix**. Physical record references are **1-based JSONL line numbers**. This audit writes reports only; it does not preprocess, convert, delete, train, or execute dataset code.', '',
      f"**Readiness: suitable raw material for pipeline pilots and a balanced tokenizer-development corpus, after targeted review; not a production-ready foundation-model training release.** Inspected all **{t['jsonl_files']} JSONL files**, **{t['parsed_records']:,} parsed records**, **{t['file_bytes']:,} file bytes** ({t['file_bytes']/1e6:.2f} decimal MB). Found **{t['invalid_records']} invalid records**. All source SHA-256, sizes and mtimes remained unchanged: **{r['audit']['all_source_files_unchanged']}**.", '',
      f"Decoded training fields contain **{t['text_chars']:,} characters** and **{t['text_utf8_bytes']:,} UTF-8 payload bytes**. The rough character-based estimate is **{t['rough_tokens']['low']/1e6:.2f}–{t['rough_tokens']['high']/1e6:.2f} million tokens** (midpoint convention: {t['rough_tokens']['mid']/1e6:.2f}M). These are heuristics, **not tokenized counts or statistical bounds**; code, Unicode and obfuscated strings may fall outside this range. JSON serialization bytes are never treated as tokens.", '',
      'No dataset receives an unconditional **READY** verdict for production use. This does not mean every record is poor. Code is mostly recognizable source, FineWeb contains useful educational text, and many synthetic QA examples are mechanically correct. The unresolved issues are provenance/rights, sensitive material candidates, distribution, evaluation isolation, and selected extraction defects.', '',
      '## Per-dataset inventory and decisions', '',
      '| Dataset | Bytes | Records | Schema | Verdict | Intended stage |',
      '|---|---:|---:|---|---|---|']
    for s in data:
        lines.append(f"| `{s['path']}` | {s['bytes']:,} | {s['parsed_records']:,} | {'; '.join(s['schema']) or 'empty'} | **{s['verdict']}** | {s['intended_use']} |")
    lines+=['','### Evidence for each verdict','']
    for s in data:lines.append(f"- **{s['path']} — {s['verdict']}:** {s['verdict_reason']}")
    lines+=['','## Format, lengths and Unicode','',
      'All nonempty files use consistent top-level string fields: `text`; `text, language`; or `question, answer`. JSON escapes were decoded before inspecting source code. Tabs, LF and CRLF are legitimate code whitespace. Missing/null/empty fields are measured independently in the CSV and JSON. No one-schema assumption or conversion was applied.', '',
      '| Dataset | Text chars | Min / median / p99 / max chars | <80 chars | >100K chars |',
      '|---|---:|---|---:|---:|']
    for s in data:
        q=s['length_chars'];lines.append(f"| `{s['path']}` | {s['text_chars']:,} | {q['min']} / {q['p50']} / {q['p99']} / {q['max']} | {stat(s,'under_80_chars'):,} | {stat(s,'over_100000_chars'):,} |")
    lines+=['','Short correct QA, exception classes, headers and small snippets can be useful. Length flags are inspection thresholds, not rejection rules. Long code can be valid; packing/chunking must respect the future context budget and document boundaries.', '',
      '| Dataset | Non-ASCII records | Controls | U+FFFD | Surrogates | Bidi controls | Mojibake candidates |',
      '|---|---:|---:|---:|---:|---:|---:|']
    for s in data:
        u=s['unicode'];lines.append(f"| `{s['path']}` | {u.get('records_with_nonascii',0)} | {u.get('unusual_control_records',0)} | {u.get('replacement_character_records',0)} | {u.get('escaped_surrogate_records',0)} | {u.get('bidi_control_records',0)} | {stat(s,'possible_mojibake')} |")
    lines+=['','Controls and apparent mojibake can occur intentionally in regexes, test fixtures, string literals or terminal examples. CJK comments and mathematical symbols are valuable coverage, not corrupt text. Review flagged references in context.', '',
      '## Code corpus','',
      '| Language | Records | Payload bytes | Share of code characters | Newline records | Tab records | CRLF records | Generated cues | Bundle/vendor cues | Minified/long-line candidates |',
      '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    code_chars=sum(s['text_chars'] for s in code)
    for s in code:
        c=s['code_lines'];lines.append(f"| {Path(s['path']).stem} | {s['parsed_records']:,} | {s['text_utf8_bytes']:,} | {pct(s['text_chars'],code_chars)} | {c.get('records_with_newlines',0)} | {c.get('records_with_tabs',0)} | {c.get('records_with_crlf',0)} | {stat(s,'generated_code')} | {stat(s,'vendor_or_bundle')} | {stat(s,'minified_or_large_single_line')} |")
    lines+=['','Candidate **character mass** helps interpret record counts:','',
      '| Code file | Generated-cue character share | Bundle/vendor-cue character share | Minified/large-line character share |',
      '|---|---:|---:|---:|']
    for s in code:
        a=s.get('code_artifact_candidate_mass',{}).get('categories',{})
        lines.append(f"| `{s['path']}` | {100*a.get('generated_code',{}).get('share_of_dataset_chars',0):.2f}% | {100*a.get('vendor_or_bundle',{}).get('share_of_dataset_chars',0):.2f}% | {100*a.get('minified_or_large_single_line',{}).get('share_of_dataset_chars',0):.2f}% |")
    lines+=['','These categories overlap and are heuristic. JavaScript has a materially larger minified/large-line candidate share than the other language files; do not add shares or interpret them as a measured rejection rate. Useful generated interfaces and bundled libraries may still be retained at deliberate weights.','']
    py=by.get('datasets/code/python.jsonl',{});astm=py.get('python3_ast',{})
    lines+=['',f"Python 3 AST parsing accepted **{astm.get('accepted',0):,}** and rejected **{astm.get('rejected',0):,}** records using Python {sys.version.split()[0]}. Rejections include historical Python 2, snippets, intentional negative tests and real syntax defects. They are not a compile/run failure rate. Other languages were checked with source cues and manual excerpts, not compilers. No dependencies were imported from dataset source and no dataset code was executed.", '',
      'The code files carry the declared Python, C++, Rust, Java and JavaScript labels. Cue counts in the JSON are overlapping and heuristic, not an independent language classifier. Modern C++ and JavaScript may embed other languages; C++ also includes C-like headers. There are no dedicated C, Go, TypeScript, C#, shell or SQL datasets. Gren appears in a separate small QA collection.', '',
      'Generated register bindings, repeated libraries and bundles consume vocabulary and training budget when dominant. Useful tests, documentation, comments and short files should remain available. Do not strip all comments or license notices. An obfuscated JavaScript string at `datasets/code/javascript.jsonl:2218` is a strong review/exclusion candidate for a future derived training manifest; ordinary punctuation-heavy code is not.', '',
      '## Duplication and overlap','',
      f"Complete document hash scans found **{exact['redundant_records']:,} exact redundant records** in {exact['duplicate_groups']:,} groups, and **{norm['redundant_records']:,} whitespace-normalized redundant records** in {norm['duplicate_groups']:,} groups. These are separate totals; do not add them. SHA-256 hashes cover all extracted document text; QA documents preserve ordered field boundaries. No Unicode/case folding was applied.", '',
      f"Cross-dataset shared unique document counts: exact `{j(exact['cross_dataset_shared_unique_documents'])}`; whitespace-normalized `{j(norm['cross_dataset_shared_unique_documents'])}`. These tests do not establish the absence of copied paragraphs, library fragments or task-family overlap.", '',
      '| Dataset | Exact redundant | Whitespace-normalized redundant | Near-positive anchors / sampled anchors | Detector-positive 95% interval |',
      '|---|---:|---:|---|---|']
    for s in data:
        near=s.get('near_duplicates',{});ci=near.get('wilson_95pct_for_detector_positive_rate',[None,None])
        lines.append(f"| `{s['path']}` | {s['exact_duplicates']['redundant_records']} | {s['norm_duplicates']['redundant_records']} | {near.get('anchors_with_detected_nonexact_near_duplicate','not run')} / {near.get('random_anchors',0)} | {ci} |")
    lines+=['',r.get('near_duplicates',{}).get('method','Near scan not run.'),'',r.get('near_duplicates',{}).get('limitations',''),'',
      'The near scan indexes the full corpus but queries up to 400 seeded uniform anchors per file. A positive means an anchor has at least one detected nonexact partner anywhere in the corpus. Wilson intervals apply to the detector-positive rate; unknown recall and anchor dependence limit interpretation. These figures are not counts of all duplicate pairs or precise removable corpus mass. Shorter-than-10-lexical-token anchors are not eligible. Caps/skips, exact matches excluded, verified pair counts and example pairs are recorded per dataset.', '',
      f"The full blank-line block scan found **{r.get('repeated_blocks',{}).get('groups',0):,} repeated block hashes**, including legitimate license text and common declarations. The short QA collections also repeat task families and answers; exact document uniqueness does not imply diverse information. Per-file template and answer statistics are in the JSON.", '',
      '## Actual content and factual review','',
      'Qualitative review covered 128 seeded excerpts across all 10 nonempty files, plus initial peeks and targeted issues. Exact reviewed line references and the sampling algorithms are in `quality_metrics.json.manual_review`. Longer code/web records were reviewed through excerpts, not every full document. This review cannot estimate a corpus-wide factual-error rate.', '',
      'The general QA collection covers arithmetic, date arithmetic, formatting, short transformations and simple Python tasks. Its narrow validators checked 1,210 integer arithmetic answers, 240 weekdays and 413 literal JSON arrays, with no mismatches. All other answers remain outside these validators. The Gren examples checked against official core 7.0.0 String and Dict documentation were plausible; other modules and compilability remain unverified. The ML/AI examples include sensible caveats around top-k ties, mean loss reduction, mixed precision and deterministic splits, but no runtime/semantic certification was performed.', '',
      'Selected meaningful defects include a historical contradiction in FineWeb line 9111, navigation at 2977, product/catalogue boilerplate at 3557 and 7119, flattened Python at 692, degraded superscripts at 3010, and a mid-sentence opening at 11978. These support targeted review, not a claim that the whole web file is unusable. The structured synthetic style of curated collections is visible, but the audit cannot establish their generating model or authorship.', '',
      '## Tokenizer suitability','',
      '**No trained tokenizer model or vocabulary artifact was found.** Round-trip fidelity, unknown/fallback rates, identifier fragmentation, compression and actual token counts therefore could not be measured. Installing SentencePiece does not supply a Peregrine tokenizer. The audit did not train one.', '',
      'The available JSONL payloads offer useful natural English, educational/scientific vocabulary, the five code languages, indentation and some mathematics/Unicode. They can support an initial 32K tokenizer experiment after provenance, privacy and representative sampling decisions. Tokenizer readiness remains unproven: educational English dominates the prose; long-form diverse writing, rigorous mathematical notation, additional code languages and rare Unicode need deliberate holdouts and possibly additional sources. Character tables in the JSON describe coverage, not compression.', '',
      '`src/tokenizer/tokenizer.py` requests BPE, 32,000 pieces, byte fallback, identity normalization, 0.9995 character coverage and `remove_extra_whitespaces=False`. `hard_vocab_limit=False` permits fewer than 32,000 pieces. These settings are not round-trip test results. Test spaces, tabs, LF, CRLF, blank lines, trailing whitespace, literal U+2581, emoji and mathematical text after a model exists. The line-based text input also needs explicit handling for document/newline representation.', '',
      '`src/tokenizer/peregrine_tokenizer_starter.txt` is the configured input and contains repeated prose variants and recurring code structures. The C++ extract is a separate input and is not referenced by the trainer. Its Windows newline expansion and concatenated boundaries are confirmed by whole-file hashes; see `tokenizer.cpp_extract_check`. Do not use either uncritically as the final representative training corpus.', '',
      '| Existing plain-text tokenizer input | Bytes | Nonempty lines / distinct normalized lines | Longest line bytes | Lines >4192 bytes |',
      '|---|---:|---|---:|---:|']
    for x in r['tokenizer']['plain_text_inputs']:
        a=x.get('normalized_nonempty_line_repetition',{});lines.append(f"| `{x['path']}` | {x['bytes']:,} | {a.get('nonempty_lines')} / {a.get('distinct')} | {x.get('line_bytes_max')} | {x.get('lines_over_default_sentencepiece_max_sentence_length_4192_bytes')} |")
    lines+=['','Repeated braces and ordinary syntax naturally inflate line-duplicate statistics; the starter review additionally found repeated semantic prose variants. A future trainer must account for its maximum input sentence length rather than silently losing long source lines. [SentencePiece options](https://github.com/google/sentencepiece/blob/master/doc/options.md) describe the relevant controls.', '',
      '## Pretraining stages and experimental scale','',
      f"The five code datasets provide {code_chars:,} decoded characters (roughly {code_chars/5/1e6:.2f}–{code_chars/3/1e6:.2f}M heuristic tokens); FineWeb provides {web.get('text_chars',0):,} characters (roughly {web.get('text_chars',0)/5/1e6:.2f}–{web.get('text_chars',0)/3/1e6:.2f}M). These are the primary coding and general pools. Curated QA should be held separately for SFT; the 502-record technical text file is a small supplement, not a broad scientific corpus.", '',
      'The repository has no usable token-budget/model-size experiment configuration: `src/main.py`, compute-budget, methodology, dataset-strategy, roadmap, decisions and research-question documents are empty. The README describes small experiments and an eventual 14B model. The present unique text is enough for tokenizer/data-loader pilots and deliberately data-limited tiny experiments; it is far too little to support a high-quality 14B foundation model from scratch. Repeated epochs do not create new information. A specific experimental sufficiency decision requires parameter count, unique-token budget, epochs, mixture and held-out tasks.', '',
      'As scale context only, 20 tokens per parameter would be 10B tokens for 500M parameters and 280B for 14B—hundreds to thousands of times this corpus. This is an illustrative rule of thumb, not a mandatory budget or a quality guarantee; [Hoffmann et al.](https://arxiv.org/abs/2203.15556) studied joint parameter/data scaling.', '',
      'Files are separated by directory, but no active MaxText loader was found to verify actual stage mixing. Recursive loading of all JSONL would mix source code, plain text and QA and would silently change the curriculum. General QA contains Python examples, and the ML/AI text contains code fences; these are expected mixed-content supplements, not evidence that the general collector accidentally appended a code dataset. The general collector references Wikipedia, but **no local Wikipedia JSONL exists**.', '',
      '## Privacy, rights and evaluation boundaries','',
      f"Full extracted-text regex scans returned these **record-level candidates**, not confirmed exposures: `{j(dict(total_priv))}`. Pattern families overlap. Complete matched credentials, email addresses, phone-like numbers and private-key bodies are not included in reports. Context classifications and redacted record references are in the JSON. Unknown/obfuscated formats and arbitrary PII may be missed; no remote credential checks were made.", '',
      'All nonempty JSONL schemas lack explicit source URL/repository path/revision/license/generator metadata. Collector code suggests FineWeb-Edu and The Stack-dedup, but it is not a signed acquisition manifest and drops upstream metadata. The Stack requires attention to original licenses and attribution, version/removal handling, and redistribution terms; its card acknowledges license-detector errors. FineWeb-Edu declares ODC-By and Common Crawl terms. The project Apache-2.0 license does not automatically relicense collected documents. Curated/synthetic origins and generating-model terms remain unknown. License headers are hints for review, not legal determinations. [The Stack card](https://huggingface.co/datasets/bigcode/the-stack-dedup/blob/main/README.md), [FineWeb-Edu card](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu/blob/main/README.md).', '',
      'No local evaluation/validation JSONL or split metadata was found, and no external benchmark corpora were supplied. Keyword references were scanned, but **benchmark decontamination was not performed**. Repeated templates and source families can contaminate future random record splits even without exact duplicates. Treat benchmark cleanliness as unknown. Pin independent evaluation sources first, then compare hashes, normalized prompts, long shared substrings and source/task groups before training.', '',
      '## Reproduction and limitations','',
      'Run from the project root:', '',
      '```powershell', 'python reports/dataset_audit/audit.py', '```', '',
      'If `python` resolves to the inert Windows system entry, invoke the installed Python executable directly. The scan uses the standard library; an already-installed NumPy accelerates signatures and is optional. SentencePiece is only used if an existing `.model` is found. No package installation is needed here. Progress is printed by file/record count with no training text.', '',
      'Full-corpus tests: discovery, raw SHA-256/size, strict parsing, field/schema/null/empty counts, decoded-text lengths/Unicode, heuristic content/code/privacy/license signals, exact/whitespace document hashes, normalized QA component hashes, numeric/quoted-literal template hashes, blank-line block hashes and narrow QA validators. Sampled tests: near-duplicate anchors and qualitative excerpt review. Unperformed tests: full semantic verification, general language identification, all-language compilation, execution, exhaustive PII/legal review, external benchmark matching and model tokenization.', '',
      'No heuristic signal alone authorizes deletion. See `issues.md` for severity and examples, `recommendations.md` for the ordered work plan, `dataset_inventory.csv` for every file, and `quality_metrics.json` for full definitions, counts, source fingerprints, references and limitations.', '']
    bad=r.get('targeted_content_review',{}).get('javascript_binary_like_record',{})
    if bad:
        lines+=['## Targeted follow-up findings','',
          f"`datasets/code/javascript.jsonl:1525` is a **strong source-training exclusion candidate**: {bad['chars']:,} decoded characters include {bad['replacement_characters']:,} U+FFFD replacement characters and {bad['unusual_control_characters']:,} unusual controls. A JavaScript bundle wrapper and source-map reference surround a binary-like payload; this is materially different from ordinary source syntax or a few deliberate control-character tests. The wrapper was not compiled and is not claimed to be syntactically invalid. This record is only {pct(bad['chars'],by['datasets/code/javascript.jsonl']['text_chars'])} of JavaScript character mass; do not generalize it to the entire file.", '',
          'Sensitive-context review found two RSA key blocks in Python line 630 in apparent unit-test fixtures; the AWS-shaped value in Python line 1952 is explicitly an example, and the Google-key-shaped identifier at 1675 is named `_CELLSET_ID`. Java line 2951 and JavaScript lines 351, 450, 1252, 1971 and 2024 contain Google-service/API-key-shaped values worth provenance/restriction review. **No live credential exposure was established.** Public attribution emails and test/private-network IPs also occur; regex totals are not a count of confirmed privacy violations.', '',
          f"The full normalized QA consistency check found **{r['qa_consistency']['conflicting_question_groups']}** repeated-question groups with differing normalized answers. Different wording or differently expressed equivalent answers are beyond this check. The largest QA collection accounts for {pct(qa['parsed_records'],t['parsed_records'])} of records but only {pct(qa['text_chars'],t['text_chars'])} of decoded characters, illustrating why record-weighted tokenizer sampling would overrepresent short synthetic tasks.", '']
    (out/'summary.md').write_text('\n'.join(lines),encoding='utf-8')

    issues=['# Findings ranked by severity','',
      'Severity reflects impact if the material were used unchanged. Candidate matches are explicitly distinguished from confirmed defects. All references are 1-based JSONL lines; sensitive values are redacted.', '',
      '## High — sensitive material and unresolved code rights','',
      'Review private-key/token/credential candidates before admitting affected source groups to a training manifest. Test keys and placeholders may be deliberate fixtures; a pattern match does not establish a live credential. No key or token was tested against a service. Excerpts are omitted for these findings.', '',
      '| Dataset | Private-key records | Known-token-pattern records | Credential-assignment records | Email-like records | Confidentiality markers |',
      '|---|---:|---:|---:|---:|---:|']
    for s in data:
        p=s['privacy'];issues.append(f"| `{s['path']}` | {p.get('private_key_block',0)} | {p.get('known_token_pattern',0)} | {p.get('credential_assignment',0)} | {p.get('email_like',0)} | {stat(s,'confidentiality_marker')} |")
    issues+=['','Examples of sensitive-pattern references:','']
    for s in data:
        for kind in ['private_key_block','known_token_pattern','credential_assignment']:
            rows=s['privacy_refs'].get(kind,[])
            if rows:issues.append(f"- `{s['path']}` — {kind}, lines {', '.join(str(x['line']) for x in rows)}: **[REDACTED]**.")
    issues+=['','The code files contain only `text` and `language`: no repository IDs, paths, revisions, SPDX licenses, acquisition revision or opt-out trail. FineWeb contains only `text`; curated collections contain only text or QA. Recover provenance in a sidecar manifest. At `datasets/code/javascript.jsonl:81` the header explicitly says **Elastic License**; this warrants rights review rather than assuming an upstream permissive filter is infallible. GPL-family headers and other notices are counted below. Header matches do not establish the effective license or a legal prohibition on training. The root Apache license does not settle these questions.', '',
      '| Dataset | Header/license hints by family (overlap possible) |', '|---|---|']
    for s in code:issues.append(f"| `{s['path']}` | `{j(s['license_hints'])}` |")
    issues+=['','**Context qualification:** Python line 630 contains two apparently deliberate RSA unit-test fixtures, not a demonstrated live deployment key. Python line 1952 explicitly labels its AWS-shaped string as an example. Python line 1675 assigns a Google-key-shaped identifier to `_CELLSET_ID`, so it may be a noncredential identifier. Java line 2951 uses a hardcoded Google geocoding key variable; the five JavaScript token-pattern records use Google/Firebase service URLs or configuration. Their validity and access restrictions are unknown. Do not conflate these categories or automatically delete useful cryptographic test source. No live credential exposure was confirmed.','',
      '## High — corpus scale and stage control','',
      f"All JSONL training fields together yield only {t['rough_tokens']['low']/1e6:.2f}–{t['rough_tokens']['high']/1e6:.2f}M **rough** tokens before eligibility decisions. Only one natural-language web file is present. The 32,180-record general QA collection is not a broad general pretraining corpus. No independent evaluation split or nonempty budget/mixture configuration exists. This is a material limitation for the intended high-quality from-scratch model, while permitting deliberately small pilots.", '',
      'A recursive `text`-only loader would ignore QA; a loader concatenating arbitrary fields could train on questions/answers without an intentional SFT policy. Directory naming alone does not enforce the general→code curriculum. No active loader exists here to demonstrate an accidental mix, so accidental mixing is a **risk**, not a confirmed training event.', '',
      '## High — configured tokenizer input is unrepresentative; C++ extraction changes structure','',
      'The trainer reads only the 654,873-byte starter, not the full audited text/code pools. The starter opens with repeated variants of the same astronomy paragraph, followed by similarly regular study-note and code patterns. Examples of recurring source lines occur 54 times; repeated braces alone are expected. This biases frequency learning toward a small designed sample. No trained model exists to establish actual damage or vocabulary efficiency.', '',
      'Whole-file hashes confirm `extracted_texts.txt` is exactly the C++ text concatenation after `LF → CRLF` expansion. It is not byte-identical to the decoded source. The 38,585 original CRLF sequences become CRCRLF. There are 214 C++ records without a terminal newline; the helper inserts no record separator. These defects affect the derivative tokenizer input, not the intact code JSONL. `tokenizer_dataset.py` opens a normal Windows text stream and writes `text_content` directly.', '',
      '## Medium — binary-like asset payload in a JavaScript bundle','',
      f"`datasets/code/javascript.jsonl:1525` contains {bad.get('chars',0):,} decoded characters, including {bad.get('replacement_characters',0):,} U+FFFD characters and {bad.get('unusual_control_characters',0):,} unusual controls. It has a JavaScript bundle wrapper and a source-map reference around a binary-like payload, so a source-language cue alone does not establish useful source content. The payload appears lossy or binary-like; no claim is made that the wrapper fails JavaScript parsing. Retain the immutable original but review/exclude this record from a future source-code/tokenizer manifest unless that asset representation is wanted. It affects approximately {pct(bad.get('chars',0),by['datasets/code/javascript.jsonl']['text_chars'])} of JavaScript character mass.",'',
      'Contrast legitimate controls: JavaScript line 1609 maps DEL/ESC key codes; Rust line 234 intentionally tests malformed input, line 1292 documents U+FFFD encoding, and line 2016 explains replacement-character semantics. These are acceptable code/test cases and should not be discarded merely for sharing a Unicode flag. C++ line 1274 and several Java/FineWeb examples show likely lost text in comments or prose, a smaller and more localized problem.','',
      '## Medium — narrow synthetic distributions and future split leakage','',
      '| QA file | Records | Distinct normalized question templates | Distinct answers | Repeated answer occurrences |',
      '|---|---:|---:|---:|---:|']
    for s in data:
        if s['formats'].get('instruction_pair'):
            a=s.get('component_duplicates',{}).get('answer',{})
            issues.append(f"| `{s['path']}` | {s['parsed_records']} | {s['question_template_groups']['distinct']} | {a.get('distinct',0)} | {a.get('redundant_records',0)} |")
    issues+=['','Template collapse deliberately hides numbers and quoted/code spans; it diagnoses repeated structure, not semantic equivalence. For example, general line 18448 asks `438 + 700` and correctly answers `1138`; a different pair of operands remains a useful different task. Gren line 457 uses a repeated API-description phrasing. Repeated short correct answers such as numbers, booleans and weekdays are normal. The harm comes from overweighting these families and leaking nearly identical task generators into evaluation, not from shortness alone.', '',
      '## Medium — selected web factual, formatting and extraction defects','',
      '- `datasets/general/fineweb.jsonl:9111`: claims Cyrus and Darius invaded northwest India together in **520 BC**. The British Museum dates Cyrus’s reign to **559–530 BC**, contradicting that joint date. This is one confirmed contradiction, not a measured factual-error rate. [Museum description](https://artsandculture.google.com/asset/cyrus-cylinder/4wHjbQnYhZgzVQ?hl=en).',
      '- `fineweb.jsonl:2977`: starts `Sign In / Sign Out` and `Navigation for Entire University` before useful sediment/rock material. The navigation is removable boilerplate in a future derived view; the geology content is not thereby worthless.',
      '- `fineweb.jsonl:3557`: lesson-plan catalogue with access prompts, view/download counts and unrelated suggested lessons; `:7119` advertises a printable teaching product. Educational-topic scoring does not guarantee substantive document quality.',
      '- `fineweb.jsonl:692`: `os.pipe()` tutorial has Python 2 code flattened into prose (`os.close(w) r = os.fdopen(r) print ...`). This teaches poor code formatting if admitted as a coding example; an English educational page may still retain some value.',
      '- `fineweb.jsonl:3010`: mathematical powers appear as flattened `x5`, `x-3` and `x8`, creating ambiguity with identifiers or subtraction. Some text formats use this convention, so review rather than deleting every such page.',
      '- `fineweb.jsonl:8088`: instructions require listening to omitted audio examples; `:862` asks the reader to inspect an unavailable image; `:11978` begins mid-sentence. These are incomplete or modality-dependent examples, not invalid JSON.',
      '- `fineweb.jsonl:81`: explains CT absorption solely using atomic “size”; flag for technical review as an oversimplification. This audit did not independently certify all medical claims and is not using that example to estimate prevalence.', '',
      'Representative positive controls: general lines 739, 2382, 3125, 3480, 3776, 5147 and 19977 are consistent with their arithmetic/date/format tasks in manual review. Narrow mechanical tests found no mismatches in their recognized subset. ML/AI line 96 explicitly notes that top-k ties can retain more than k elements; line 66 acknowledges that its optimizer example is not an AMP/distributed recipe. Gren String.count, String.replace, String.split and Dict operations were checked selectively against official core 7.0.0 docs. No claim is made that every technical explanation or citation was verified. [String](https://packages.gren-lang.org/package/gren-lang/core/version/7.0.0/module/String), [Dict](https://packages.gren-lang.org/package/gren-lang/core/version/7.0.0/module/Dict).', '',
      '## Medium — generated, bundled, obfuscated and historical code','',
      '| Dataset | Generated cues | Vendor/bundle cues | Lock/build cues | >80% comment-like lines | Minified/large-line candidates | Missing expected source cue |',
      '|---|---:|---:|---:|---:|---:|---:|']
    for s in code:issues.append(f"| `{s['path']}` | {stat(s,'generated_code')} | {stat(s,'vendor_or_bundle')} | {stat(s,'lock_or_build')} | {stat(s,'over_80pct_comment_like_lines')} | {stat(s,'minified_or_large_single_line')} | {stat(s,'no_expected_language_cue')} |")
    issues+=['','- `datasets/code/javascript.jsonl:2218`: 24,971-character krpano plugin record dominated by an encoded/obfuscated string. Low source-learning value and an unresolved source/license context make it a strong review candidate.',
      '- `datasets/code/rust.jsonl:2002`: uses `extern mod`, `~str` and `ret`, clearly historical Rust syntax. Such source is real code; contemporary compiler failure would not imply storage corruption. Downweight only if the target is modern Rust.',
      '- `datasets/code/python.jsonl:457`: includes `Tkinter`, `tkFileDialog` and a `raw_input` comment; other records contain Python 2 syntax. Keep language-version context when interpreting AST rejection.',
      '- `datasets/code/java.jsonl:278`: a 133-character empty entity class is a legitimate short source file. `python.jsonl:685` contains small exception definitions. Neither should be removed by a blanket length rule.',
      '- `datasets/code/rust.jsonl:81`: standard-library iterator implementation with substantial documentation. Repeated libraries and generated register interfaces can dominate a small coding corpus, but source context and comments can be useful.', '',
      'In the full JavaScript scan, 135 minified/large-line candidate records account for **4,132,861 decoded characters (20.78%)**. Vendor/bundle cues cover 16.25% and generated cues 17.01% of JavaScript characters; these sets overlap. Generated cues cover 20.96% of Rust characters. This is a meaningful distribution concern in a small code corpus, not proof that all flagged source is useless. Full per-file candidate character masses are in the JSON and summary.','',
      'Content heuristics can flag strings that merely mention generation, vendor paths or confidential material. Lock/build counts are lower bounds because source paths were discarded; no complete vendored-dependency or artifact classification is possible. Code comment ratios are approximate line-prefix counts and include preprocessor directives in C++, so they do not justify automatic comment removal.', '',
      '## Medium/low — exact/near duplicates, controls and benchmark uncertainty','',
      f"Complete exact redundant records: {exact['redundant_records']}; whitespace-normalized redundant records: {norm['redundant_records']}. Sampled near matches and cross-file examples are in the summary/JSON. Common license blocks and declarations are explicitly separated from document duplication. Preserve required notices even when balancing duplicate source families.", '',
      '| Dataset | Web boilerplate cues | Promotion cues | Repetitive lines (>50%) | Low word diversity | Explicit truncation markers | Benchmark references |',
      '|---|---:|---:|---:|---:|---:|---:|']
    for s in data:issues.append(f"| `{s['path']}` | {stat(s,'web_boilerplate')} | {stat(s,'promotion')} | {stat(s,'over_half_repeated_lines')} | {stat(s,'low_word_diversity')} | {stat(s,'explicit_truncation_marker')} | {stat(s,'benchmark_reference')} |")
    issues+=['','A privacy/copyright banner in code is not scraped navigation; a benchmark name in a technical explanation is not proof of a leaked benchmark item. Keyword absence cannot establish cleanliness. No local evaluation set or external test corpora were available for actual train/eval matching.', '',
      'The JSON records unusual controls, replacement characters, surrogates and mojibake candidates with references. Interpret them in source context: escape-related tests and terminal output are valid code. A final missing newline, external imports, a snippet or unbalanced braces in a string do not prove truncation. No blanket sanitization or source deletion was performed.', '',
      '## Low — empty/prototype files','',
      '`src/dataset_generator/code.jsonl` is empty: **NOT SUITABLE** as training data. `src/dataset_generator/general.jsonl` has two plausible QA examples, useful only as a prototype pending origin/rights and SFT validation. Neither meaningfully expands the pretraining pool.', '']
    (out/'issues.md').write_text('\n'.join(issues),encoding='utf-8')

    rec=['# Prioritized recommendations','',
      'These are proposed next steps. The audit performed none of the preprocessing, exclusion, acquisition, training, or retraining actions below. Preserve source files and implement later decisions as versioned manifests/derived artifacts.', '',
      '## 1. Resolve sensitive candidates and provenance before a production run','',
      'Review private-key blocks, recognized-token patterns and nontrivial credential assignments at the redacted references in `quality_metrics.json`. Classify test fixtures/placeholders versus material that needs removal from the eligible training view. Keep any sensitive review local; do not validate credentials against remote services. A regex hit alone does not justify rotating an owner’s key or rejecting a whole dataset.', '',
      'Recover source dataset revision, repository/path/commit or source URL, license evidence, attribution requirements, acquisition date and removal/opt-out status into a separate sidecar keyed by document hash. Review the Elastic-license and GPL-family header candidates. Record the curated datasets’ authorship, generating model/version, generation settings, validation and applicable terms. The repository license does not settle acquired-data permissions. This is the first production eligibility gate.', '',
      '## 2. Define frozen general, code, SFT and evaluation manifests','',
      'Use FineWeb as the primary general pool and the five language-labeled source datasets as the coding pool after eligibility review. Keep the 32,180 general QA pairs, Gren QA and generator examples in a separate SFT pool. Admit the ML/AI text as a small explicitly weighted supplement if reviewed; it contains QA headings and code. Specify schema adapters and whether input/prompt loss is masked for SFT. Do not infer stage membership from a recursive glob alone.', '',
      'Pin independent evaluation sources and keep them out of both tokenizer training and model-training pools where practical. Split by repository/source/document and synthetic task family, not just rows. Compare exact/normalized hashes, long matching substrings and near duplicates to actual benchmark versions. Preserve all identified overlap as an auditable manifest decision rather than editing originals.', '',
      '## 3. Repair the proposed tokenizer input pipeline before training a model','',
      'Design a representative sample weighted by decoded character/token mass and intended training mixture, not record count. Cap repeated source/template families without removing normal code syntax. Include natural long-form English, science/technical text, mathematics/LaTeX, all five existing code languages and any additional languages Peregrine is expected to support.', '',
      'Replace the C++-only derivative-input approach in a future implementation: preserve LF, CRLF, tabs, blank lines and trailing whitespace explicitly, prevent document-boundary fusion, and avoid Windows text newline expansion. The configured starter is too small and templated to establish a production vocabulary distribution. Decide how a line-based SentencePiece input represents newlines/documents and handle lines exceeding the trainer’s configured maximum length.', '',
      'Before freezing a 32K tokenizer, run byte-for-byte encode→decode probes and held-out corpus tests for each language and topic. Measure tokens/UTF-8 byte, bytes/token, unknown and byte-fallback rates, identifier fragmentation, indentation cost, math/Unicode cost, achieved vocabulary size and vocabulary stability across samples. Include spaces/tabs/LF/CRLF, empty/blank lines, emoji, combining marks and literal U+2581. Set acceptance criteria by intended use and compare against a reference tokenizer. No trained Peregrine model exists here to evaluate yet.', '',
      '## 4. Improve distribution and selected content, with conservative review','',
      'Review FineWeb navigation/catalogues and pages with missing code/math/audio/image context. The named factual contradiction warrants source-level review; a few such pages do not justify discarding all educational text. Prefer better extraction or source-aware eligibility rules for future acquisitions. Do not globally strip Unicode, math symbols, comments, headers, short records, tests or incomplete but useful snippets.', '',
      'Prioritize the corrupted/binary-like `datasets/code/javascript.jsonl:1525` for exclusion from a future derived training manifest. Preserve legitimate control-character fixtures, including JavaScript key-code tables and Rust Unicode decoder tests. Treat the separate obfuscated plugin at line 2218 as its own review decision.', '',
      'Limit obfuscated JS, repetitive generated bindings and duplicated library families when they consume a disproportionate training share. Keep examples needed for the intended tasks. Identify source/revision and language era rather than labeling Python 2 or historical Rust as corrupt. Python AST failures need classification, not automatic rejection; validate executable SFT code in isolated pinned environments only as a separately authorized future task.', '',
      'General QA is useful for short task execution but narrow as knowledge pretraining. Add validated diverse multi-turn SFT and non-template instruction tasks if conversational behavior is a goal. Pin Gren/compiler/package versions and compile representative examples later; String/Dict spot checks cannot validate every module. Maintain factual review by topic and risk, with explicit pass/fail evidence rather than trusting synthetic fluency.', '',
      '## 5. Expand unique text to a stated experimental budget','',
      f"Current corpus: {t['rough_tokens']['low']/1e6:.2f}–{t['rough_tokens']['high']/1e6:.2f}M rough tokens before exclusions, with no model-token counts. Write the model parameter count, unique-token target, total tokens/epochs, general/code ratio and stage boundaries into the presently empty strategy/budget/methodology documents before deciding this is sufficient. Keep small loader/tokenizer pilots separate from claims about a capable 14B foundation model.", '',
      'Collect broader independently sourced natural writing and technical/math material with retained metadata. Add code languages according to intended capability rather than treating five balanced byte quotas as universal language coverage. The collector takes the first accepted streaming records, so use a reproducible upstream shuffle/stratified acquisition strategy in a future dataset version; this audit did not verify that the existing prefix is representative of its upstream source.', '',
      'For sequential-vs-mixed experiments, keep the **same frozen eligible document pool, tokenizer, actual total token budget, evaluation tasks and seed policy** across schedules. Log stage-specific language/token distributions and repeated exposure counts. Use multiple seeds and held-out loss/behavior; otherwise data selection or repeated-template exposure can masquerade as a curriculum effect.', '',
      '## Audit operation','',
      'Rerun `audit.py` after new acquisitions. Every run must discover files again, hash sources, report full versus sampled coverage, preserve source bytes and report privacy candidates only with redaction. Review new datasets rather than treating this snapshot’s qualitative conclusions as permanent certification. The optional SQLite index contains hashes/signatures/offsets only and is temporary unless `--keep-index` is used. Reports and their line references should be versioned with the acquisition manifest.', '']
    (out/'recommendations.md').write_text('\n'.join(rec),encoding='utf-8')

def write_generic_reports(out,r):
    """A changed corpus must never inherit this snapshot's manual conclusions."""
    lines=['# Dataset audit — automated results for a changed corpus','',
           '**New qualitative review is required.** The October 23, 2026 manually reviewed fingerprints do not match this corpus. Prior line-specific findings and factual checks are intentionally withheld.','',
           f"Files: {r['totals']['jsonl_files']}; parsed records: {r['totals']['parsed_records']}; invalid: {r['totals']['invalid_records']}.",'',
           '| Dataset | Bytes | Parsed | Invalid | Provisional verdict | Intended use |','|---|---:|---:|---:|---|---|']
    for s in r['datasets']:
        lines.append(f"| `{s['path']}` | {s['bytes']} | {s['parsed_records']} | {s['invalid_records']} | {s['verdict']} | {s['intended_use']} |")
    lines+=['','Machine metrics, exact duplicate coverage, sampled near coverage, privacy limitations and source integrity are recorded in `quality_metrics.json`. Rough token estimates are character heuristics, not tokenizer counts. Automated verdicts do not certify quality, rights or safety.','']
    (out/'summary.md').write_text('\n'.join(lines),encoding='utf-8')
    lines=['# Automated findings — manual review pending','']
    for s in r['datasets']:
        lines.extend([f"## {s['path']}",'',f"Invalid: {s['invalid_records']}; signals: `{json.dumps(s['signals'])}`; sensitive candidates: `{json.dumps(s['privacy'])}`.",'',
                      'See redacted line references in the JSON; candidate counts do not establish confirmed exposures.',''])
    (out/'issues.md').write_text('\n'.join(lines),encoding='utf-8')
    (out/'recommendations.md').write_text('# Recommendations\n\nReview the changed corpus before training. Resolve sensitive candidates and provenance, define stage-specific and independent evaluation manifests, classify duplicates and quality flags in context, and test the actual tokenizer if present. Do not delete source documents based only on heuristics. Prioritize severe parsing, schema and safety issues, then distribution and scale.\n',encoding='utf-8')

def finalize_reports(root,out,report,keep_index=False,render_only=False):
    if render_only and not (out/'audit_index.sqlite').is_file():
        raise SystemExit('Temporary index was removed; run a new full audit to rebuild it.')
    actual_paths={p.relative_to(root).as_posix() for p in walk_jsonl(root,out)}
    if actual_paths!={s['path'] for s in report['datasets']}:
        raise SystemExit('Source inventory changed; run a fresh full audit.')
    for st in report['datasets']:
        p=root/st['path'];h=hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        if h.hexdigest()!=st['sha256_before'] or p.stat().st_size!=st['bytes']:
            raise SystemExit('Source changed; run a fresh full audit: '+st['path'])
    if not render_only:
        report=supplemental_checks(root,out,report)
    report=refine_results(root,out,report)
    report['audit']['final_report_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['audit']['reports_finalized_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    report['audit']['temporary_index_retained']=keep_index
    write_reports(out,report);save_metrics(out,report);write_inventory(out,report['datasets'])
    if not keep_index:
        p=(out/'audit_index.sqlite').resolve()
        if p.parent!=out.resolve() or p.name!='audit_index.sqlite':
            raise SystemExit('Refusing cache removal outside audit output directory')
        p.unlink(missing_ok=True)
    print('REPORTS complete; '+('hash-only index retained' if keep_index else 'temporary hash-only index removed'),flush=True)

def full_audit(root,out,anchors,skip_near=False):
    started=dt.datetime.now(dt.timezone.utc)
    out.mkdir(parents=True,exist_ok=True)
    paths=sorted(walk_jsonl(root,out))
    print(f'DISCOVERY {len(paths)} JSONL files, {sum(p.stat().st_size for p in paths):,} bytes; seed={SEED}; numpy_acceleration={np is not None}',flush=True)
    db=init_db(out);stats=[]
    for i,path in enumerate(paths):
        stats.append(scan_file(path,root,db,i,anchors))
    print('INDEX creating disk-backed hash and LSH indexes',flush=True)
    db.executescript('CREATE INDEX exact_idx ON docs(exact); CREATE INDEX norm_idx ON docs(norm); CREATE INDEX band_idx ON bands(band,value); CREATE INDEX file_idx ON docs(file_id); CREATE INDEX template_idx ON templates(file_id,hash); CREATE INDEX component_idx ON components(file_id,role,hash);')
    duplicate=duplicate_metrics(db,stats)
    for st in stats:
        if st['formats'].get('instruction_pair'):
            st['deterministic_qa_checks']=verify_simple_qa(root/st['path'])
        st['intended_use']=stage(st);st['verdict']=verdict(st)
    report={'audit':{'started_utc':started.isoformat(),'client_date':'2026-10-23','client_timezone':'America/Phoenix','seed':SEED,'python':sys.version,
        'numpy_acceleration':np is not None,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_mutation_policy':'All JSONL source handles rb only; final SHA-256 and size/mtime compared against streaming scan. Writes confined to report directory.',
        'exact_coverage':'Every nonblank physical line of every discovered JSONL, strict UTF-8 and strict JSON. Duplicate keys and nonfinite numbers rejected. Complete extracted-document SHA-256 and case-sensitive whitespace-normalized hashes, within and across datasets. No casefold, Unicode normalization, translation or identifier renaming in exact dedup.',
        'privacy_limitations':'Regex candidate scan of every extracted text. Pattern matches are not confirmed secrets/PII; arbitrary names, addresses, confidential data, obfuscated credentials and unrecognized token formats may be missed. Stored examples omit matched values. No remote credential validation.',
        'content_limitations':'Full streaming heuristics plus reproducibly sampled manual review. Quality proxies are not deletion decisions. No code execution; Python3 AST syntax only. Other languages not compiled. No semantic proof or complete fact verification.',
        'near_status':'pending' if not skip_near else 'explicitly skipped'},
        'totals':{'jsonl_files':len(paths),'file_bytes':sum(s['bytes'] for s in stats),'parsed_records':sum(s['parsed_records'] for s in stats),
                  'invalid_records':sum(s['invalid_records'] for s in stats),'text_chars':sum(s['text_chars'] for s in stats),'text_utf8_bytes':sum(s['text_utf8_bytes'] for s in stats)},
        'duplicates':duplicate,'datasets':stats,'tokenizer':profile_tokenizer_inputs(root)}
    save_metrics(out,report)
    if not skip_near:
        report['near_duplicates']=near_scan(db,stats,root)
        report['audit']['near_status']='completed sampled anchor search against full corpus index'
    print('INTEGRITY rehashing every JSONL source',flush=True)
    for path,st in zip(paths,stats):
        h=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        st['sha256_after']=h.hexdigest()
        st['unchanged_after_audit']=st['sha256_before']==h.hexdigest() and path.stat().st_size==st['bytes'] and path.stat().st_mtime_ns==st['mtime_ns_before']
    report['audit']['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    report['audit']['all_source_files_unchanged']=all(s['unchanged_after_audit'] for s in stats)
    report['totals']['rough_tokens']={x:sum(s['estimated_tokens'][x] for s in stats) for x in ['low','mid','high']}
    save_metrics(out,report);write_inventory(out,stats)
    db.close()
    print(f"COMPLETE files={len(paths)}, records={report['totals']['parsed_records']:,}, unchanged={report['audit']['all_source_files_unchanged']}",flush=True)
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--out', type=Path)
    parser.add_argument('--peek', action='store_true')
    parser.add_argument('--anchors',type=int,default=400,help='Uniform random near-duplicate anchors per dataset; full hash scans always complete')
    parser.add_argument('--skip-near',action='store_true',help='Explicitly skip near scan; marked in metrics')
    parser.add_argument('--finalize',action='store_true',help='Finalize reports from an existing complete scan and retained hash index; validates all source fingerprints')
    parser.add_argument('--keep-index',action='store_true',help='Retain temporary hash-only SQLite cache for inspection')
    parser.add_argument('--render-only',action='store_true',help='Validate sources and rerender an already completed supplementary scan')
    args = parser.parse_args()
    root = args.root.resolve()
    out = (args.out or root / 'reports/dataset_audit').resolve()
    if args.peek:
        peek(root, out)
    else:
        if out!=(root/'reports/dataset_audit').resolve():
            raise SystemExit('All audit writes must remain in root/reports/dataset_audit')
        if args.anchors<1:raise SystemExit('--anchors must be positive')
        if args.finalize or args.render_only:
            report=json.loads((out/'quality_metrics.json').read_text(encoding='utf-8'))
            if not report['audit'].get('finished_utc'):
                raise SystemExit('The core scan is not complete; cannot finalize partial results')
        else:
            report=full_audit(root,out,args.anchors,args.skip_near)
        finalize_reports(root,out,report,args.keep_index,args.render_only)

if __name__ == '__main__':
    main()
