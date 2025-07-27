# Wikipedia XML Dump to Markdown Converter

A comprehensive Python tool for converting Wikipedia XML dumps into individual Markdown files with extensive wikitext parsing capabilities.

## 🌟 Features

### Core Functionality
- **Fast XML Parsing**: Efficiently processes large Wikipedia XML dump files (multi-GB)
- **Individual Article Files**: Converts each Wikipedia article to a separate Markdown file
- **Comprehensive Wikitext Support**: Handles 15+ wikitext markup features
- **Metadata Preservation**: Includes page ID, source information, and word count

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
- **Template Removal**: Comprehensive infobox and template cleanup
- **Special Templates**: 
  - `{{main|Article}}` → `*See main article: [Article](Article)*`
  - Citation templates → Reference format
  - Quote templates → Blockquote format
- **Code Preservation**: 
  - `<code>` → backticks
  - `<pre>` → code blocks
  - `<syntaxhighlight>` → language-specific code blocks
- **HTML Entity Conversion**: Complete support for named and numeric entities
- **Reference Removal**: Cleans `<ref>` tags while preserving content
- **Comment Removal**: Strips XML comments
- **Nowiki Preservation**: Maintains literal text without parsing

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

### Typical Performance
- **Speed**: ~100-500 articles/second (depending on hardware)
- **Memory**: Low memory footprint even for multi-GB files
- **Scalability**: Successfully tested on complete Wikipedia dumps

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
- **Error Recovery**: Continues processing even if individual articles fail

## 🧪 Testing

The project includes comprehensive tests to validate parsing accuracy:

```bash
python3 test_comprehensive_parser.py
```

### Test Coverage
- Basic text formatting
- Math and chemistry notation
- Wiki tables
- Lists and indentation
- Headings
- Internal and external links
- Templates and infoboxes
- Code and preformatted text
- HTML elements and entities
- References and citations
- Complex nested markup

## 📈 Progress Monitoring

The tool provides detailed progress information:

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
```

## 🏗️ Architecture

### Core Components
1. **XML Parser**: Stream-based processing for memory efficiency
2. **Wikitext Converter**: Comprehensive markup transformation engine
3. **Template Engine**: Advanced template removal with nesting support
4. **Link Processor**: Multi-format link conversion system
5. **Content Filter**: Intelligent content inclusion/exclusion logic

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
