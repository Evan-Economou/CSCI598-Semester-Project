# Ollama Integration with CodeLlama

## Overview

The Code Style Grader now integrates with Ollama and CodeLlama to provide intelligent, context-aware C++ code analysis. The system combines rule-based checking with LLM-powered semantic analysis to identify style violations.

## Architecture

### Two-Phase Analysis Pipeline

1. **Rule-Based Analysis** (Fast, Deterministic)
   - Parses style guide to extract rules
   - Runs pattern-matching checks
   - Detects common violations (tabs, trailing whitespace, line length, etc.)

2. **LLM Analysis** (Semantic, Context-Aware)
   - Sends code and style guide to CodeLlama
   - Receives structured violation reports
   - Provides one-sentence descriptions for each issue
   - Identifies semantic and contextual violations

3. **Smart Merging**
   - Deduplicates violations found by both systems
   - Prevents reporting the same issue twice
   - Sorts by line number for readability

## Setup Requirements

### 1. Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from https://ollama.com/download

### 2. Download CodeLlama Model

```bash
ollama pull codellama:7b
```

**Note:** CodeLlama 7B model is approximately 3.8GB. First download will take time depending on internet speed.

### 3. Start Ollama Service

```bash
ollama serve
```

Or on most systems, Ollama starts automatically after installation.

### 4. Verify Installation

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Or use the API endpoint
curl -X POST http://localhost:8000/api/setup/check
```

## Configuration

### Environment Variables

Add to `backend/.env`:

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=codellama:7b
OLLAMA_TEMPERATURE=0.3
```

**OLLAMA_TEMPERATURE:** Controls randomness (0.0-1.0)
- `0.3` (default): More consistent, focused analysis
- Lower values: More deterministic
- Higher values: More creative but less consistent

## How It Works

### 1. Prompt Engineering

The system constructs a specialized prompt that:
- Provides the style guide rules
- Shows the code to analyze
- Instructs the LLM on output format
- Requests one-sentence descriptions

**Example Prompt Structure:**
```
You are a C++ code style analyzer...

STYLE GUIDE RULES:
CRITICAL:
- No tabs for indentation - use spaces only
- Opening braces must be on the same line
...

CODE TO ANALYZE:
```cpp
int main() {
	int x = 5;
}
```

OUTPUT FORMAT:
LINE <number> | <SEVERITY> | <type> | <one-sentence description>
```

### 2. Response Parsing

The LLM returns violations in a structured format:

```
LINE 2 | CRITICAL | indentation | Tabs used instead of spaces for indentation
LINE 5 | WARNING | naming | Variable name 'x' is not descriptive
LINE 10 | MINOR | whitespace | Missing blank line between logical sections
```

### 3. Violation Object Creation

Each parsed line becomes a `Violation` object with:
- `type`: Category of violation (indentation, naming, etc.)
- `severity`: CRITICAL, WARNING, or MINOR
- `line_number`: Exact line in source code
- `description`: One-sentence explanation
- `code_snippet`: The actual line of code
- `style_guide_reference`: Which rule was violated

## RAG Integration (Future)

The system is designed to support RAG (Retrieval-Augmented Generation):

### Current State
- `context` parameter in `analyze_code()` is optional
- `_get_rag_context()` method exists but returns `None`
- Prompt includes section for "ADDITIONAL CONTEXT"

### Future Enhancement
When RAG is implemented:

1. **Context Retrieval:**
   ```python
   def _get_rag_context(self, code: str) -> Optional[str]:
       # Extract code patterns
       patterns = self._extract_patterns(code)
       
       # Query ChromaDB for similar examples
       relevant_docs = self.rag_service.search(patterns)
       
       # Return focused style guide excerpts
       return self._format_context(relevant_docs)
   ```

2. **Enhanced Analysis:**
   - LLM receives code + style guide + similar examples
   - Better context for edge cases
   - More accurate violation detection

## API Usage

### Check System Status

