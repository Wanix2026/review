#!/bin/bash
# Review Skill — 一键安装脚本
set -e

echo "========================================="
echo "  Review Skill · 环境检查与安装"
echo "========================================="
echo ""

# ---- Python ----
PYTHON=$(which python3 2>/dev/null || echo "")
if [ -z "$PYTHON" ]; then
    echo "❌ python3 未安装，请先安装 Python 3"
    exit 1
fi
echo "✅ python3: $($PYTHON --version)"

# ---- pip packages ----
MISSING=""
for pkg in pdfminer.six python-pptx python-docx openpyxl; do
    if ! $PYTHON -c "import ${pkg//-/_}" 2>/dev/null && ! $PYTHON -c "import ${pkg%.six}" 2>/dev/null; then
        MISSING="$MISSING $pkg"
    fi
done

# Special check for pdfminer.six (module name is pdfminer)
if $PYTHON -c "import pdfminer" 2>/dev/null; then
    : # pdfminer.six provides 'pdfminer' module
elif echo "$MISSING" | grep -q "pdfminer.six"; then
    : # already flagged as missing
fi

if [ -n "$MISSING" ]; then
    echo ""
    echo "📦 安装缺失依赖: $MISSING"
    $PYTHON -m pip install $MISSING
else
    echo "✅ 所有 Python 依赖已就绪"
fi

# ---- pdf2txt ----
if ! command -v pdf2txt &>/dev/null; then
    if $PYTHON -c "import pdfminer" 2>/dev/null; then
        PDF2TXT_PATH=$($PYTHON -m site --user-base 2>/dev/null)/bin/pdf2txt
        if [ -x "$PDF2TXT_PATH" ]; then
            echo "✅ pdf2txt: $PDF2TXT_PATH (通过 pip 安装)"
        else
            echo "⚠️  pdf2txt 命令未在 PATH 中，但 pdfminer 已安装。可以通过 pip 路径调用。"
        fi
    fi
else
    echo "✅ pdf2txt: $(command -v pdf2txt)"
fi

# ---- Install skill ----
SKILL_DIR="$HOME/.claude/skills/review"
if [ -d "$SKILL_DIR" ]; then
    echo ""
    echo "📁 技能目录已存在: $SKILL_DIR"
    echo "   将覆盖更新..."
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$SKILL_DIR/scripts" "$SKILL_DIR/references"

# Copy files
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"
cp "$SCRIPT_DIR/scripts/extract.py" "$SKILL_DIR/scripts/extract.py"
cp "$SCRIPT_DIR/scripts/verify.py" "$SKILL_DIR/scripts/verify.py"
cp "$SCRIPT_DIR/references/template.html" "$SKILL_DIR/references/template.html"
cp "$SCRIPT_DIR/references/checklist.md" "$SKILL_DIR/references/checklist.md"

echo ""
echo "========================================="
echo "  ✅ 安装完成"
echo "========================================="
echo ""
echo "  技能位置: $SKILL_DIR"
echo "  使用方式: /review <课程目录路径>"
echo ""

# ---- Verify ----
echo "快速验证:"
$PYTHON -c "
import pptx, docx, openpyxl
from pdfminer.high_level import extract_text
print('  ✅ pptx: OK')
print('  ✅ docx: OK')
print('  ✅ openpyxl: OK')
print('  ✅ pdfminer: OK')
" 2>&1

echo ""
echo "重启 Claude Code 后技能即生效。"
