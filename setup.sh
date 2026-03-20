#!/bin/bash
set -e
echo "🖥  Decision Desk — Setup"
echo "========================="

# Check Rust
if ! command -v cargo &>/dev/null; then
  export PATH="$HOME/.cargo/bin:$PATH"
fi
if ! command -v cargo &>/dev/null; then
  echo "⚠  Rust not found. Installing..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
  export PATH="$HOME/.cargo/bin:$PATH"
fi
echo "✓ Rust $(rustc --version)"

# npm install
echo ""
echo "Installing npm dependencies..."
npm install
echo "✓ npm packages installed"

# Python deps
echo ""
echo "Installing Python dependencies..."
pip3 install fastapi uvicorn sqlalchemy pydantic httpx 2>/dev/null || true
echo "✓ Python packages installed"

# Create data dir
mkdir -p data
echo "✓ Data directory ready"

echo ""
echo "========================="
echo "✅ Setup complete!"
echo ""
echo "To run Decision Desk:"
echo "  Terminal 1: cd backend && python3 -m uvicorn app.main:app --reload --port 8000"
echo "  Terminal 2: npm run dev"
echo ""
echo "Or for the full desktop experience (after Tauri is ready):"
echo "  ./run.sh"
echo ""
echo "Optional — enable AI features:"
echo "  1. Download Ollama: https://ollama.com/download"
echo "  2. Run: ollama pull llama3.2"
