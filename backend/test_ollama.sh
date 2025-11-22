#!/bin/bash

# Quick test script for Ollama integration
# This script demonstrates the complete workflow

set -e  # Exit on error

echo "=============================================="
echo "  Ollama Integration Test Script"
echo "=============================================="
echo ""

# Configuration
BACKEND_URL="http://localhost:8000"
STYLE_GUIDE="../style_guide.txt"
TEST_FILE="../test_samples/bad_style.cpp"

echo "1. Checking system status..."
STATUS=$(curl -s -X POST "${BACKEND_URL}/api/setup/check")
echo "$STATUS" | python -m json.tool

OLLAMA_RUNNING=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin)['ollama_running'])" 2>/dev/null || echo "false")
MODEL_AVAILABLE=$(echo "$STATUS" | python -c "import sys, json; print(json.load(sys.stdin)['model_available'])" 2>/dev/null || echo "false")

if [ "$OLLAMA_RUNNING" != "True" ] && [ "$OLLAMA_RUNNING" != "true" ]; then
    echo "❌ ERROR: Ollama is not running!"
    echo "Please start Ollama: ollama serve"
    exit 1
fi

if [ "$MODEL_AVAILABLE" != "True" ] && [ "$MODEL_AVAILABLE" != "true" ]; then
    echo "❌ ERROR: CodeLlama model not found!"
    echo "Please download the model: ollama pull codellama:7b"
    exit 1
fi

echo "✅ Ollama is ready!"
echo ""

echo "2. Uploading style guide..."
STYLE_UPLOAD=$(curl -s -X POST "${BACKEND_URL}/api/rag/upload" \
  -F "file=@${STYLE_GUIDE}" \
  -F "doc_type=style_guide")
echo "$STYLE_UPLOAD" | python -m json.tool

STYLE_ID=$(echo "$STYLE_UPLOAD" | python -c "import sys, json; print(json.load(sys.stdin)['document_id'])" 2>/dev/null)
echo "Style guide ID: $STYLE_ID"
echo ""

echo "3. Uploading test C++ file..."
FILE_UPLOAD=$(curl -s -X POST "${BACKEND_URL}/api/files/upload" \
  -F "file=@${TEST_FILE}")
echo "$FILE_UPLOAD" | python -m json.tool

FILE_ID=$(echo "$FILE_UPLOAD" | python -c "import sys, json; print(json.load(sys.stdin)['file_id'])" 2>/dev/null)
echo "File ID: $FILE_ID"
echo ""

echo "4. Running analysis (this may take 5-15 seconds)..."
ANALYSIS=$(curl -s -X POST "${BACKEND_URL}/api/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"file_id\":\"${FILE_ID}\",\"style_guide_id\":\"${STYLE_ID}\",\"use_rag\":false}")

echo "$ANALYSIS" | python -m json.tool

echo ""
echo "5. Summary:"
TOTAL=$(echo "$ANALYSIS" | python -c "import sys, json; print(json.load(sys.stdin)['total_violations'])" 2>/dev/null)
echo "Total violations found: $TOTAL"

echo ""
echo "✅ Test complete! Check the violations above."
echo ""
echo "To see detailed documentation:"
echo "  cat ../OLLAMA_INTEGRATION.md"
