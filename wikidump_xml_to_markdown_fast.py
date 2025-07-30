#!/usr/bin/env python3
"""
Wikipedia XML dump to Markdown converter - COMPREHENSIVE EDITION
Parses Wikipedia XML dump and converts each article to individual MD files
with extensive wikitext parsing including math, templates, tables, and more.

ENHANCED FEATURES:
- Advanced math equation support (LaTeX -> markdown math blocks, inline/block detection)
- Chemistry notation support (<chem>, <ce> tags -> chemistry code blocks)
- Comprehensive template removal with special handling for citations, quotes, main links
- Enhanced table conversion to markdown format with complex cell parsing
- Complete HTML entity handling (named, numeric, hexadecimal)
- Proper nested list formatting (bullets, numbers, definitions)
- Advanced link conversion (internal, external, with sections, piped links)
- Citation and reference removal with content preservation
- Syntax highlighting preservation with language mapping
- Complex nested markup parsing with balanced brace handling
- HTML tag conversion (blockquotes, subscript, superscript, etc.)
- Nowiki content preservation
- Comment removal and cleanup

BASED ON OFFICIAL DOCUMENTATION:
- MediaWiki wikitext specification (mediawiki.org/wiki/Wikitext)
- WikiDump parsing guidelines (en.wikipedia.org/wiki/Help:Wikitext)
- Math extension documentation (mediawiki.org/wiki/Extension:Math)
- Wikipedia style guidelines for mathematics and chemistry

IMPROVEMENTS OVER BASIC VERSION:
- Handles 15+ wikitext features comprehensively
- Preserves important content while removing templates
- Advanced table parsing with cell formatting
- Proper math notation handling (inline vs block)
- Enhanced link processing with section support
- Better HTML entity conversion
- Robust nested structure parsing
"""

import xml.etree.ElementTree as ET
import argparse
import os
import re
import sys
import time
import html
import sqlite3
from pathlib import Path


def clean_filename(title):
    """Clean article title to create valid filename"""
    # Remove or replace invalid filename characters
    title = re.sub(r'[<>:"/\\|?*]', '_', title)
    # Remove leading/trailing whitespace and dots
    title = title.strip(' .')
    # Limit length to avoid filesystem issues
    if len(title) > 200:
        title = title[:200]
    return title


