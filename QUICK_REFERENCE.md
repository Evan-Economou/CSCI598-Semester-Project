# Ollama Integration - Quick Reference

## ⚡ Quick Start

### 1. Prerequisites
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download CodeLlama
ollama pull codellama:7b

# Start Ollama (if not auto-started)
ollama serve
```

### 2. Configure Backend
```bash
cd backend
cp .env.example .env
# Edit .env if needed (defaults work for most cases)
```

### 3. Test Integration
```bash
# Start backend
python run.py

# In another terminal, run test
./test_ollama.sh
```

---

## 🔧 Configuration

### Environment Variables
```env
OLLAMA_HOST=http://localhost:11434     # Ollama API endpoint
OLLAMA_MODEL=codellama:7b               # Model to use
OLLAMA_TEMPERATURE=0.3                  # Randomness (0.0-1.0)
```

**Temperature Guide:**
- `0.1-0.3`: More consistent, focused (recommended for style analysis)
- `0.4-0.6`: Balanced creativity and consistency
- `0.7-1.0`: More creative, less predictable

---

## 🚀 API Quick Reference

### Check System Status
```bash
curl -X POST http://localhost:8000/api/setup/check
```

**Response:**
```json
{
  "ollama_running": true,
  "model_available": true,
  "status": "ready",
  "message": "System ready for code analysis"
}
```

### Upload Style Guide
```bash
curl -X POST http://localhost:8000/api/rag/upload \
  -F "file=@style_guide.txt" \
  -F "doc_type=style_guide"
```

**Response:**
```json
{
  "document_id": "abc123",
  "filename": "style_guide.txt",
  "size": 5432
}
```

### Upload C++ File
```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@example.cpp"
```

**Response:**
```json
{
  "file_id": "xyz789",
  "file_name": "example.cpp",
  "file_size": 1234
}
```

### Run Analysis
```bash
curl -X POST http://localhost:8000/api/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "xyz789",
    "style_guide_id": "abc123",
    "use_rag": false
  }'
```

**Response:**
```json
{
  "file_name": "example.cpp",
  "violations": [
    {
      "type": "indentation",
      "severity": "CRITICAL",
      "line_number": 5,
      "column": 1,
      "description": "Tabs used instead of spaces for indentation",
      "code_snippet": "\tint x = 5;",
      "style_guide_reference": "CRITICAL rules"
    }
  ],
  "total_violations": 1,
  "violations_by_severity": {
    "CRITICAL": 1,
    "WARNING": 0,
    "MINOR": 0
  },
  "status": "success"
}
```

---

## 📊 Violation Object Structure

```typescript
interface Violation {
  type: string;                        // Category: indentation, naming, etc.
  severity: "CRITICAL" | "WARNING" | "MINOR";
  line_number: number;                 // 1-indexed line number
  column?: number;                     // Optional column position
  description: string;                 // One-sentence explanation
  code_snippet?: string;               // The actual line of code
  style_guide_reference?: string;      // Which rule was violated
}
```

---

## 🎨 Severity Levels

| Severity | Color | Meaning | Examples |
|----------|-------|---------|----------|
| **CRITICAL** | 🔴 Red | Must fix | Tabs, missing braces, memory leaks |
| **WARNING** | 🟡 Yellow | Should fix | Long lines, naming conventions |
| **MINOR** | 🔵 Blue | Good practice | Missing comments, extra whitespace |

---

## 🧪 Testing

### Automated Test
```bash
cd backend
./test_ollama.sh
```

### Manual Test with Sample Files
```bash
# Test with intentional violations
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@test_samples/bad_style.cpp"

# Test with clean code
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@test_samples/good_style.cpp"
```

---

## 🐛 Troubleshooting

### Ollama Not Running
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start if not running
ollama serve
```

### Model Not Found
```bash
# List installed models
ollama list

# Download CodeLlama if missing
ollama pull codellama:7b
```

### Slow Analysis (>30 seconds)
- Check Ollama server load: `htop` or `top`
- Reduce file size (max 10MB recommended)
- Check internet connection (first run downloads model)

### Empty Violations List
- Verify style guide uploaded correctly
- Check Ollama logs: `journalctl -u ollama -f`
- Enable debug logging in backend

---

## 📈 Performance Expectations

| Metric | Expected Value |
|--------|----------------|
| Rule-based analysis | 50-100ms |
| LLM analysis | 2-10 seconds |
| Total per file | 3-12 seconds |
| Memory usage | ~4.5GB (CodeLlama 7B) |
| Model download size | ~3.8GB |

---

## 🔮 RAG Integration (Coming Soon)

### Current State
- ✅ Context parameter ready
- ✅ Prompt supports additional context
- ⏳ ChromaDB integration pending

### When Implemented
```python
# RAG will provide similar examples
context = rag_service.search(code_patterns)
violations = ollama_service.analyze_code(code, style_guide, context)
```

**Benefits:**
- Better context for edge cases
- Historical violation patterns
- Similar code examples

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **OLLAMA_INTEGRATION.md** | Comprehensive guide (350 lines) |
| **IMPLEMENTATION_SUMMARY.md** | Technical details (450 lines) |
| **README_PROJECT.md** | Project overview |
| **This file** | Quick reference |

---

## 🔗 Useful Commands

```bash
# Check Ollama version
ollama --version

# List available models
ollama list

# Remove a model
ollama rm codellama:7b

# View Ollama logs
journalctl -u ollama -f

# Test backend is running
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

---

## 💡 Tips

1. **First analysis is slower** - CodeLlama needs to "warm up"
2. **Use temperature 0.3** - More consistent results
3. **Keep style guides concise** - Extract only relevant rules
4. **Test with sample files** - Verify before running on real code
5. **Monitor Ollama logs** - Helpful for debugging

---

## 🚦 Status Indicators

### System Check Response
```json
{
  "status": "ready",          // ✅ Everything working
  "status": "not_ready",      // ⚠️ Missing components
  "ollama_running": false,    // ❌ Start Ollama
  "model_available": false    // ❌ Download CodeLlama
}
```

---

## 📞 Support

**Issues?** Check these in order:

1. ✅ Is Ollama running? → `curl http://localhost:11434/api/tags`
2. ✅ Is CodeLlama downloaded? → `ollama list`
3. ✅ Is backend running? → `curl http://localhost:8000/health`
4. 📖 Check detailed docs → `OLLAMA_INTEGRATION.md`
5. 🐛 Enable debug logging → Add `print()` statements

---

## 🎯 Next Steps

### For Backend Developers
- ✅ Integration complete
- ⏳ Waiting on RAG implementation

### For Frontend Developers
- ⏳ Display violations in UI
- ⏳ Add loading states (3-12s wait)
- ⏳ Implement violation highlighting
- ⏳ Test end-to-end workflow

### For Educators
- 📝 Customize style guide
- 🧪 Test with student code
- 📊 Review violation types
- ✏️ Adjust severity levels

---

**Last Updated:** November 21, 2025  
**Version:** 1.0.0 (Ollama Integration Complete)  
**Status:** ✅ Ready for Production Use
