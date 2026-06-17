#!/usr/bin/env python3
"""从 Markdown 复习笔记中提取章节结构，生成 Mermaid 思维导图"""

import sys, re, json
from pathlib import Path

def build_tree(md_path):
    """构建章节树"""
    text = Path(md_path).read_text(encoding='utf-8')
    tree = {'title': '', 'children': []}
    current_chapter = None
    current_section = None

    for line in text.split('\n'):
        # h1 = 课程名
        h1 = re.match(r'^#\s+(.+?)(?:\s*·|$)', line)
        if h1:
            tree['title'] = h1.group(1).strip('# ').replace('复习笔记', '').strip()
            continue

        # h2 = 章节 (handles both "第X章 章节名" and "第X章 章节名（X学时）")
        h2 = re.match(r'^##\s+(第[^（(]+)', line)
        if h2:
            name = h2.group(1).strip().replace('· 重点章', '').strip()
            # Extract 重点章 marker
            weight = ' 重点章' if '重点章' in line else ''
            current_chapter = {
                'name': f'{name}{weight}',
                'hours': '',
                'weight': weight,
                'children': []
            }
            tree['children'].append(current_chapter)
            continue

        # h3 = 小节
        if current_chapter:
            h3 = re.match(r'^###\s+(●|○|·)?\s*(.+)', line)
            if h3:
                prefix = h3.group(1) or ''
                name = h3.group(2).strip()
                # 跳过非内容性小节名
                if name in ('大纲要求', '内容要点', '可能的考点', '标记说明'):
                    continue
                icon = '🔴' if prefix == '●' else ('🟡' if prefix == '○' else '')
                current_section = {
                    'name': f'{icon}{name}' if icon else name,
                    'children': []
                }
                current_chapter['children'].append(current_section)

    return tree

def to_mermaid(tree, indent=0):
    """转换为 Mermaid mindmap 格式"""
    lines = ['mindmap']
    title = tree.get('title', '复习笔记')
    lines.append(f'  root(({title}))')

    for ch in tree.get('children', []):
        weight = ch.get('weight', '')
        label = f"{ch['name']}"
        if weight:
            label += f"  [{weight.strip()}]"
        lines.append(f'    {label}')

        for sec in ch.get('children', []):
            lines.append(f'      {sec["name"]}')

    return '\n'.join(lines)

def to_markdown_mermaid(tree):
    """封装为 Markdown 代码块"""
    mermaid = to_mermaid(tree)
    return f'```mermaid\n{mermaid}\n```'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 mindmap.py <复习笔记.md>")
        sys.exit(1)

    tree = build_tree(sys.argv[1])

    if '--json' in sys.argv:
        print(json.dumps(tree, ensure_ascii=False, indent=2))
    else:
        print(to_markdown_mermaid(tree))
