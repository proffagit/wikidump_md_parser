# Wikipedia XML Dump to Markdown Converter

A robust, high-performance Python tool for converting Wikipedia XML dumps into individual Markdown files with comprehensive wikitext parsing and advanced safeguards against complex nested structures.

## 🌟 Features

### Core Functionality
- **Fast XML Parsing**: Efficiently processes large Wikipedia XML dump files (multi-GB)
- **Individual Article Files**: Converts each Wikipedia article to a separate Markdown file
- **Comprehensive Wikitext Support**: Handles 15+ wikitext markup features
- **Metadata Preservation**: Includes page ID, source information, and word count
- **🛡️ Robust Processing**: Advanced safeguards prevent hangs on complex articles
- **⚡ Smart Fallbacks**: Graceful degradation ensures continuous processing
- **🔄 Timeout Protection**: Per-article processing limits prevent infinite loops

### Advanced Wikitext Parsing

#### 📝 Text Formatting
- **Bold**: `'''text'''` → `**text**`
- **Italic**: `''text''` → `*text*`
- **Bold Italic**: `'''''text'''''` → `***text***`
- **Strikethrough**: `<s>text</s>` → `~~text~~`
- **Subscript**: `<sub>text</sub>` → `_text_`
- **Superscript**: `<sup>text</sup>` → `^(text)`
- **Underline**: `<u>text</u>` → preserved as HTML

#### 🧮 Math and Chemistry Notation
- **Inline Math**: `<math>E = mc^2</math>` → `$E = mc^2$`
- **Block Math**: Multi-line equations → ````math` code blocks
- **Chemistry**: `<chem>H2SO4</chem>` → ````chemistry` code blocks
- **Alternative Chemistry**: `<ce>CO2</ce>` → ````chemistry` code blocks

#### 📊 Tables
- **Wiki Tables**: Complete conversion to Markdown table format
- **Headers**: Automatic header detection with separator rows
- **Complex Cells**: Handles nested formatting within cells
- **Multi-cell Rows**: Supports `!!` and `||` syntax

#### 📋 Lists and Structure
- **Nested Bullet Lists**: `*`, `**`, `***` → proper indentation
- **Numbered Lists**: `#`, `##`, `###` → numbered with indentation
- **Definition Lists**: `;term:definition` → **bold terms** with descriptions
- **Proper Nesting**: Maintains hierarchical structure

#### 🔗 Links
- **Internal Links**: `[[Article]]` → `[Article](Article)`
- **Piped Links**: `[[Article|Display]]` → `[Display](Article)`
- **Section Links**: `[[Article#Section]]` → `[Article#Section](Article#Section)`
- **External Links**: `[http://example.com Text]` → `[Text](http://example.com)`
- **Bare URLs**: Automatic link conversion

#### 🏗️ Advanced Features
- **Template Removal**: Comprehensive infobox and template cleanup with nested structure handling
- **🔄 Smart Template Processing**: Lazy fallback preserves content when complex parsing fails
- **Special Templates**: 
  - `{{main|Article}}` → `*See main article: [Article](Article)*`
  - Citation templates → Reference format
  - Quote templates → Blockquote format
- **🛡️ Robust Table Conversion**: 
  - Full markdown conversion for normal tables
  - Lazy text conversion for oversized/complex tables
  - Content preservation with simplified formatting
- **Code Preservation**: 
  - `<code>` → backticks
  - `<pre>` → code blocks
  - `<syntaxhighlight>` → language-specific code blocks
- **HTML Entity Conversion**: Complete support for named and numeric entities
- **Reference Removal**: Cleans `<ref>` tags while preserving content
- **Comment Removal**: Strips XML comments
- **Nowiki Preservation**: Maintains literal text without parsing

### 🛡️ Robustness & Safety Features

#### Anti-Hang Safeguards
- **Nesting Depth Limits**: Prevents infinite recursion on deeply nested templates (50-level max)
- **Iteration Limits**: Stops runaway loops in complex template parsing
- **Size Limits**: 
  - Articles >2MB: Skip complex processing, use basic cleanup
  - Articles >1MB: Use lazy template removal
  - Tables >50KB: Convert to simple text format
  - Tables >500 lines: Truncate with continuation notice
- **Per-Article Timeouts**: 30-second limit per article prevents individual hangs
- **Memory Protection**: Early detection and handling of memory-intensive content

