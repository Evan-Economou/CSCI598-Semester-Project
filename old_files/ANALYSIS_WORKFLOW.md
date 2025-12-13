# Code Analysis Workflow

## Overview

The Code Style Grader uses a **two-tier analysis system**:

1. **Built-in Algorithmic Checks** (always run, fast, deterministic)
2. **LLM Semantic Analysis** (requires semantic style guide, slower, intelligent)

---

## Built-in Algorithmic Checks (No Upload Required)

These checks **always run automatically** on every analysis:

### ✅ Consistent Indentation
- **Rule**: File must use either tabs OR spaces consistently (not mixed)
- **Severity**: WARNING
- **Example**: Mixing `\t` and `    ` in the same file triggers violation

### ✅ Line Length
- **Rule**: Lines should not exceed 200 characters
- **Severity**: MINOR
- **Rationale**: Extremely long lines are hard to read

### ✅ Consistent Brace Placement
- **Rule**: Opening braces must be placed consistently (all same-line OR all next-line)
- **Severity**: MINOR
- **Example Violation**: Using both styles:
  ```cpp
  if (x) {        // Same line
      doThing();
  }

  if (y)          // Next line
  {
      doOther();
  }
  ```

### ✅ Missing Braces on Single-Line Statements
- **Rule**: All control structures (if/for/while) must use braces, even for single statements
- **Severity**: WARNING
- **Example Violation**:
  ```cpp
  if (x > 0)
      doSomething();  // VIOLATION: Missing braces
  ```
- **Correct**:
  ```cpp
  if (x > 0) {
      doSomething();
  }
  ```

### ✅ File Header Comment
- **Rule**: File should have a comment in the first 10 lines
- **Severity**: MINOR
- **Purpose**: Files should describe their purpose

### ✅ Comment Frequency
- **Rule**: At least one comment every 20 lines of code
- **Severity**: MINOR
- **Purpose**: Ensures code is documented

### ✅ No Comments At All
- **Rule**: File MUST have at least one comment somewhere
- **Severity**: CRITICAL
- **Purpose**: Completely undocumented code is unmaintainable

---

## LLM Semantic Analysis (Requires Upload)

To enable semantic analysis, upload `semantic_style_guide.txt` in **RAG Management**.

### 🧠 What the LLM Checks For:

**CRITICAL Severity:**
- Memory leaks (unmatched new/delete, malloc/free)
- Array allocation/deallocation mismatch (new[] without delete[])
- Missing default cases in switch statements
- Variable shadowing (parameters shadowing members)
- Use of uninitialized variables
- Magic numbers (hardcoded values)

**WARNING Severity:**
- Naming conventions (camelCase for functions, PascalCase for classes)
- Deep nesting (>3 levels)
- Long functions (>50 lines)
- Use of `NULL` instead of `nullptr`
- Missing const correctness
- Missing include guards

**MINOR Severity:**
- Missing documentation comments
- Code organization issues
- Readability improvements

### 🚫 What the LLM Does NOT Check:

The LLM is explicitly told to **ignore formatting issues** because they're handled by algorithmic checks:
- Tabs vs spaces
- Line length
- Brace placement
- Trailing whitespace
- Indentation

---

## User Workflow

### Step 1: Upload Code Files
Go to **Code Analysis** tab → Upload C++ files or folders

### Step 2: Upload Semantic Style Guide (One-time)
Go to **RAG Management** tab → Upload `semantic_style_guide.txt`
- This file is provided in the project root
- It tells the LLM what semantic issues to look for
- You can customize it for your specific needs (e.g., add memory leak patterns)

### Step 3: Run Analysis
1. Select uploaded C++ file
2. Select semantic style guide from dropdown
3. Click **Run Analysis**

### What Happens:
```
============================================================
Starting analysis for: example.cpp
File size: 1250 characters
============================================================

Step 1: Running built-in algorithmic checks...
  - Consistent indentation (tabs/spaces)
  - Line length (<200 chars)
  - Consistent brace placement
  - Single-line if statements
  - File header comment
  - Comment frequency
  - No comments check (CRITICAL)
[OK] Found 3 formatting/documentation violations

Step 2: LLM Semantic Analysis (using uploaded semantic style guide)...
  Searching for semantic issues:
  - Memory leaks
  - Naming conventions
  - Magic numbers
  - Code structure issues
  - Modern C++ best practices
[OK] Retrieved RAG context (2400 characters)

  -> Calling Ollama/CodeLlama for semantic analysis...
  [WAIT] This may take 30-60 seconds depending on code complexity...
[OK] LLM semantic analysis complete
[OK] Found 5 semantic violations from LLM

Step 3: Deduplicating violations...
[OK] Final violation count: 8
============================================================
```

---

## Customizing Semantic Analysis

You can modify `semantic_style_guide.txt` to add custom checks:

### Example: Add Memory Leak Detection Rules
```
CRITICAL SEVERITY - Memory Management
- All calls to fopen() must have corresponding fclose()
- All calls to malloc() must have corresponding free()
- All calls to new must have corresponding delete
- Resource acquisition (RAII) should be used for file handles
```

### Example: Add Project-Specific Naming Rules
```
WARNING SEVERITY - Naming Conventions
- All member variables must start with 'm_' prefix
- All constants must use UPPER_SNAKE_CASE
- All getter functions must start with 'get'
```

The LLM will read your custom rules and apply them during analysis!

---

## Benefits of This Approach

### ⚡ Fast Algorithmic Checks
- Instant results for formatting issues
- No false positives
- Consistent behavior

### 🧠 Intelligent Semantic Analysis
- Finds complex issues like memory leaks
- Understands code context
- Adapts to your custom style guide

### 🎯 Best of Both Worlds
- Formatting: handled by precise algorithms
- Semantics: handled by intelligent LLM
- No redundancy or conflicts

---

## Troubleshooting

### "No semantic violations found"
- Make sure you uploaded `semantic_style_guide.txt` in RAG Management
- Check that Ollama is running: `ollama serve`
- Check console logs for errors

### "Too many formatting violations"
- These are from built-in checks
- Fix common issues like mixing tabs/spaces
- Add consistent braces to if statements

### "LLM line numbers are wrong"
- The prompt now includes line numbers for accuracy
- If still wrong, the LLM may need a better model
- Consider using a larger model: `ollama pull codellama:13b`

---

## Summary

**You don't need to upload a formatting style guide anymore!**

Just upload:
1. Your C++ code files
2. `semantic_style_guide.txt` (for LLM analysis)

Everything else is automatic!
