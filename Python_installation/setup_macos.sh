#!/bin/bash
set -e

echo "=== 1. Kiem tra va cai dat uv ==="
if command -v conda >/dev/null 2>&1; then
    conda deactivate 2>/dev/null || true
fi

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

echo "=== 2. Cai dat Python 3.12 ==="
uv python install 3.12

echo "=== 3. Khoi tao du an & moi truong ao (.venv) ==="
mkdir -p "$HOME/Downloads/code-practice"
cd "$HOME/Downloads/code-practice"

if [ ! -f "pyproject.toml" ]; then
    uv init --bare --python 3.12
fi

uv venv --python 3.12 --clear
source .venv/bin/activate

echo "=== 4. Tao requirements.txt & cai dat thu vien ==="
cat > requirements.txt <<'EOF'
numpy
pandas
matplotlib
seaborn
streamlit
yfinance
EOF

uv pip install -r requirements.txt

echo ""
echo "=========================================================="
echo "HOAN TAT CAI DAT!"
echo "Thu muc du an: $HOME/Downloads/code-practice"
echo "Python version: $(python --version)"
echo "=========================================================="

# Giu terminal mo va giu nguyen trang thai da kich hoat .venv
exec "${SHELL:-/bin/zsh}" -i
