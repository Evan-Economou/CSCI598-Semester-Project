# Code Style Grader - Project Specifications

## Project Overview

An AI-powered code evaluation system designed for educational settings to accelerate the grading process of student C++ assignments against custom style guides. The system combines a Python-based backend with RAG (Retrieval-Augmented Generation) capabilities and a React-based frontend that mimics an IDE interface.

## Core Requirements

### Target Audience
- **Primary Users**: Educators and teaching assistants grading student code
- **Use Case**: Automated evaluation of C++ assignments against custom style guides
- **Environment**: Local deployment with no user accounts or multi-user features

### Supported Languages
- **C++ only**: `.cpp` and `.h` files

## Functional Specifications

### 1. Backend System

#### 1.1 AI-Powered Code Analysis Engine
- **Language**: Python (preferred for LLM integration)
- **Purpose**: Analyze C++ source code for style guide violations
- **Processing**: Static code analysis (no compilation required)
- **Analysis Types**:
  - Code formatting violations
  - Code structure issues
  - Best practices violations
  - Comment density and quality
  - Custom violations as defined in uploaded style guides

#### 1.2 RAG (Retrieval-Augmented Generation) System
- **Knowledge Base Contents**:
  - User-uploaded custom style guides
  - Coding best practices documentation
  - Reference materials for C++ standards
- **Functionality**:
  - Provide live access to style guide information during analysis
  - Support dynamic updates to knowledge base
  - Enable context-aware violation detection and explanation

#### 1.3 Style Guide Processing
- **Input Format**: Plain text files
- **Parsing Requirements**:
  - Parse different severity sections (CRITICAL, WARNING, MINOR, etc.)
  - Extract violation rules organized by severity level
  - Handle section headers in ALL CAPS format
  - Link specific violations back to relevant style guide sections
- **Error Handling**: Report errors for unparsable or unclear style guide content

### 2. Frontend System

#### 2.1 Technology Stack
- **Framework**: React
- **Design**: IDE-like interface
- **Deployment**: Local hosting

#### 2.2 Core Interface Components

##### File Management Panel
- **File Upload**: Support for individual `.cpp` and `.h` files
- **Folder Upload**: Ability to select and upload entire directories
- **File Browser**: List view of all uploaded files
- **File Selection**: Click-to-select individual files for analysis
- **Batch Processing**: Sequential processing of multiple files

##### Code Display Panel
- **Syntax Highlighting**: C++ code with proper highlighting
- **Line Numbers**: Display line numbers alongside code
- **Violation Highlighting**: Color-coded markers for different violation types
- **Violation Navigation**: Next/Previous buttons to jump between violations
- **Responsive Layout**: Scrollable code view with fixed line numbers

##### Violation Details Panel
- **Violation Information**:
  - Violation type and severity level
  - Line number and character position
  - Description of the violation
  - Reference to relevant style guide section
- **Summary Statistics**:
  - Total violation count
  - Breakdown by violation type
  - Breakdown by severity level

##### RAG System Management Panel
- **Document Upload**: Interface for adding new reference documents
- **Document Management**: View, remove, or replace existing RAG documents
- **Document Types**: Support for style guides and best practices documents

### 3. Data Management

#### 3.1 Input Data Formats
- **Code Files**: `.cpp` and `.h` files
- **Style Guides**: Plain text format with structured sections
- **RAG Documents**: Various text formats for reference materials

#### 3.2 Output Data Formats
- **Analysis Results**: JSON format containing:
  - File metadata (name, path, analysis timestamp)
  - Violation list with details (type, severity, line number, description, style guide reference)
  - Summary statistics
  - Processing status and any errors

#### 3.3 Data Persistence
- **Results Storage**: JSON files saved to local filesystem
- **RAG Knowledge Base**: Local storage for uploaded reference documents
- **No User Accounts**: Stateless application with file-based data management

## Technical Specifications

### 4. Backend Architecture