def init_database(db_path):
    """Initialize the SQLite database for storing articles"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id TEXT NOT NULL,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            content_size INTEGER,
            content BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(page_id)
        )
    ''')
    
    conn.commit()
    return conn


def wikitext_to_markdown(wikitext, timeout_seconds=30):
    """
    Convert wikitext markup to markdown with comprehensive parsing.
    Handles math, templates, tables, infoboxes, citations, and complex markup.
    Based on MediaWiki wikitext specification and WikiDump parsing guidelines.
    
    Args:
        wikitext: The wikitext content to convert
        timeout_seconds: Maximum time to spend on conversion (default: 30 seconds)
    """
    if not wikitext:
        return ""
    
    start_time = time.time()
    
    # Early check for extremely large articles
    if len(wikitext) > 2000000:  # 2MB limit
        print(f"⚠️  Warning: Article extremely large ({len(wikitext)} chars), skipping complex processing")
        # Return basic cleanup only
        simple_text = re.sub(r'\{\{[^}]*\}\}', '', wikitext)  # Remove templates
        simple_text = re.sub(r'<[^>]*>', '', simple_text)     # Remove HTML tags
        simple_text = re.sub(r'\[\[[^]]*\]\]', '', simple_text)  # Remove links
        return simple_text[:10000]  # Truncate to manageable size
    
    text = wikitext
    
    # Timeout check helper
    def check_timeout():
        if time.time() - start_time > timeout_seconds:
            print(f"⚠️  Warning: Article processing timeout ({timeout_seconds}s), using simplified conversion")
            return True
        return False
    
    # Step 1: Decode HTML entities first
    text = html.unescape(text)
    
    if check_timeout():
        # Apply simple template removal to what we have so far and return it
        partial_result = re.sub(r'\{\{([^}]*)\}\}', r'\1', text)  # Remove template braces, keep content
        return partial_result[:5000]  # Return truncated simplified text
    
    # Step 2: Handle special preservation tags (nowiki, pre, code, math, etc.)
    preserved_blocks = {}
    block_counter = 0
    
    # Preserve nowiki content
    def preserve_nowiki(match):
        nonlocal block_counter
        key = f"__PRESERVED_NOWIKI_{block_counter}__"
        preserved_blocks[key] = match.group(1)
        block_counter += 1
        return key
    
    text = re.sub(r'<nowiki>(.*?)</nowiki>', preserve_nowiki, text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<nowiki\s*/>', '', text, flags=re.IGNORECASE)
    
    # Preserve and convert math content - ENHANCED
    def preserve_math(match):
        nonlocal block_counter
        key = f"__PRESERVED_MATH_{block_counter}__"
        math_content_raw = match.group(1)  # Keep original content for newline detection
        math_content = math_content_raw.strip()  # Stripped content for output
        
        # Get math tag attributes if any
        full_match = match.group(0)
        is_display_block = 'display="block"' in full_match or 'display=block' in full_match
        is_chem = 'chem' in full_match.lower()
        
        # Convert to appropriate markdown math format
        if is_chem:
            preserved_blocks[key] = f"\n```chemistry\n{math_content}\n```\n"
        elif '\n' in math_content_raw or len(math_content) > 50 or is_display_block:
            # Block math - use markdown math block format (check raw content for newlines)
            preserved_blocks[key] = f"\n```math\n{math_content}\n```\n"
        else:
            # Inline math - use LaTeX inline format
            preserved_blocks[key] = f"${math_content}$"
        
        block_counter += 1
        return key
    
    # Handle various math tag formats
    text = re.sub(r'<math[^>]*>(.*?)</math>', preserve_math, text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<math\s+chem[^>]*>(.*?)</math>', preserve_math, text, flags=re.DOTALL | re.IGNORECASE)
    
    # Preserve and convert chemistry notation
    def preserve_chem(match):
        nonlocal block_counter
        key = f"__PRESERVED_CHEM_{block_counter}__"
        chem_content = match.group(1).strip()
        preserved_blocks[key] = f"\n```chemistry\n{chem_content}\n```\n"
        block_counter += 1
        return key
    
    text = re.sub(r'<chem[^>]*>(.*?)</chem>', preserve_chem, text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<ce[^>]*>(.*?)</ce>', preserve_chem, text, flags=re.DOTALL | re.IGNORECASE)
    
    # Preserve pre and code blocks
    def preserve_pre(match):
        nonlocal block_counter
        key = f"__PRESERVED_PRE_{block_counter}__"
        pre_content = match.group(1).strip()
        preserved_blocks[key] = f"\n```\n{pre_content}\n```\n"
        block_counter += 1
        return key
    
    text = re.sub(r'<pre[^>]*>(.*?)</pre>', preserve_pre, text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<code[^>]*>(.*?)</code>', lambda m: f"`{m.group(1)}`", text, flags=re.IGNORECASE)
    
    # Preserve syntaxhighlight blocks - ENHANCED
    def preserve_syntax(match):
        nonlocal block_counter
        key = f"__PRESERVED_SYNTAX_{block_counter}__"
        
        # Extract language and content more robustly
        full_tag = match.group(0)
        content = match.group(2) if len(match.groups()) >= 2 else match.group(1)
        
        # Try multiple patterns to extract language
        lang = 'text'  # default
        lang_patterns = [
            r'lang=["\']?([^"\'>\s]+)["\']?',
            r'language=["\']?([^"\'>\s]+)["\']?',
            r'<(?:syntaxhighlight|source)\s+([^>\s]+)(?:\s|>)'
        ]
        
        for pattern in lang_patterns:
            lang_match = re.search(pattern, full_tag, re.IGNORECASE)
            if lang_match:
                lang = lang_match.group(1).lower()
                break
        
        # Map some common language aliases
        lang_map = {
            'c++': 'cpp',
            'c#': 'csharp',
            'js': 'javascript',
            'py': 'python',
            'rb': 'ruby',
            'sh': 'bash',
            'shell': 'bash',
            'console': 'bash',
            'mysql': 'sql',
            'postgresql': 'sql',
            'html5': 'html',
            'xhtml': 'html',
            'xml': 'xml',
            'yaml': 'yaml',
            'yml': 'yaml'
        }
        
        lang = lang_map.get(lang, lang)
        preserved_blocks[key] = f"\n```{lang}\n{content.strip()}\n```\n"
        block_counter += 1
        return key
    
    # Handle various syntax highlighting tag formats
    text = re.sub(r'<syntaxhighlight[^>]*>(.*?)</syntaxhighlight>', 
                  preserve_syntax, text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<source[^>]*>(.*?)</source>', 
                  preserve_syntax, text, flags=re.DOTALL | re.IGNORECASE)
    
    # Handle simple code tags with language hints
    text = re.sub(r'<code\s+lang=["\']?([^"\'>\s]+)["\']?[^>]*>(.*?)</code>', 
                  lambda m: f"\n```{m.group(1)}\n{m.group(2).strip()}\n```\n", 
                  text, flags=re.DOTALL | re.IGNORECASE)
    
    # Step 3: Remove XML-style comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    if check_timeout():
        # Apply simple template removal and return
        simplified_result = re.sub(r'\{\{([^}]*)\}\}', r'\1', text)
        return simplified_result[:5000]
    
    # Step 4: Handle templates (complex nested structures) - ENHANCED
    # Remove infoboxes first (they start with {{ and contain | separators)
    def remove_complex_templates(text):
        """
        Advanced template removal with proper nesting support.
        Handles complex cases like nested templates, math within templates, etc.
        Added safeguards to prevent infinite loops and excessive processing.
        """
        # Early exit for very large texts to prevent memory issues
        if len(text) > 1000000:  # 1MB limit
            print(f"⚠️  Warning: Article too large ({len(text)} chars), using simple template processing")
            return re.sub(r'\{\{([^}]*)\}\}', r'\1', text)  # Lazy: just remove the braces, keep content
        
        # First pass: Handle special templates that might contain valuable content
        # Convert some citation templates to markdown-style references
        text = re.sub(r'\{\{cite\s+[^}]*\|?\s*title\s*=\s*([^|}]+)[^}]*\}\}', 
                     r'*(Reference: \1)*', text, flags=re.IGNORECASE)
        
        # Handle quote templates by preserving the quoted text
        text = re.sub(r'\{\{quote\s*\|\s*([^|}]+)[^}]*\}\}', 
                     r'> \1', text, flags=re.IGNORECASE)
        
        # Handle main template by converting to "See also" link
        text = re.sub(r'\{\{main\s*\|\s*([^|}]+)[^}]*\}\}', 
                     r'*See main article: [\1](\1)*', text, flags=re.IGNORECASE)
        
        # Enhanced balanced brace removal with proper nesting and safeguards
        result = []
        i = 0
        brace_stack = []
        max_iterations = len(text) * 2  # Safety limit
        iteration_count = 0
        max_nesting_depth = 50  # Prevent excessive nesting
        
        while i < len(text) and iteration_count < max_iterations:
            iteration_count += 1
            
            if i < len(text) - 1 and text[i:i+2] == '{{':
                # Check for excessive nesting depth
                if len(brace_stack) >= max_nesting_depth:
                    # Skip this template entirely - too deeply nested
                    i += 2
                    continue
                    
                if not brace_stack:  # Starting new template
                    template_start = i
                brace_stack.append(i)
                i += 2
            elif i < len(text) - 1 and text[i:i+2] == '}}':
                if brace_stack:
                    brace_stack.pop()
                    if not brace_stack:  # Closed outermost template
                        # Skip the entire template
                        i += 2
                        continue
                i += 2
            else:
                if not brace_stack:  # Not inside any template
                    result.append(text[i])
                i += 1
        
        # If we hit the iteration limit, fall back to simple removal
        if iteration_count >= max_iterations:
            print(f"⚠️  Warning: Complex template parsing timeout, using fallback")
            remaining_text = ''.join(result) + text[i:]
            return re.sub(r'\{\{([^}]*)\}\}', r'\1', remaining_text)  # Lazy: just remove braces, keep content
        
        return ''.join(result)
    
    text = remove_complex_templates(text)
    
    if check_timeout():
        # Apply simple template removal to remaining text
        final_result = re.sub(r'\{\{([^}]*)\}\}', r'\1', text)
        return final_result[:5000]
    
    # Step 5: Handle tables (convert to markdown tables where possible) - ENHANCED
    def clean_table_cell(content):
        """Clean a table cell of wikitext markup and HTML attributes"""
        if not content:
            return ''
        
        # Split by | to separate attributes from content
        parts = content.split('|')
        if len(parts) > 1:
            # Everything after the first | is the actual content
            cell_content = '|'.join(parts[1:])
        else:
            # No | separator, whole thing is content
            cell_content = content
        
        # Remove HTML attributes from the content part
        cell_content = re.sub(r'scope="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        cell_content = re.sub(r'rowspan="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        cell_content = re.sub(r'colspan="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        cell_content = re.sub(r'style="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        cell_content = re.sub(r'class="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        cell_content = re.sub(r'align="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        cell_content = re.sub(r'valign="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        cell_content = re.sub(r'width="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        cell_content = re.sub(r'height="[^"]*"', '', cell_content, flags=re.IGNORECASE)
        
        # Basic wikitext cleanup
        cell_content = re.sub(r"'''(.*?)'''", r'**\1**', cell_content)  # Bold
        cell_content = re.sub(r"''(.*?)''", r'*\1*', cell_content)     # Italic
        cell_content = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'[\2](\1)', cell_content)  # Links
        cell_content = re.sub(r'\[\[([^\]]+)\]\]', r'[\1](\1)', cell_content)  # Simple links
        
        return cell_content.strip()
    
    def convert_wikitable(match):
        """
        Enhanced table conversion with better cell parsing and formatting.
        Handles complex table structures, rowspan/colspan attributes, and nested markup.
        Added safeguards to prevent excessive processing time.
        """
        table_content = match.group(1)
        
        # Skip extremely large or complex tables - use lazy regex approach
        if len(table_content) > 50000:  # 50KB limit for tables
            # Lazy fallback: just clean up the table markup minimally
            simple_content = re.sub(r'\{\{([^}]*)\}\}', r'\1', table_content)  # Remove template braces, keep content
            simple_content = re.sub(r'\|\|', ' | ', simple_content)  # Convert table separators
            simple_content = re.sub(r'^\|', '', simple_content, flags=re.MULTILINE)  # Remove leading pipes
            simple_content = re.sub(r'\|-\s*', '\n', simple_content)  # Convert row separators to newlines
            simple_content = re.sub(r'^\!\s*', '**', simple_content, flags=re.MULTILINE)  # Convert headers to bold
            return '\n' + simple_content + '\n'
        
        lines = table_content.split('\n')
        
        # Limit number of lines processed in a table - use lazy approach for very long tables
        if len(lines) > 500:
            # For very long tables, use simple text conversion instead of full markdown
            truncated_content = '\n'.join(lines[:500])
            simple_content = re.sub(r'\{\{([^}]*)\}\}', r'\1', truncated_content)  # Remove template braces, keep content
            simple_content = re.sub(r'\|\|', ' | ', simple_content)  # Convert table separators
            simple_content = re.sub(r'^\|', '', simple_content, flags=re.MULTILINE)  # Remove leading pipes
            simple_content = re.sub(r'\|-\s*', '\n', simple_content)  # Convert row separators to newlines
            simple_content = re.sub(r'^\!\s*', '**', simple_content, flags=re.MULTILINE)  # Convert headers to bold
            return '\n' + simple_content + '\n... (table continues)\n'
        
        markdown_rows = []
        headers = []
        data_rows = []
        current_row = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('{|') or line.startswith('|}'):
                continue
            
            # Table row separator (ignore styling)
            if line.startswith('|-'):
                if current_row:
                    data_rows.append(current_row)
                current_row = []
                continue
            
            # Table header row (!)
            if line.startswith('!'):
                # Extract header content after removing attributes
                header_content = line[1:].strip()
                
                # Handle multiple headers in one line
                if '!!' in header_content:
                    header_cells = header_content.split('!!')
                else:
                    header_cells = [header_content]
                
                # Clean each header cell
                for header_cell in header_cells:
                    # Remove all HTML attributes using a more robust approach
                    clean_header = clean_table_cell(header_cell)
                    if clean_header.strip():
                        headers.append(clean_header.strip())
                continue
            
            # Table data row (|)
            if line.startswith('|'):
                # Extract cell content after removing attributes
                cell_content = line[1:].strip()
                
                # Handle multiple cells in one line
                if '||' in cell_content:
                    cell_parts = cell_content.split('||')
                else:
                    cell_parts = [cell_content]
                
                # Clean each cell
                for cell_part in cell_parts:
                    clean_cell = clean_table_cell(cell_part)
                    current_row.append(clean_cell.strip())
        
        # Add final row if exists
        if current_row:
            data_rows.append(current_row)
        
        # Build markdown table
        if headers:
            # Create header row
            markdown_rows.append('| ' + ' | '.join(headers) + ' |')
            markdown_rows.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
            
            # Add data rows, padding to match header count
            for row in data_rows:
                while len(row) < len(headers):
                    row.append('')
                # Truncate if row is longer than headers
                row = row[:len(headers)]
                markdown_rows.append('| ' + ' | '.join(row) + ' |')
        
        elif data_rows:
            # No headers, but we have data - create a simple table
            max_cols = max(len(row) for row in data_rows) if data_rows else 0
            if max_cols > 0:
                # Create generic headers
                markdown_rows.append('| ' + ' | '.join([f'Col {i+1}' for i in range(max_cols)]) + ' |')
                markdown_rows.append('| ' + ' | '.join(['---'] * max_cols) + ' |')
                
                # Add data rows
                for row in data_rows:
                    while len(row) < max_cols:
                        row.append('')
                    markdown_rows.append('| ' + ' | '.join(row) + ' |')
        
        if markdown_rows:
            return '\n' + '\n'.join(markdown_rows) + '\n'
        return ''
    
    # Convert wiki tables to markdown
    text = re.sub(r'\{\|(.*?)\|\}', convert_wikitable, text, flags=re.DOTALL)
    
    # ADDITIONAL: Remove any remaining malformed table syntax that wasn't caught
    # Remove scope attributes and other HTML table remnants
    text = re.sub(r'scope="[^"]*"', '', text, flags=re.IGNORECASE)
    text = re.sub(r'rowspan="[^"]*"', '', text, flags=re.IGNORECASE)
    text = re.sub(r'colspan="[^"]*"', '', text, flags=re.IGNORECASE)
    
    # Remove lines that are mostly table markup artifacts
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip lines that are mostly HTML table attributes
        stripped_line = line.strip()
        if (stripped_line.startswith('|') and 
            ('scope=' in stripped_line or 'rowspan=' in stripped_line or 'colspan=' in stripped_line) and
            len(re.sub(r'[|\s-]', '', stripped_line)) < 10):
            continue  # Skip this line as it's mostly table markup
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    
    if check_timeout():
        # Apply simple template removal to any remaining templates
        final_result = re.sub(r'\{\{([^}]*)\}\}', r'\1', text)
        return final_result[:5000]
    
    # Step 6: Remove remaining complex markup
    # Remove file and image references with all their parameters
    text = re.sub(r'\[\[(?:File|Image|Media):[^\]]*\]\]', '', text, flags=re.IGNORECASE)
    
    # Remove categories
    text = re.sub(r'\[\[Category:[^\]]*\]\]', '', text, flags=re.IGNORECASE)
    
    # Remove interlanguage links
    text = re.sub(r'\[\[[a-z]{2,3}(-[a-z]+)?:[^\]]*\]\]', '', text)
    
    # Step 7: Convert text formatting FIRST (before links and headings)
    # Handle nested formatting carefully - ENHANCED with better regex
    # Use a more robust approach that handles complex nested content
    
    # Handle bold and italic formatting with improved regex patterns
    # Process the entire text to handle multi-line formatting correctly
    
    # Handle bold italic first (5 apostrophes) - use DOTALL for multi-line
    text = re.sub(r"'''''(.*?)'''''", r'***\1***', text, flags=re.DOTALL)
    
    # Handle bold (3 apostrophes) - use DOTALL for multi-line, non-greedy
    text = re.sub(r"'''(.*?)'''", r'**\1**', text, flags=re.DOTALL)
    
    # Handle italic (2 apostrophes) - use DOTALL for multi-line, non-greedy
    text = re.sub(r"''(.*?)''", r'*\1*', text, flags=re.DOTALL)
    
    # Step 8: Handle small and big tags (after text formatting)
    text = re.sub(r'<small[^>]*>(.*?)</small>', r'\1', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<big[^>]*>(.*?)</big>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Handle subscript and superscript
    text = re.sub(r'<sub[^>]*>(.*?)</sub>', r'_\1_', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<sup[^>]*>(.*?)</sup>', r'^(\1)', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Step 9: Handle lists (with proper nesting) - MUST HAPPEN BEFORE HEADINGS!
    # Convert wiki lists to markdown with proper indentation
    lines = text.split('\n')
    converted_lines = []
    
    for line in lines:
        original_line = line
        stripped_line = line.lstrip()
        
        # Handle unordered lists with proper nesting (use stripped line to avoid leading space issues)
        if re.match(r'^(\*{1,})\s+(.+)$', stripped_line):
            match = re.match(r'^(\*{1,})\s+(.+)$', stripped_line)
            level = len(match.group(1)) - 1
            content = match.group(2).strip()
            if content:  # Only add non-empty content
                converted_lines.append('  ' * level + '- ' + content)
        # Handle ordered lists with proper nesting (use stripped line to avoid leading space issues)
        elif re.match(r'^(#{1,})\s+(.+)$', stripped_line):
            match = re.match(r'^(#{1,})\s+(.+)$', stripped_line)
            level = len(match.group(1)) - 1
            content = match.group(2).strip()
            if content:  # Only add non-empty content
                converted_lines.append('  ' * level + '1. ' + content)
        # Handle mixed ordered list with sub-items (#*) - Wikipedia specific syntax
        elif re.match(r'^(#{1,}\*+)\s+(.+)$', stripped_line):
            match = re.match(r'^(#{1,}\*+)\s+(.+)$', stripped_line)
            prefix = match.group(1)
            content = match.group(2).strip()
            # Count # symbols for base level, * symbols add to indentation
            hash_count = len([c for c in prefix if c == '#'])
            star_count = len([c for c in prefix if c == '*'])
            level = hash_count - 1 + star_count  # Combine both levels
            if content:  # Only add non-empty content
                # Use bullet points for sub-items in ordered lists
                converted_lines.append('  ' * level + '- ' + content)
        # Handle definition lists - IMPROVED (apply bold formatting to terms)
        elif re.match(r'^;\s*(.*?)(?::\s*(.*))?$', stripped_line):
            match = re.match(r'^;\s*(.*?)(?::\s*(.*))?$', stripped_line)
            term = match.group(1).strip()
            definition = match.group(2).strip() if match.group(2) else ""
            if term:
                # Make sure term is bold
                if not term.startswith('**') and not term.endswith('**'):
                    converted_lines.append(f'**{term}**')
                else:
                    converted_lines.append(term)
                if definition:
                    converted_lines.append(f': {definition}')
        elif re.match(r'^:\s*(.+)$', stripped_line):
            match = re.match(r'^:\s*(.+)$', stripped_line)
            content = match.group(1).strip()
            if content:
                converted_lines.append(f': {content}')
        # Skip lines that are already converted markdown headings (# followed by space at start)
        elif re.match(r'^#+\s+', stripped_line):
            converted_lines.append(original_line)
        # Skip wiki headings (= signs) - will be converted later
        elif re.match(r'^=+\s+.*\s+=+$', stripped_line.strip()):
            converted_lines.append(original_line)
        else:
            converted_lines.append(original_line)
    
    text = '\n'.join(converted_lines)
    
    # Step 10: Convert headings (= to #) - AFTER list processing to avoid conflicts
    text = re.sub(r'^======\s*(.*?)\s*======\s*$', r'###### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^=====\s*(.*?)\s*=====\s*$', r'##### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^====\s*(.*?)\s*====\s*$', r'#### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^===\s*(.*?)\s*===\s*$', r'### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^==\s*(.*?)\s*==\s*$', r'## \1', text, flags=re.MULTILINE)
    
    # Step 11: Handle links - ENHANCED (moved after text formatting and lists)
    # Handle various types of internal and external links with proper escaping
    
    # First, handle complex internal links with sections and custom text
    # [[Article#Section|Display text]] -> [Display text](Article#Section)
    text = re.sub(r'\[\[([^|\]#]+)#([^|\]]+)\|([^\]]+)\]\]', r'[\3](\1#\2)', text)
    
    # Handle piped links: [[Article|Display text]] -> [Display text](Article)
    text = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'[\2](\1)', text)
    
    # Handle simple links with sections: [[Article#Section]] -> [Article#Section](Article#Section)
    text = re.sub(r'\[\[([^|\]#]+)#([^\]]+)\]\]', r'[\1#\2](\1#\2)', text)
    
    # Handle simple internal links: [[Article]] -> [Article](Article)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'[\1](\1)', text)
    
    # External links with custom text: [URL Display text] -> [Display text](URL) - FIXED
    text = re.sub(r'\[(https?://[^\s\]]+)\s+([^\]]+)\]', r'[\2](\1)', text)
    text = re.sub(r'\[(ftp://[^\s\]]+)\s+([^\]]+)\]', r'[\2](\1)', text)
    
    # External links without text: [URL] -> [URL](URL) - FIXED
    text = re.sub(r'\[(https?://[^\s\]]+)\]', r'[\1](\1)', text)
    text = re.sub(r'\[(ftp://[^\s\]]+)\]', r'[\1](\1)', text)
    
    # Handle bare URLs (make them clickable) - IMPROVED to avoid double processing
    text = re.sub(r'(?<!\[|\()\bhttps?://[^\s\]<>\)]+(?!\]|\))', r'[\g<0>](\g<0>)', text)
    
    # Handle interwiki links (convert to external style)
    text = re.sub(r'\[\[([a-z]{2,3}):([^|\]]+)\|([^\]]+)\]\]', r'[\3](https://\1.wikipedia.org/wiki/\2)', text)
    text = re.sub(r'\[\[([a-z]{2,3}):([^\]]+)\]\]', r'[\2](https://\1.wikipedia.org/wiki/\2)', text)
    
    # Step 12: Remove reference tags and citations - ENHANCED
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<ref[^>]*/?>', '', text, flags=re.IGNORECASE)
    # Remove any remaining standalone ref tags
    text = re.sub(r'</ref>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<ref>', '', text, flags=re.IGNORECASE)
    
    # Step 13: Handle special characters and entities FIRST (before HTML tag removal)
    # Convert common HTML entities (but preserve some for display)
    entity_map = {
        '&nbsp;': ' ',
        '&ndash;': '–',
        '&mdash;': '—',
        '&hellip;': '…',
        '&lsquo;': ''',
        '&rsquo;': ''',
        '&ldquo;': '"',
        '&rdquo;': '"',
        '&quot;': '"',
        '&apos;': "'",
        '&amp;': '&',  # Process &amp; last to avoid double conversion
        '&lt;': '<',
        '&gt;': '>',
    }
    
    for entity, char in entity_map.items():
        text = text.replace(entity, char)
    
    # Convert numeric entities
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
    
    # Step 14: Handle remaining HTML tags AFTER entity conversion
    # Convert common HTML tags to markdown equivalents BEFORE removing all HTML
    # Handle strikethrough tags first 
    text = re.sub(r'<s[^>]*>(.*?)</s>', r'~~\1~~', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<del[^>]*>(.*?)</del>', r'~~\1~~', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<strike[^>]*>(.*?)</strike>', r'~~\1~~', text, flags=re.IGNORECASE | re.DOTALL)
    
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<hr\s*/?>', '\n---\n', text, flags=re.IGNORECASE)
    
    # Handle blockquotes
    def convert_blockquote(match):
        content = match.group(1).strip()
        if not content:
            return ''
        # Split by lines and add > prefix to each non-empty line
        lines = content.split('\n')
        quoted_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:
                quoted_lines.append(f'> {stripped_line}')
        return '\n'.join(quoted_lines)
    
    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', 
                  convert_blockquote, 
                  text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove other HTML tags AFTER converting entities (but preserve <u> tags)
    # Be more specific to avoid removing standalone < characters
    text = re.sub(r'<(?!/?u\b)[a-zA-Z][^>]*>', '', text)
    
    # Step 15: Clean up whitespace and formatting artifacts
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple blank lines
    # DON'T remove leading whitespace - it's needed for list indentation!
    text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)  # Trailing whitespace
    
    # Remove empty parentheses and brackets
    text = re.sub(r'\(\s*\)', '', text)
    text = re.sub(r'\[\s*\]', '', text)
    
    # Clean up malformed links
    text = re.sub(r'\]\([^)]*\)\(', '] (', text)
    text = re.sub(r'\)([A-Z])', r') \1', text)
    
    # Remove template artifacts
    text = re.sub(r'\{\{\{[^}]*\}\}\}', '', text)  # Template parameters
    text = re.sub(r'\{\{[^}]*\}\}', '', text)      # Remaining templates
    
    # Step 16: Restore preserved blocks
    for key, value in preserved_blocks.items():
        text = text.replace(key, value)
    
    # Step 17: Final cleanup
    # Fix spacing around preserved blocks
    text = re.sub(r'\n\n\n+', '\n\n', text)
    text = re.sub(r'^\s+|\s+$', '', text)
    
    # Fix common markdown formatting issues
    text = re.sub(r'\*\s+\*', '', text)  # Empty bold (with whitespace)
    text = re.sub(r'\*\*\s*\*\*', '', text)  # Empty bold markers
    text = re.sub(r'\*\*\*\s*\*\*\*', '', text)  # Empty bold italic markers
    text = re.sub(r'_\s*_', '', text)    # Empty italic
    text = re.sub(r'\[\]\([^)]*\)', '', text)  # Empty links
    
    return text


def parse_wikipedia_xml_fast(xml_file, output_dir="wikipedia_articles", db_conn=None):
    """Fast parsing focusing only on page content"""
    
    if db_conn:
        print(f"🚀 FAST Wikipedia XML Parser Starting (DATABASE MODE)...")
        print(f"📁 Input file: {xml_file}")
        print(f"📊 File size: {os.path.getsize(xml_file) / (1024**3):.2f} GB")
        print(f"💾 Database storage: articles will be stored in database")
        print("⚡ Using optimized parsing - looking for <page> tags only...\n")
    else:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"🚀 FAST Wikipedia XML Parser Starting...")
        print(f"📁 Input file: {xml_file}")
        print(f"📊 File size: {os.path.getsize(xml_file) / (1024**3):.2f} GB")
        print(f"📂 Output directory: {output_path.absolute()}")
        print("⚡ Using optimized parsing - looking for <page> tags only...\n")
    
    article_count = 0
    redirect_count = 0
    skipped_count = 0
    error_count = 0
    start_time = time.time()
    last_report_time = start_time
    
    try:
        # Open file and look for page elements specifically
        print("🔍 Scanning file for Wikipedia articles...")
        
        with open(xml_file, 'r', encoding='utf-8') as f:
            current_page = {}
            in_page = False
            in_title = False
            in_text = False
            in_id = False
            current_content = ""
            
            line_count = 0
            
            for line in f:
                line_count += 1
                
                # Progress every million lines
                if line_count % 1000000 == 0:
                    current_time = time.time()
                    elapsed = current_time - last_report_time
                    print(f"📖 Read {line_count//1000000}M lines, found {article_count} articles so far... ({elapsed:.1f}s)")
                    last_report_time = current_time
                
                line = line.strip()
                
                # Start of page
                if '<page>' in line:
                    in_page = True
                    current_page = {}
                    current_content = ""
                    if article_count == 0:
                        print("🎯 Found first <page> element! Starting article extraction...")
                    continue
                
                # End of page
                if '</page>' in line and in_page:
                    if 'title' in current_page and 'text' in current_page and 'id' in current_page:
                        if db_conn:
                            result = process_article_fast(current_page, None, db_conn)
                        else:
                            result = process_article_fast(current_page, output_path)
                        
                        if result == 'success':
                            article_count += 1
                        elif result == 'redirect':
                            redirect_count += 1
                        elif result == 'skipped':
                            skipped_count += 1
                        else:
                            error_count += 1
                        
                        # Report progress
                        total_processed = article_count + redirect_count + skipped_count + error_count
                        
                        if total_processed == 1:
                            print(f"✅ First article processed: '{current_page['title']}'")
                        
                        if total_processed % 1000 == 0:
                            elapsed = time.time() - start_time
                            rate = total_processed / elapsed if elapsed > 0 else 0
                            print(f"📈 PROGRESS: {article_count} articles, {redirect_count} redirects, {skipped_count} skipped ({rate:.1f}/sec)")
                            if article_count > 0:
                                print(f"   📄 Latest: '{current_page['title'][:60]}...'")
                        
                        if total_processed % 10000 == 0:
                            elapsed_hours = (time.time() - start_time) / 3600
                            print(f"\n🎉 MILESTONE: {total_processed} pages processed!")
                            print(f"   ✅ Articles: {article_count}")
                            print(f"   ⏱️  Time: {elapsed_hours:.2f} hours\n")
                    
                    in_page = False
                    continue
                
                if not in_page:
                    continue
                
                # Extract title
                if '<title>' in line:
                    title_match = re.search(r'<title>(.*?)</title>', line)
                    if title_match:
                        current_page['title'] = title_match.group(1)
                    in_title = '<title>' in line and '</title>' not in line
                    continue
                
                if in_title:
                    if '</title>' in line:
                        current_content += line.split('</title>')[0]
                        current_page['title'] = current_content
                        current_content = ""
                        in_title = False
                    else:
                        current_content += line
                    continue
                
                # Extract ID
                if '<id>' in line and 'id' not in current_page:
                    id_match = re.search(r'<id>(\d+)</id>', line)
                    if id_match:
                        current_page['id'] = id_match.group(1)
                    continue
                
                # Extract text content
                if '<text' in line:
                    text_match = re.search(r'<text[^>]*>(.*)', line)
                    if text_match:
                        current_content = text_match.group(1)
                        if '</text>' in current_content:
                            current_page['text'] = current_content.split('</text>')[0]
                        else:
                            in_text = True
                    continue
                
                if in_text:
                    if '</text>' in line:
                        current_content += line.split('</text>')[0]
                        current_page['text'] = current_content
                        current_content = ""
                        in_text = False
                    else:
                        current_content += line + '\n'
                    continue
        
        # Final statistics
        elapsed_total = time.time() - start_time
        print(f"\n🎊 PROCESSING COMPLETE! 🎊")
        print(f"📊 Final Statistics:")
        print(f"   ✅ Articles successfully converted: {article_count}")
        print(f"   ➡️  Redirects found: {redirect_count}")
        print(f"   ⏭️  Pages skipped: {skipped_count}")
        print(f"   ❌ Errors encountered: {error_count}")
        print(f"   📖 Total lines processed: {line_count:,}")
        print(f"   ⏱️  Total time: {elapsed_total/3600:.2f} hours")
        print(f"   🚀 Average rate: {(article_count)/elapsed_total:.1f} articles/sec")
        if db_conn:
            print(f"   💾 Storage: Database (articles stored in SQLite database)")
        else:
            print(f"   📂 Output directory: {output_path.absolute()}")
        
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\n⚠️  INTERRUPTED BY USER")
        print(f"📊 Progress when stopped:")
        print(f"   ✅ Articles converted: {article_count}")
        print(f"   ⏱️  Time elapsed: {elapsed/3600:.2f} hours")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        sys.exit(1)


def process_article_fast(page_data, output_path, db_conn=None):
    """Process a single article and save as markdown - fast version with error handling"""
    title = page_data.get('title', 'Untitled')
    text = page_data.get('text', '')
    page_id = page_data.get('id', 'unknown')
    
    try:
        # Skip redirect pages
        if text.lower().startswith('#redirect'):
            return 'redirect'
        
        # Skip special namespace pages
        if ':' in title:
            namespace = title.split(':')[0]
            if namespace in ['File', 'Category', 'Template', 'User', 'Wikipedia', 'Help', 'MediaWiki', 'Talk', 'User talk', 'Wikipedia talk', 'Module']:
                return 'skipped'
        
        # Skip disambiguation pages
        if '(disambiguation)' in title.lower():
            return 'skipped'
        
        # Skip extremely large articles (likely to cause issues)
        if len(text) > 3000000:  # 3MB limit
            print(f"⚠️  Skipping very large article: '{title}' ({len(text)} chars)")
            return 'skipped'
        
        # Create clean filename
        filename = clean_filename(title) + '.md'
        
        # Convert wikitext to markdown with timeout
        start_conversion = time.time()
        markdown_content = wikitext_to_markdown(text, timeout_seconds=30)
        conversion_time = time.time() - start_conversion
        
        # Log slow conversions
        if conversion_time > 10:
            print(f"⚠️  Slow conversion: '{title}' took {conversion_time:.1f}s")
        
        # Skip very short articles
        if len(markdown_content.strip()) < 50:
            return 'skipped'
    
    except Exception as e:
        print(f"❌ Error processing article '{title}': {e}")
        return 'error'
    
    # Create markdown file with metadata
    markdown_output = f"""# {title}

