# Quick Test Guide

## Setup (One-time)

1. **Start the application:**
   ```bash
   npm start
   ```

2. **No additional setup needed!**
   - All checks are built-in (algorithmic + LLM)
   - Just upload files and analyze

## Test Files at a Glance

### 🔴 test_algorithmic.cpp (violations expected)
Tests formatting checks:
- Inconsistent tabs/spaces
- Long lines (>200 chars)
- Missing braces on if/for/while

**Quick check:** Should find formatting violations

---

### 🔴 test_semantic.cpp (many violations expected)
Tests algorithmic semantic checks:
- Memory leaks (new without delete)
- Wrong delete type (delete vs delete[])
- Naming conventions (snake_case vs camelCase/PascalCase)
- Magic numbers
- NULL vs nullptr

**Quick check:** Should find ~10-15 semantic violations (all REAL, no hallucinations)

---

### 🔴 test_no_comments.cpp (1 CRITICAL violation)
Tests the "no comments at all" check

**Quick check:** Should find exactly 1 CRITICAL violation, NO hallucinated memory leaks

---

### 🟢 test_clean.cpp (0 violations)
Perfect code with no issues

**Quick check:** Should find 0 violations

---

## Running a Test

1. **Upload file:**
   - Click "Upload Files"
   - Select test file

2. **Analyze:**
   - Select the uploaded file
   - Click "Analyze Code"
   - Wait 10-20 seconds

3. **Verify results:**
   - Check violation count matches expected
   - Click on violations to see details
   - Verify line numbers are accurate

---

## Analysis Flow

```
Step 1: Running formatting checks...
  - Proper indentation (nesting levels)
  - Line length (<200 chars)
  - Single-line if statements (missing braces)
  - File header comment
  - No comments check - CRITICAL (excluding header)

Step 2: Running algorithmic semantic checks...
  - Memory leaks (new/delete matching)
  - Naming conventions (camelCase/PascalCase)
  - Magic numbers (hardcoded literals) [if style guide mentions it]
  - NULL vs nullptr

Step 3: LLM comment quality analysis...
  - Checking if comments are descriptive...

Step 4: Deduplicating violations...
```

---

## What's Checked Algorithmically (Reliable & Fast)

✅ **Formatting:**
- Indentation (4 spaces = 1 tab = 1 level)
- Line length >200 chars
- Missing braces on control structures
- File header comments
- No comments at all (CRITICAL)

✅ **Semantic:**
- Memory leaks (new without delete)
- Wrong delete type (delete vs delete[])
- Naming conventions (PascalCase for classes, camelCase for functions)
- Magic numbers (only if style guide mentions "magic number", "const", or "named constant")
- NULL vs nullptr

## What LLM Checks (Simple Task)

✅ **Comment Quality:**
- Vague comments ("// x", "// temp")
- Unhelpful comments ("// code")
- Obvious/redundant comments ("// increment i" for i++)

---

## Common Issues

**❌ False memory leak detections:**
- Restart backend to pick up latest code changes
- Algorithmic detector only flags actual `new` without `delete`

**❌ Wrong line numbers:**
- Restart backend to pick up latest code
- Check console for parsing errors

**❌ Indentation violations on properly indented code:**
- Verify 4 spaces = 1 level (or 1 tab = 1 level)
- Check that code matches brace nesting depth
- Case statements inside switch blocks are allowed to be indented +1

**❌ Analysis is slow:**
- Algorithmic checks are fast (<1 second)
- LLM comment quality check takes 5-10 seconds
- If it takes longer, check Ollama console