#### 4.1 Core Modules
- **File Parser**: Handle C++ file reading and basic syntax parsing
- **Style Guide Processor**: Parse and structure style guide rules
- **RAG Integration**: Interface with vector database and retrieval system
- **Analysis Engine**: AI-powered code evaluation using LLM
- **API Layer**: REST endpoints for frontend communication

#### 4.2 RAG Implementation
- **Vector Database**: Local vector storage for document embeddings
- **Retrieval System**: Semantic search for relevant style guide sections
- **Context Assembly**: Combine code context with relevant style guide information
- **LLM Integration**: Process combined context for violation detection

#### 4.3 AI Model Requirements
- **Language Model**: Support for code analysis and natural language processing
- **Input Processing**: Handle combined code and style guide context
- **Output Format**: Structured violation reports with explanations
- **Local Deployment**: Models that can run locally without external API calls

### 5. Frontend Architecture

#### 5.1 Component Structure
- **App Container**: Main application wrapper
- **File Manager**: Handle file upload and selection
- **Code Viewer**: Display and highlight code with violations
- **Violation Navigator**: Violation details and navigation controls
- **Settings Panel**: RAG document management
- **Results Exporter**: JSON file generation and download

#### 5.2 State Management
- **File State**: Currently selected file and file list
- **Analysis State**: Violation data and processing status
- **UI State**: Selected violation, navigation position
- **Settings State**: RAG document configuration

#### 5.3 User Experience Flow
1. **Setup**: Upload style guide and RAG documents
2. **File Upload**: Select C++ files or folders for analysis
3. **Processing**: Sequential analysis of uploaded files
4. **Review**: Navigate between files and violations
5. **Export**: Save results as JSON files

## Quality and Performance Requirements

### 6.1 Performance Targets
- **Analysis Speed**: Process typical student assignment files (< 1000 lines) within reasonable time
- **UI Responsiveness**: Smooth navigation between violations and files
- **Memory Usage**: Efficient handling of multiple files in memory
- **Local Processing**: No external dependencies for core functionality

### 6.2 Error Handling
- **File Processing Errors**: Clear error messages for unreadable files
- **Style Guide Parsing**: Detailed error reporting for malformed style guides
- **Analysis Failures**: Graceful handling of LLM processing errors
- **User Input Validation**: Prevent invalid file uploads and configurations

### 6.3 Usability Requirements
- **Intuitive Navigation**: Easy switching between files and violations
- **Clear Visual Feedback**: Color coding and highlighting for different violation types
- **Informative Displays**: Helpful violation descriptions and style guide references
- **Efficient Workflow**: Streamlined process from upload to results export

## Security and Privacy

### 7.1 Data Security
- **Local Processing**: All data remains on local machine
- **No External Communication**: No data transmission to external services
- **File System Security**: Standard file system permissions for data access

### 7.2 Privacy Protection
- **No User Tracking**: No analytics or user behavior tracking
- **Local Storage Only**: All processed code and results stored locally
- **No Cloud Dependencies**: Fully offline-capable operation

## Success Criteria

### 8.1 Functional Success
- **Accurate Analysis**: Correctly identify style guide violations in C++ code
- **Complete Coverage**: Evaluate all specified violation types
- **Reliable Processing**: Handle various C++ code styles and structures
- **Useful Output**: Generate actionable violation reports

### 8.2 Educational Value
- **Time Savings**: Significantly reduce manual grading time
- **Consistency**: Provide consistent evaluation across all student submissions
- **Learning Aid**: Help students understand style guide requirements
- **Feedback Quality**: Generate clear, educational violation explanations

## Future Considerations

### 9.1 Potential Enhancements
- **Additional Languages**: Support for other programming languages
- **Advanced Analysis**: More sophisticated code quality metrics
- **Batch Reporting**: Aggregate reports across multiple student submissions
- **Integration Options**: Export formats for common grading systems

### 9.2 Scalability Considerations
- **Performance Optimization**: Improved processing speed for larger codebases
- **Memory Management**: Enhanced efficiency for processing many files
- **UI Enhancements**: Additional navigation and visualization features
- **Configuration Options**: More granular control over analysis parameters