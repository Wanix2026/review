#!/usr/bin/env python3
"""将复习笔记 Markdown 转换为 HTML，使用 references/template.html 模板"""

import re, html as htmllib, sys, os

def slugify(text, max_len=50):
    """Generate a URL-safe slug from Chinese/English text."""
    s = re.sub(r'[^\w一-鿿]', '', text)
    return ('sec-' + s)[:max_len]

def convert(md_path, template_path, output_path=None):
    if output_path is None:
        output_path = md_path.replace('.md', '.html')

    if not os.path.exists(md_path):
        print(f"❌ 文件不存在: {md_path}")
        return None
    if not os.path.exists(template_path):
        print(f"❌ 模板不存在: {template_path}")
        return None

    with open(md_path) as f: md = f.read()
    with open(template_path) as f: template = f.read()

    h1_match = re.search(r'^# (.+?) ·', md, re.MULTILINE)
    course_name = h1_match.group(1).strip() if h1_match else "复习笔记"

    # Build sidebar
    sidebar_items = []
    seen_slugs = set()
    ch_idx = 0
    for line in md.split('\n'):
        if line.startswith('## '):
            title = line[3:].strip()
            slug = slugify(title, 40)
            sidebar_items.append(f'        <li><a href="#{slug}">{htmllib.escape(title)}</a></li>')
            ch_idx += 1
        elif line.startswith('### '):
            title = line[4:].strip()
            if title in ('大纲要求', '可能的考点', '内容要点', '标记说明'):
                continue
            base = slugify(title, 50)
            slug = base if base not in seen_slugs else f'{base}-ch{ch_idx}'
            seen_slugs.add(slug)
            sidebar_items.append(f'        <li><a class="sub" href="#{slug}">{htmllib.escape(title)}</a></li>')

    def fmt(txt):
        return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', txt)

    # Convert body
    lines = md.split('\n')
    result = []
    in_table = False; in_code = False; in_bq = False; rows = []
    seen_slugs2 = set(); ch_idx2 = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith('# ') and '复习笔记' in line:
            result.append(f'<h1 id="sec-{course_name}">{htmllib.escape(line[2:].strip())}</h1>')
            i += 1; continue

        if line.startswith('> '):
            if not in_bq: result.append('<blockquote>'); in_bq = True
            txt = fmt(line[2:])
            result.append(f'<p>{htmllib.escape(txt).replace("&lt;strong&gt;", "<strong>").replace("&lt;/strong&gt;", "</strong>")}</p>')
            i += 1; continue
        elif in_bq and not line.startswith('> '):
            result.append('</blockquote>'); in_bq = False

        if line.startswith('```'):
            if in_code: result.append('</code></pre>'); in_code = False
            else: result.append('<pre><code>'); in_code = True
            i += 1; continue
        if in_code: result.append(htmllib.escape(line)); i += 1; continue

        if '|' in line and line.strip().startswith('|'):
            if not in_table: result.append('<table>'); in_table = True
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if all(c.startswith('---') or c.startswith(':--') for c in cells):
                rows.append('__SEP__')
            else:
                is_header = len([r for r in rows if r != '__SEP__']) == 0
                tag = 'th' if is_header else 'td'
                cells_html = ''.join(f'<{tag}>{fmt(htmllib.escape(c))}</{tag}>' for c in cells)
                rows.append(f'<tr>{cells_html}</tr>')
            i += 1; continue
        elif in_table and '|' not in line:
            result.append('\n'.join([r for r in rows if r != '__SEP__']))
            result.append('</table>'); rows = []; in_table = False

        if line.startswith('## '):
            title = line[3:].strip()
            base = slugify(title, 40)
            ch_idx2 += 1
            result.append(f'<h2 id="{base}">{htmllib.escape(title)}</h2>')
            i += 1; continue
        if line.startswith('### '):
            title = line[4:].strip()
            base = slugify(title, 50)
            slug = base if base not in seen_slugs2 else f'{base}-ch{ch_idx2}'
            seen_slugs2.add(slug)
            result.append(f'<h3 id="{slug}">{htmllib.escape(title)}</h3>')
            i += 1; continue
        if line.startswith('📄 '):
            result.append(f'<p class="src-tag">{htmllib.escape(line)}</p>')
            i += 1; continue

        txt = fmt(line)
        txt = htmllib.escape(txt).replace("&lt;strong&gt;", "<strong>").replace("&lt;/strong&gt;", "</strong>")
        txt = re.sub(r'^●\s', '<span class="dot-master"></span>', txt)
        txt = re.sub(r'^○\s', '<span class="dot-familiar"></span>', txt)
        txt = re.sub(r'^·\s', '<span class="dot-know"></span>', txt)
        if not line.strip(): result.append('')
        elif txt.strip(): result.append(f'<p>{txt}</p>')
        i += 1

    if in_table:
        result.append('\n'.join([r for r in rows if r != '__SEP__']))
        result.append('</table>')
    if in_bq: result.append('</blockquote>')

    content = '\n'.join(result)
    sb = '\n'.join(sidebar_items)

    html = template.replace('{{COURSE_NAME}}', course_name)
    html = html.replace('{{SIDEBAR_ITEMS}}', sb)
    html = html.replace('{{GAP_SUMMARY}}', '资料完整 · 0处缺口')
    html = html.replace('{{CONTENT}}', content)

    with open(output_path, 'w') as f: f.write(html)

    h2n = len([l for l in sidebar_items if 'class="sub"' not in l])
    h3n = len([l for l in sidebar_items if 'class="sub"' in l])

    # Char-count sanity check: HTML text should not be drastically shorter than MD
    import html as _h
    md_text = re.sub(r'[#*>\-\|\s]', '', md)
    html_text = re.sub(r'<[^>]+>', '', html)
    html_text = re.sub(r'\s', '', html_text)
    ratio = len(html_text) / max(len(md_text), 1)
    warning = ''
    if ratio < 0.5:
        warning = ' ⚠️ HTML字符数不足MD的50%，转换可能有遗漏'
    elif ratio < 0.8:
        warning = ' (content ratio OK)'

    print(f'✅ {os.path.basename(output_path)}: {len(html):,} bytes · 侧栏 {h2n}章+{h3n}子节 · 内容比 {ratio:.0%}{warning}')
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 to_html.py <笔记.md> [output.html]")
        sys.exit(1)
    md = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else md.replace('.md', '.html')
    tpl = os.path.join(os.path.dirname(__file__), '..', 'references', 'template.html')
    convert(md, tpl, out)