#### Fallback Mechanisms
- **Lazy Template Processing**: When complex parsing fails, removes braces but preserves content
  - `{{cite book|title=Example|author=Author}}` → `cite book|title=Example|author=Author`
- **Progressive Degradation**: Multiple fallback levels ensure some output is always produced
- **Content Preservation**: Prioritizes readable output over perfect formatting
- **Error Recovery**: Continues processing entire dump even when individual articles fail

#### Real-World Testing
- **✅ Tested on Complex Articles**: Successfully handles problematic pages like "House Corrino" (Dune series)
- **✅ Handles Pathological Cases**: Safely processes malformed or extremely nested markup
- **✅ Large Table Support**: Processes tables with hundreds of rows and complex nested templates
- **✅ Memory Efficient**: Maintains low memory usage even with complex content

## 🚀 Installation

### Requirements
- Python 3.6+
- No external dependencies (uses only standard library)

### Setup
```bash
git clone <repository-url>
cd wikidump_md_parser
chmod +x wikidump_xml_to_markdown_fast.py
```

### Obtaining Wikipedia Dump Files
Download the latest Wikipedia XML dump from the official Wikimedia dumps:
- **English Wikipedia**: https://dumps.wikimedia.org/enwiki/
- **Other Languages**: https://dumps.wikimedia.org/ (browse to your preferred language)

Look for files named like `enwiki-YYYYMMDD-pages-articles.xml.bz2` - these contain the full article content. You'll need to extract the bz2 file before processing:

```bash
# Download (example - replace with current date)
wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2

# Extract
bunzip2 enwiki-latest-pages-articles.xml.bz2
```

## 📖 Usage

### Basic Usage
```bash
python3 wikidump_xml_to_markdown_fast.py path/to/wikipedia-dump.xml
```

### With Custom Output Directory
```bash
python3 wikidump_xml_to_markdown_fast.py wikipedia-dump.xml -o output_directory
```

### Command Line Options
- `xml_file`: Path to Wikipedia XML dump file (required)
- `-o, --output`: Output directory for markdown files (default: `wikipedia_articles`)

## 📊 Performance

### Optimization Features
- **Stream Processing**: Processes files without loading entirely into memory
- **Fast Page Detection**: Uses optimized `<page>` tag scanning
- **Selective Processing**: Skips redirects, disambiguation pages, and special namespaces
- **Progress Reporting**: Real-time statistics every 1000 articles
- **🛡️ Hang Prevention**: Multiple timeout and limit mechanisms
- **⚡ Smart Fallbacks**: Maintains processing speed even with complex content
- **🔄 Adaptive Processing**: Adjusts parsing strategy based on content complexity

### Typical Performance
- **Speed**: ~100-500 articles/second (depending on hardware and content complexity)
- **Memory**: Low memory footprint even for multi-GB files
- **Scalability**: Successfully tested on complete Wikipedia dumps
- **🛡️ Reliability**: Processes entire dumps without hanging on complex articles
- **⚡ Consistency**: Maintains steady performance through adaptive processing

## 📁 Output Format

Each article is saved as an individual Markdown file with:

```markdown
# Article Title

**Page ID:** 12345  
**Source:** Wikipedia XML Dump  
**Word Count:** 1500

---

[Converted article content in Markdown format]
```

### File Naming
- Article titles are cleaned for filesystem compatibility
- Invalid characters replaced with underscores
- Length limited to 200 characters
- Extension: `.md`

## 🔧 Processing Details

### Included Content
- ✅ Main article text
- ✅ Formatted content (bold, italic, etc.)
- ✅ Tables converted to Markdown
- ✅ Math equations
- ✅ Code blocks
- ✅ Lists and structures
- ✅ Links (internal and external)

### Excluded Content
- ❌ Infoboxes and templates
- ❌ Navigation boxes
- ❌ References and citations
- ❌ Category links
- ❌ File/image links
- ❌ Talk pages and meta pages
- ❌ Redirect pages
- ❌ Disambiguation pages

### Special Handling
- **Namespace Filtering**: Skips `File:`, `Category:`, `Template:`, `User:`, etc.
- **Content Validation**: Filters out articles shorter than 50 characters
- **🛡️ Robust Error Recovery**: Continues processing even if individual articles fail
- **⚡ Adaptive Processing**: Automatically adjusts parsing strategy for complex content
- **🔄 Fallback Processing**: Multiple levels of graceful degradation ensure continuous operation
- **⏱️ Timeout Management**: Per-article limits prevent hangs while preserving content quality

