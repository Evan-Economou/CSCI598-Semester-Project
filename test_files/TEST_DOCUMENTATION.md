# Style Guide Test Suite Documentation

This directory contains test files to validate the C++ code analyzer's algorithmic checks and LLM semantic analysis.

## Test Files Overview

### 1. `test_algorithmic.cpp` - Built-in Algorithmic Checks

Tests all 7 built-in formatting/documentation checks that run automatically.

**Expected Violations:**

| Line | Type | Severity | Description |
|------|------|----------|-------------|
| ~23  | inconsistent_indentation | WARNING | File mixes tabs (line 17-20) and spaces (line 23-26) |
| 33   | line_too_long | MINOR | Line exceeds 200 characters |
| 1    | inconsistent_brace_placement | MINOR | Mixes same-line (functions 1-2) and next-line braces (function 3) |
| 61   | missing_braces | WARNING | `if (x > 0)` followed by statement without braces |
| 64   | missing_braces | WARNING | `if (x < 10) x--;` one-liner without braces |
| 74   | missing_braces | WARNING | `for` loop without braces |
| 78   | missing_braces | WARNING | `while` loop without braces |
| ~105 | insufficient_comments | MINOR | 20+ lines of code without comments (in testCommentFrequency) |

**Total Expected:** ~8 violations

---

### 2. `test_semantic.cpp` - LLM Semantic Analysis

Tests LLM's ability to detect semantic and logic issues.

**Expected LLM Violations:**

#### CRITICAL Severity:

| Line | Type | Description |
|------|------|-------------|
| 22   | memory_leak | `new int[100]` without corresponding `delete[]` |
| 30   | wrong_delete_type | Uses `delete` instead of `delete[]` for array |
| 68   | missing_default_case | Switch statement without default case |
| 77   | variable_shadowing | Parameter `value` shadows member variable |
| 93   | uninitialized_variable | Variable `x` used before initialization |
| 155  | double_delete | Pointer `p1` deleted twice |
| 158  | memory_leak | Pointer `p2` never deleted |

#### WARNING Severity:

| Line | Type | Description |
|------|------|-------------|
| 36   | naming_convention | Class `my_bad_class` should be `MyBadClass` |
| 39   | naming_convention | Function `Calculate_Sum` should be `calculateSum` |
| 48   | magic_number | Hardcoded 18 instead of named constant |
| 52   | magic_number | Hardcoded 1.15 instead of named constant |
| 53   | magic_number | Hardcoded 500 instead of named constant |
| 59   | use_nullptr | Uses `NULL` instead of `nullptr` |
| 60   | use_nullptr | Uses `0` instead of `nullptr` |
| 84   | deep_nesting | 4 levels of nesting (exceeds 3 level limit) |
| 98   | function_too_long | Function exceeds 50 lines |

**Total Expected:** ~16 semantic violations

---

### 3. `test_no_comments.cpp` - No Comments Check

Tests the CRITICAL check for files with zero comments.

**Expected Violations:**

| Line | Type | Severity | Description |
|------|------|----------|-------------|
| 1    | no_comments | CRITICAL | File contains NO comments whatsoever |

**Total Expected:** 1 CRITICAL violation

---

### 4. `test_clean.cpp` - Clean Code (No Violations)

A well-written C++ file following all best practices.

**Features:**
- ✅ Proper file header comment
- ✅ Consistent indentation (spaces throughout)
- ✅ Consistent brace placement (same-line style)
- ✅ All control structures use braces
- ✅ Comments every ~10-15 lines
- ✅ Named constants instead of magic numbers
- ✅ PascalCase for classes (`BankAccount`)
- ✅ camelCase for functions (`getBalance`, `setBalance`)
- ✅ Uses `nullptr` instead of `NULL`
- ✅ Switch statement has default case
- ✅ No variable shadowing
- ✅ Proper memory management (smart pointers)
- ✅ No deep nesting

**Total Expected:** 0 violations

---

## How to Run Tests

### Manual Testing via Web Interface:

1. Start the application:
   ```bash
   npm start
   ```

2. Navigate to http://localhost:3000

3. Test each file:
   - Upload test file (e.g., `test_algorithmic.cpp`)
   - Click "Analyze Code"
   - Compare results with expected violations above

Note: No need to upload semantic style guide - it's built into the analyzer!

### Expected Analysis Flow:

```
Step 1: Running built-in algorithmic checks...
  - Proper indentation (nesting levels)
  - Line length (<200 chars)
  - Single-line if statements (missing braces)
  - File header comment
  - No comments check - CRITICAL (excluding header)
[OK] Found X formatting/documentation violations

Step 2: LLM Semantic Analysis...
  - Memory leaks
  - Naming conventions
  - Magic numbers
  - Code structure issues
  - Modern C++ best practices
[OK] Found Y semantic violations from LLM

Step 3: Deduplicating violations...
[OK] Final violation count: Z
```

---

## Validation Checklist

Use this checklist when running tests:

### `test_algorithmic.cpp`
- [ ] Detects inconsistent indentation (tabs vs spaces)
- [ ] Detects line >200 characters
- [ ] Detects inconsistent brace placement
- [ ] Detects missing braces on if statements
- [ ] Detects missing braces on for loops
- [ ] Detects missing braces on while loops
- [ ] Detects insufficient comment frequency

### `test_semantic.cpp`
- [ ] Detects memory leaks (new without delete)
- [ ] Detects wrong delete type (delete vs delete[])
- [ ] Detects naming convention violations
- [ ] Detects magic numbers
- [ ] Detects NULL vs nullptr issues
- [ ] Detects missing default in switch
- [ ] Detects variable shadowing
- [ ] Detects deep nesting
- [ ] Detects uninitialized variables
- [ ] Detects double deletion

### `test_no_comments.cpp`
- [ ] Detects CRITICAL "no comments" violation

### `test_clean.cpp`
- [ ] Reports 0 violations
- [ ] Completes analysis without errors

---

## Troubleshooting

### LLM hallucinating violations:
- Restart backend to ensure latest code is running
- The LLM should NOT analyze style guide examples
- Check that violations reference actual code lines

### LLM returns no violations on test_semantic.cpp:
- Check Ollama is running: `ollama serve`
- Verify model is available: `ollama list`
- Try running analysis again (LLM can be inconsistent)

### Indentation violations on properly indented code:
- Algorithm expects 4 spaces = 1 tab = 1 level
- Verify indentation matches brace nesting depth
- Check for mixed tabs/spaces

### Analysis hangs or takes >2 minutes:
- LLM analysis typically takes 30-60 seconds
- Check Ollama console for errors
- Restart Ollama if needed

---

## Summary Statistics

| Test File | Algorithmic Violations | Semantic Violations | Total |
|-----------|------------------------|---------------------|-------|
| test_algorithmic.cpp | ~8 | 0 | ~8 |
| test_semantic.cpp | ~1 (header) | ~16 | ~17 |
| test_no_comments.cpp | 1 (CRITICAL) | 0 | 1 |
| test_clean.cpp | 0 | 0 | 0 |

**Total Test Coverage:** 26+ distinct violation patterns across both algorithmic and semantic checks.
