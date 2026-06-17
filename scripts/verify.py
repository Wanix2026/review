#!/usr/bin/env python3
"""提取后完整性自检脚本"""

import sys, os, json
from pathlib import Path

def check_pdf(extracted_text_path, original_size):
    """检查PDF提取完整性"""
    text = Path(extracted_text_path).read_text(encoding='utf-8', errors='replace')
    pages = text.count('\f') + 1
    chars = len(text.replace('\n','').replace(' ',''))

    issues = []
    if pages == 0:
        issues.append(('critical', '提取文本为0页'))
    if chars < 100:
        issues.append(('critical', f'提取文字过少: {chars}字符'))
    elif chars < 500:
        issues.append(('warning', f'提取文字较少: {chars}字符，可能为扫描件'))

    # 乱码检测
    total = len(text)
    non_printable = sum(1 for c in text if c.isprintable() or c in '\n\r\t\f')
    if total > 0 and non_printable / total < 0.7:
        issues.append(('critical', f'疑似乱码: 可打印字符仅{non_printable/total:.0%}'))

    return {
        'type': 'pdf',
        'pages': pages,
        'chars': chars,
        'issues': issues,
        'pass': not any(i[0] == 'critical' for i in issues)
    }

def check_pptx(extracted_text_path, slide_warnings):
    """检查PPTX提取完整性"""
    text = Path(extracted_text_path).read_text(encoding='utf-8', errors='replace')
    slides = text.count('--- Slide')
    chars = len(text.replace('\n','').replace(' ',''))

    issues = []
    if slides == 0:
        issues.append(('critical', '提取Slide数为0'))

    for w in slide_warnings:
        issues.append(('warning', w))

    return {
        'type': 'pptx',
        'slides': slides,
        'chars': chars,
        'issues': issues,
        'pass': not any(i[0] == 'critical' for i in issues)
    }

def check_generic(extracted_text_path):
    """通用文本检查"""
    text = Path(extracted_text_path).read_text(encoding='utf-8', errors='replace')
    chars = len(text.replace('\n','').replace(' ',''))

    issues = []
    if chars < 50:
        issues.append(('critical', f'提取文字过少: {chars}字符'))
    if chars < 200:
        issues.append(('warning', f'提取文字偏少: {chars}字符'))

    return {
        'chars': chars,
        'issues': issues,
        'pass': not any(i[0] == 'critical' for i in issues)
    }

def verify_all(manifest_path, extract_dir):
    """验证全部已提取文件"""
    manifest = json.loads(Path(manifest_path).read_text())
    results = {}
    files = manifest.get('files', manifest)  # Support both formats

    for filename, info in files.items():
        if not isinstance(info, dict):
            continue
        if info.get('status') not in ('ok', 'ok_ocr'):
            results[filename] = {'pass': False, 'skip': True, 'reason': info.get('status')}
            continue

        output = info.get('output')
        if not output or not os.path.exists(output):
            results[filename] = {'pass': False, 'skip': True, 'reason': '提取输出文件不存在'}
            continue

        ext = Path(filename).suffix.lower()
        if ext == '.pdf':
            results[filename] = check_pdf(output, info.get('size', 0))
        elif ext in ('.pptx', '.ppt'):
            results[filename] = check_pptx(output, info.get('warnings', []))
        else:
            results[filename] = check_generic(output)

    return results

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 verify.py <manifest.json> <extract_dir>")
        sys.exit(1)

    results = verify_all(sys.argv[1], sys.argv[2])

    total = len(results)
    passed = sum(1 for r in results.values() if r.get('pass') and not r.get('skip'))
    failed = sum(1 for r in results.values() if not r.get('pass') and not r.get('skip'))
    skipped = sum(1 for r in results.values() if r.get('skip'))

    print(f'\n=== 完整性自检结果 ===')
    print(f'总计: {total} | 通过: {passed} | 失败: {failed} | 跳过: {skipped}')
    print()

    for name, r in results.items():
        if r.get('skip'):
            print(f'  ⏭ {name} — {r.get("reason")}')
        elif r.get('pass'):
            print(f'  ✅ {name}')
        else:
            print(f'  ❌ {name}')
            for severity, issue in r.get('issues', []):
                print(f'     [{severity}] {issue}')

    print('\n##RESULT_JSON##')
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
