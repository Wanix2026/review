#!/usr/bin/env python3
"""将复习笔记中的关键知识点导出为 Anki 可导入的 CSV 格式"""

import sys, csv, re, json
from pathlib import Path

def extract_cards(md_path):
    """从 Markdown 复习笔记中提取记忆卡"""
    text = Path(md_path).read_text(encoding='utf-8')
    cards = []

    # 当前章节追踪
    current_chapter = ""

    # 规则1: 对比表格 → Basic卡(正面=术语, 背面=定义)
    # 匹配 "| **术语** | 定义 |" 或 "| 术语 | 描述 |"
    table_pattern = r'\|\s*\*{0,2}([^*|]+?)\*{0,2}\s*\|\s*([^|\n]+?)\s*\|'
    in_table = False
    for line in text.split('\n'):
        # 追踪章节
        chap_match = re.match(r'^##\s+(第[^（]+)', line)
        if chap_match:
            current_chapter = chap_match.group(1).strip()

        if '|' in line and '---' not in line:
            match = re.match(table_pattern, line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                # 跳过表头
                if key in ('级别', '对象', '目的', '措施举例', '项目', '内容', '指标', '正常值', ''):
                    continue
                if len(key) > 2 and len(value) > 5:
                    cards.append({
                        'type': 'Basic',
                        'front': f'[{current_chapter}]\n{key}',
                        'back': value,
                        'tags': current_chapter
                    })

    # 规则2: ● 掌握级名词 → Cloze卡
    master_pattern = r'\*\*([^*]+?)\*\*[：:]\s*(.+?)(?=\n|$)'
    for line in text.split('\n'):
        if line.startswith('- **') or line.startswith('* **'):
            match = re.match(master_pattern, line.strip('- *'))
            if match:
                term = match.group(1).strip()
                desc = match.group(2).strip()
                if len(term) > 1 and len(desc) > 5:
                    cards.append({
                        'type': 'Cloze',
                        'front': f'[{current_chapter}]\n{term}',
                        'back': desc,
                        'tags': current_chapter
                    })

    # 规则3: 数值知识点 → Basic卡
    value_pattern = r'\*\*([^*\d]+?)\*\*[：:]\s*[（(]?(\d+[^）)]*?)[）)]?\s*(?:$|，|。)'
    for line in text.split('\n'):
        for match in re.finditer(value_pattern, line):
            term = match.group(1).strip()
            val = match.group(2).strip()
            if len(term) > 1 and val:
                cards.append({
                    'type': 'Basic',
                    'front': f'[{current_chapter}]\n{term}的值/标准是？',
                    'back': val,
                    'tags': current_chapter + ' 数值'
                })

    # 去重
    seen = set()
    unique = []
    for c in cards:
        key = c['front'][:60]
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique

def export_anki(cards, output_path):
    """导出为 Anki CSV 格式"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Anki CSV header: 支持 Basic 和 Cloze 两种类型
        writer.writerow(['Type', 'Front', 'Back', 'Tags'])
        for c in cards:
            writer.writerow([c['type'], c['front'], c['back'], c['tags']])

    print(f'✅ 导出 {len(cards)} 张记忆卡 → {output_path}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 anki.py <复习笔记.md> [output.csv]")
        sys.exit(1)

    md_path = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else Path(md_path).with_suffix('.anki.csv')

    cards = extract_cards(md_path)
    export_anki(cards, str(output))