## 🧪 Testing

The project includes comprehensive tests to validate parsing accuracy and robustness:

```bash
# Test comprehensive parsing features
python3 test_comprehensive_parser.py

# Test complex nested structures (House Corrino scenario)
python3 test_complex_article.py
```

### Test Coverage
- Basic text formatting
- Math and chemistry notation
- Wiki tables (normal and oversized)
- Lists and indentation
- Headings
- Internal and external links
- Templates and infoboxes (including deeply nested)
- Code and preformatted text
- HTML elements and entities
- References and citations
- Complex nested markup
- **🛡️ Pathological cases**: Malformed and extremely complex structures
- **⚡ Performance limits**: Large content and timeout scenarios
- **🔄 Fallback mechanisms**: Lazy processing and content preservation

## 📈 Progress Monitoring

The tool provides detailed progress information with enhanced monitoring:

```
🚀 FAST Wikipedia XML Parser Starting...
📁 Input file: enwiki-latest-pages-articles.xml
📊 File size: 18.45 GB
📂 Output directory: /path/to/output

📖 Read 1M lines, found 45123 articles so far... (12.3s)
📈 PROGRESS: 50000 articles, 12000 redirects, 8000 skipped (487.2/sec)
   📄 Latest: 'Quantum mechanics in popular culture...'

🎉 MILESTONE: 100000 pages processed!
   ✅ Articles: 75000
   ⏱️  Time: 2.15 hours

⚠️  Warning: Complex template parsing timeout, using fallback
⚠️  Slow conversion: 'House Corrino' took 12.3s
✅ Lazy fallback regex used - template content preserved
```

### Enhanced Monitoring Features
- **Real-time Processing Stats**: Articles, redirects, skipped counts
- **Performance Metrics**: Processing rate and time estimates
- **Warning System**: Alerts for slow conversions and fallback usage
- **Memory Monitoring**: Automatic detection of memory-intensive articles
- **Timeout Tracking**: Reports on articles requiring fallback processing

## 🏗️ Architecture

### Core Components
1. **XML Parser**: Stream-based processing for memory efficiency
2. **Wikitext Converter**: Comprehensive markup transformation engine with fallback support
3. **🛡️ Template Engine**: Advanced template removal with nesting limits and timeout protection
4. **🔄 Fallback System**: Multi-level graceful degradation for complex content
5. **Link Processor**: Multi-format link conversion system
6. **Content Filter**: Intelligent content inclusion/exclusion logic
7. **⚡ Safety Monitor**: Real-time processing limits and timeout management

### Processing Pipeline
1. **Stream Parsing**: Extract pages from XML
2. **Content Filtering**: Skip unwanted page types
3. **Wikitext Conversion**: Transform markup to Markdown
4. **File Generation**: Create individual Markdown files
5. **Progress Reporting**: Update statistics

## 🤝 Contributing

### Areas for Enhancement
- Additional template handling
- More math notation support
- Enhanced table processing
- Performance optimizations
- Output format options

### Code Quality
- Comprehensive error handling
- Detailed logging and progress reporting
- Modular design for extensibility
- Performance-optimized algorithms

## 📄 License

This project is open source. Please check the license file for details.

## 🔍 Technical Details

### Dependencies
- `xml.etree.ElementTree`: XML processing
- `re`: Regular expression operations
- `html`: HTML entity decoding
- `pathlib`: File system operations
- `argparse`: Command line parsing

### Supported Wikipedia Formats
- **XML Dump Format**: Standard MediaWiki XML export format
- **Wikitext Version**: Compatible with current Wikipedia markup
- **Encoding**: UTF-8 support for international content

### System Requirements
- **Storage**: ~2-3x the size of input XML for output files
- **RAM**: Minimal memory usage (stream processing)
- **CPU**: Multi-core systems recommended for large dumps

## 📚 References

Based on official documentation:
- [MediaWiki Wikitext Specification](https://mediawiki.org/wiki/Wikitext)
- [WikiDump Parsing Guidelines](https://en.wikipedia.org/wiki/Help:Wikitext)
- [Math Extension Documentation](https://mediawiki.org/wiki/Extension:Math)
- [Wikipedia Style Guidelines](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style)

---

**Note**: This tool is designed for processing Wikipedia XML dumps and converting them to Markdown format for documentation, analysis, or archival purposes. It handles the complex wikitext markup comprehensively while maintaining content quality and readability.