```bash
POST /api/setup/check
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

### Analyze Code

```bash
POST /api/analysis/analyze
{
  "file_id": "abc123",
  "style_guide_id": "xyz789",
  "use_rag": false
}
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
      "description": "Tabs used instead of spaces for indentation",
      "code_snippet": "\tint x = 5;",
      "style_guide_reference": "CRITICAL rules"
    }
  ],
  "total_violations": 1,
  "status": "success"
}
```

## Testing

### Test Samples Provided

1. **`test_samples/bad_style.cpp`**
   - Contains multiple intentional violations
   - Good for testing detection

2. **`test_samples/good_style.cpp`**
   - Follows style guide correctly
   - Should have minimal/no violations

### Manual Testing

```bash
# 1. Start backend
cd backend
python run.py

# 2. Upload style guide
curl -X POST http://localhost:8000/api/rag/upload \
  -F "file=@../style_guide.txt" \
  -F "doc_type=style_guide"

# 3. Upload test file
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@../test_samples/bad_style.cpp"

# 4. Run analysis
curl -X POST http://localhost:8000/api/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"file_id":"<file_id>","style_guide_id":"<style_guide_id>","use_rag":false}'
```

## Performance Considerations

### Response Times
- **Rule-based checks:** < 100ms
- **LLM analysis:** 2-10 seconds (depends on code length)
- **Total:** Typically 3-12 seconds per file

### Optimization Strategies

1. **Prompt Optimization:**
   - Extract only relevant rules from style guide
   - Limit context to 1000 characters
   - Use `num_predict` to cap response length

2. **Parallel Processing (Future):**
   - Analyze multiple files concurrently
   - Background processing with status updates

3. **Caching (Future):**
   - Cache similar code patterns
   - Reuse analysis for unchanged files

## Troubleshooting

### Ollama Not Running
**Error:** `Ollama connection check failed`

**Solution:**
```bash
ollama serve
# Or check if already running:
ps aux | grep ollama
```

### Model Not Found
**Error:** `CodeLlama model not found`

**Solution:**
```bash
ollama pull codellama:7b
# Verify:
ollama list
```

### Slow Analysis
**Symptom:** Analysis takes > 30 seconds

**Solutions:**
- Reduce file size (max 10MB)
- Lower `num_predict` in ollama_service.py
- Use faster model: `codellama:7b` instead of larger variants

### Empty Violations List
**Symptom:** LLM returns no violations

**Possible Causes:**
1. Code actually follows style guide perfectly
2. LLM didn't understand prompt format
3. Response parsing failed

**Debug:**
```python
# Add logging in ollama_service.py
print(f"LLM Response: {response_text}")
```

## Development Notes

### Key Files

- **`backend/app/services/ollama_service.py`**
  - Core LLM integration
  - Prompt construction
  - Response parsing

- **`backend/app/parsers/cpp_analyzer.py`**
  - Analysis orchestration
  - Violation merging
  - Statistics calculation

- **`backend/app/api/setup.py`**
  - System health checks
  - Configuration endpoints

### Adding New Violation Types

To teach the LLM about new violation types:

1. Update `style_guide.txt` with new rules
2. LLM will automatically detect based on guide
3. No code changes needed!

### Customizing Output Format

Modify `_build_analysis_prompt()` to change output format:

```python
# Current format
"LINE <number> | <SEVERITY> | <type> | <description>"

# Custom format (modify prompt accordingly)
"<number>:<severity>:<type> - <description>"
```

Then update `_parse_violations()` regex pattern.

## Future Enhancements

### Phase 1 (Current) ✅
- [x] Ollama integration
- [x] CodeLlama analysis
- [x] One-sentence descriptions
- [x] Violation parsing
- [x] Smart merging

### Phase 2 (Next)
- [ ] RAG context integration
- [ ] ChromaDB semantic search
- [ ] Similar code examples
- [ ] Historical violation patterns

### Phase 3 (Advanced)
- [ ] Multi-file analysis
- [ ] Project-wide style checking
- [ ] Auto-fix suggestions
- [ ] Custom rule definitions

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [CodeLlama Model Card](https://huggingface.co/codellama)
- [FastAPI Async Guide](https://fastapi.tiangolo.com/async/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