**Page ID:** {page_id}  
**Source:** Wikipedia XML Dump  
**Word Count:** {len(markdown_content.split())}

---

{markdown_content}
"""
    
    try:
        if db_conn:
            # Store in database
            cursor = db_conn.cursor()
            content_blob = markdown_output.encode('utf-8')
            content_size = len(content_blob)
            
            cursor.execute('''
                INSERT OR REPLACE INTO articles 
                (page_id, title, filename, content_size, content) 
                VALUES (?, ?, ?, ?, ?)
            ''', (page_id, title, filename, content_size, content_blob))
            
            db_conn.commit()
        else:
            # Store as file
            filepath = output_path / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
        
        return 'success'
    except Exception as e:
        if db_conn:
            print(f"❌ Error storing article '{title}' in database: {e}")
        else:
            print(f"❌ Error writing file for article '{title}': {e}")
        return 'error'


def main():
    parser = argparse.ArgumentParser(
        description='Convert Wikipedia XML dump to individual Markdown files - FAST VERSION'
    )
    parser.add_argument(
        'xml_file',
        help='Path to Wikipedia XML dump file'
    )
    parser.add_argument(
        '-o', '--output',
        default='wikipedia_articles',
        help='Output directory for markdown files or database path when using --database (default: wikipedia_articles)'
    )
    parser.add_argument(
        '--database',
        action='store_true',
        help='Enable database storage mode (stores articles in a database instead of files)'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.xml_file):
        print(f"Error: File '{args.xml_file}' not found.")
        sys.exit(1)
    
    # Handle database mode
    db_conn = None
    if args.database:
        db_path = args.output + '.db' if not args.output.endswith('.db') else args.output
        print(f"💾 Initializing database: {db_path}")
        db_conn = init_database(db_path)
    
    try:
        # Parse the XML file with fast method
        if db_conn:
            parse_wikipedia_xml_fast(args.xml_file, args.output, db_conn)
        else:
            parse_wikipedia_xml_fast(args.xml_file, args.output)
    finally:
        # Close database connection if it was opened
        if db_conn:
            db_conn.close()
            print(f"💾 Database connection closed")


if __name__ == '__main__':
    main()