#!/usr/bin/env python3
"""从教学大纲中提取与名词解释相关的关键段落，辅助代理提取候选术语"""

import sys, re
from pathlib import Path

def extract_blocks(text):
    """提取所有【XXX】标注的关键段落"""
    blocks = []

    # 1. 独立概念清单
    for kw in ['名词解释', '基本概念', '术语表', '核心概念']:
        m = re.search(rf'{kw}\s*\n(.{{10,2000}}?)(?:\n\s*\n|\n\s*(?:【|第[一二三四五六七八九十\d]+章))', text, re.DOTALL)
        if m:
            blocks.append(('概念清单', kw, m.group(1).strip()[:2000]))

    # 2. 找所有章节标题（支持"第X章"和"（一）"两种格式）
    ch_pattern = r'((?:第[一二三四五六七八九十\d]+章|（[一二三四五六七八九十]+）)[^\n]{0,60})\n'
    for ch_m in re.finditer(ch_pattern, text):
        chapter = ch_m.group(1).strip()
        start = ch_m.end()
        next_ch = re.search(ch_pattern, text[start:])
        end = start + next_ch.start() if next_ch else len(text)
        body = text[start:end]

        # 格式A: 【教学目的和要求】 或 【教学内容、目的和要求】
        m = re.search(r'【教学(?:内容[,、]?\s*)?目的[,、]?\s*要求】(.*?)(?:【|\Z)', body, re.DOTALL)
        if m:
            content = m.group(1).strip()[:1500]
            mastery_lines = re.findall(r'[^。\n]{0,10}(?:掌握|熟悉|了解)[^。\n]{5,150}', content)
            if mastery_lines:
                blocks.append(('教学要求', chapter, '\n'.join(mastery_lines)))

        # 格式B: 【掌握】【熟悉】【了解】 直接标注（麻醉学格式）
        for level_kw in ['掌握', '熟悉', '了解']:
            for m in re.finditer(rf'【{level_kw}】([^【]{{5,200}}?)(?:【|\Z)', body):
                content = m.group(1).strip()[:500]
                if content:
                    blocks.append(('教学要求', chapter, f'【{level_kw}】{content}'))

        # 格式C: 【(本章)教学重点、难点】 或 【教学重点、难点】
        m = re.search(r'【(?:本章)?\s*教学重点[,、]?\s*难点】(.*?)(?:【|\Z)', body, re.DOTALL)
        if m:
            content = m.group(1).strip()[:1500]
            if content:
                blocks.append(('重点难点', chapter, content))

    return blocks

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 noun_extract.py <大纲.txt>")
        sys.exit(1)

    text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='replace')
    blocks = extract_blocks(text)

    if not blocks:
        # 兜底：输出含关键词的行
        print("未找到结构化段落。含'掌握/熟悉/了解'的原文行：\n")
        for line in text.split('\n'):
            line = line.strip()
            if any(kw in line for kw in ['掌握', '熟悉', '了解']) and len(line) > 5:
                # 跳过解释性文字
                if '指学生对' not in line and '指对学过' not in line:
                    print(f"  {line[:150]}")
        sys.exit(0)

    print("## 名词解释候选提取参考\n")
    print("以下是从大纲中提取的关键段落。请从中识别所有可能的**名词解释候选术语**，")
    print("按掌握度（●掌握/○熟悉/·了解）分类。注意：概念/定义类术语优先，方法/步骤类排除。\n")

    for btype, title, content in blocks:
        label = {'教学要求': '教学目的和要求', '重点难点': '教学重点/难点', '概念清单': '独立概念清单'}.get(btype, btype)
        print(f"### {title} · {label}")
        print(f"```\n{content.strip()}\n```\n")

    print(f"> 共 {len(blocks)} 个段落。以上段落中所有标记为掌握/熟悉/了解的概念性术语均应纳入名词解释汇总。")
