#!/usr/bin/env python3
"""sanitize_ingest.py — Defensive Prompt Injection & Payload Sanitizer for Bunker OS Ingestion.

Zero external dependencies.
Sanitizes raw ingest content by:
- Stripping zero-width unicode characters and invisible control characters.
- Defanging and neutralizing prompt injection attacks (e.g. "ignore previous instructions", "disregard prior directives", "system prompt:", "assistant override").
- Stripping hidden markdown directives, malicious HTML comments, and dangerous tags (<script>, <iframe>, <object>, etc.).
- Safely escaping nested/malformed wikilinks (`[[...]]`) and payload tags.
"""

import argparse
import html
import os
import re
import sys
from typing import Dict, List, Tuple

# Zero-width & invisible unicode characters (often used for token smuggling/bypasses)
ZERO_WIDTH_PATTERN = re.compile(
    r'[\u200B-\u200D\uFEFF\u200E\u200F\u202A-\u202E\u2060-\u206F\u00AD\u180E\u034F\u061C]'
)

# Common Prompt Injection keywords and adversarial instruction override patterns
INJECTION_PATTERNS = [
    (re.compile(r'(?i)\b(?:ignore|disregard|forget|override|bypass)\s+(?:all\s+)?(?:previous|prior|above|preceding|existing)\s+(?:instructions|prompts|directives|commands|rules|guidelines)\b'), '[SANITIZED_INSTRUCTION_OVERRIDE]'),
    (re.compile(r'(?i)\b(?:system\s*prompt|developer\s*mode|jailbreak|DAN\s*mode|prompt\s*injection)\s*:\s*'), '[SANITIZED_SYSTEM_PROMPT_HEADER]: '),
    (re.compile(r'(?i)\b(?:assistant\s*override|you\s+are\s+now\s+in\s+developer\s+mode|unrestricted\s+mode)\b'), '[SANITIZED_ASSISTANT_OVERRIDE]'),
    (re.compile(r'(?i)\b(?:new\s+system\s+directive|hidden\s+instruction|system\s+instruction)\s*:'), '[SANITIZED_DIRECTIVE]:'),
    (re.compile(r'(?i)<!--\s*(?:system|eval|instruction|override|inject|ignore).*?-->', re.DOTALL), '[SANITIZED_COMMENT]'),
]

# Potentially malicious HTML tags and scripts
DANGEROUS_TAGS = re.compile(
    r'<\s*(?:script|iframe|embed|object|base|link|meta|style|form|input|button|svg|math)[^>]*>.*?<\s*/\s*(?:script|iframe|embed|object|base|link|meta|style|form|input|button|svg|math)\s*>|<\s*(?:script|iframe|embed|object|base|link|meta|style|form|input|button|svg|math)[^>]*/>|<\s*(?:script|iframe|embed|object|base|link|meta|style|form|input|button|svg|math)[^>]*>',
    re.IGNORECASE | re.DOTALL
)

# HTML event handlers like onload=, onerror=
EVENT_HANDLERS = re.compile(r'(?i)\bon\w+\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+)')


def strip_zero_width(text: str) -> Tuple[str, int]:
    """Removes invisible/zero-width unicode characters."""
    matches = len(ZERO_WIDTH_PATTERN.findall(text))
    cleaned = ZERO_WIDTH_PATTERN.sub('', text)
    return cleaned, matches


def sanitize_prompt_injections(text: str) -> Tuple[str, List[str]]:
    """Detects and defangs prompt injection patterns."""
    detected = []
    cleaned = text
    for pat, replacement in INJECTION_PATTERNS:
        found = pat.findall(cleaned)
        if found:
            detected.extend([f.strip() if isinstance(f, str) else "override_pattern" for f in found])
            cleaned = pat.sub(replacement, cleaned)
    return cleaned, detected


def sanitize_html_and_tags(text: str) -> Tuple[str, int]:
    """Strips dangerous HTML tags and script event handlers, and cleans suspicious comments."""
    matches = len(DANGEROUS_TAGS.findall(text))
    cleaned = DANGEROUS_TAGS.sub('[SANITIZED_TAG]', text)
    cleaned = EVENT_HANDLERS.sub('', cleaned)
    return cleaned, matches


def sanitize_wikilinks(text: str) -> Tuple[str, int]:
    """Safely escapes malformed or nested wikilinks to avoid obsidian vault corruption or link-based injection.
    
    Valid: [[Target Note]] or [[Target Note|Custom Alias]]
    Invalid/Suspicious: [[http://...]], [[javascript:...]], [[nested [[wikilink]]]]
    """
    escaped_count = 0

    def replace_wikilink(match):
        nonlocal escaped_count
        inner = match.group(1)
        # Check for nested brackets or suspicious protocols
        if '[[' in inner or ']]' in inner or re.match(r'^(?:https?|javascript|data|file|ftp):', inner.strip(), re.IGNORECASE):
            escaped_count += 1
            return f"\\[\\[{html.escape(inner)}\\]\\]"
        # Check for null bytes or newlines inside wikilinks
        if '\n' in inner or '\r' in inner or '\0' in inner:
            escaped_count += 1
            return f"\\[\\[{inner.replace(chr(10), ' ').replace(chr(13), ' ')}\\]\\]"
        return match.group(0)

    cleaned = re.sub(r'\[\[(.*?)\]\]', replace_wikilink, text)
    return cleaned, escaped_count


def sanitize_document(content: str) -> Dict:
    """Performs full defensive sanitization pipeline on an ingested document string."""
    cleaned, zw_count = strip_zero_width(content)
    cleaned, injections = sanitize_prompt_injections(cleaned)
    cleaned, tag_count = sanitize_html_and_tags(cleaned)
    cleaned, escaped_links = sanitize_wikilinks(cleaned)

    is_suspicious = (zw_count > 0 or len(injections) > 0 or tag_count > 0 or escaped_links > 0)

    return {
        'clean_text': cleaned,
        'is_suspicious': is_suspicious,
        'stats': {
            'zero_width_chars_removed': zw_count,
            'prompt_injections_defanged': len(injections),
            'injection_details': injections,
            'dangerous_tags_removed': tag_count,
            'malformed_links_escaped': escaped_links
        }
    }


def sanitize_file(filepath: str, in_place: bool = False, output_path: str = None) -> Dict:
    """Sanitizes a file on disk."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    result = sanitize_document(content)

    dest = filepath if in_place else (output_path or filepath)
    if in_place or output_path:
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(result['clean_text'])

    result['filepath'] = filepath
    result['output_path'] = dest
    return result


def main():
    parser = argparse.ArgumentParser(description="Sanitize input text/markdown against prompt injections and obfuscations.")
    parser.add_argument("file", nargs="?", default=None, help="File to sanitize (if omitted, reads from stdin)")
    parser.add_argument("--in-place", "-i", action="store_true", help="Modify file in-place")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output JSON report")

    args = parser.parse_args()

    if args.file:
        res = sanitize_file(args.file, in_place=args.in_place, output_path=args.output)
        if args.json:
            import json
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            if not args.in_place and not args.output:
                print(res['clean_text'])
            else:
                print(f"✅ Sanitized {args.file} (Suspicious: {res['is_suspicious']}, Injections: {res['stats']['prompt_injections_defanged']})")
    else:
        content = sys.stdin.read()
        res = sanitize_document(content)
        if args.json:
            import json
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            sys.stdout.write(res['clean_text'])


if __name__ == '__main__':
    main()
