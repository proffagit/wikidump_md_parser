#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced wikitext_to_markdown parser.
Tests all major wikitext features including math, tables, templates, and complex markup.

Based on official MediaWiki documentation and Wikipedia style guidelines.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import the parser
sys.path.insert(0, str(Path(__file__).parent))

from wikidump_xml_to_markdown_fast import wikitext_to_markdown


def run_test(name, wikitext, expected_keywords=None):
    """Run a single test case and display results"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"INPUT WIKITEXT:\n{wikitext}")
    print(f"\n{'-'*40}")
    print("OUTPUT MARKDOWN:")
    
    result = wikitext_to_markdown(wikitext)
    print(result)
    
    if expected_keywords:
        print(f"\n{'-'*40}")
        print("VALIDATION:")
        for keyword in expected_keywords:
            if keyword in result:
                print(f"✅ Contains '{keyword}'")
            else:
                print(f"❌ Missing '{keyword}'")
    
    return result


def main():
    """Run comprehensive tests for the wikitext parser"""
    print("🧪 COMPREHENSIVE WIKITEXT PARSER TESTS")
    print("Based on MediaWiki documentation and Wikipedia guidelines")
    print("=" * 70)
    
    # Test 1: Basic formatting
    run_test(
        "Basic Text Formatting",
        """This is '''bold text''' and ''italic text'' and '''''bold italic'''''.
        
Text can also have <u>underlined</u>, <s>strikethrough</s>, <sub>subscript</sub>, and <sup>superscript</sup> formatting.""",
        ["**bold text**", "*italic text*", "***bold italic***", "<u>underlined</u>", "~~strikethrough~~"]
    )
    
    # Test 2: Math equations
    run_test(
        "Math and Chemistry Notation",
        """Here is an inline math equation: <math>E = mc^2</math>
        
And here's a block equation:
<math>
\\sum_{i=1}^{n} x_i = \\frac{n(n+1)}{2}
</math>

Chemistry notation: <chem>H2SO4 + 2NaOH -> Na2SO4 + 2H2O</chem>

Alternative chemistry: <ce>CO2 + H2O -> H2CO3</ce>""",
        ["```math", "E = mc^2", "```chemistry", "H2SO4"]
    )
    
    # Test 3: Tables
    run_test(
        "Wiki Tables",
        """{| class="wikitable"
|-
! Header 1 !! Header 2 !! Header 3
|-
| Cell 1 || Cell 2 || Cell 3
|-
| Row 2, Col 1 || Row 2, Col 2 || Row 2, Col 3
|}""",
        ["| Header 1 |", "| Cell 1 |", "| --- |"]
    )
    
    # Test 4: Lists
    run_test(
        "Lists and Indentation",
        """* First level bullet
** Second level bullet
*** Third level bullet
* Another first level

# First numbered item
## Sub-numbered item
### Sub-sub-numbered item
# Second numbered item

; Definition term
: Definition description
: Another description
; Another term
: Its description""",
        ["- First level bullet", "  - Second level bullet", "1. First numbered item", "**Definition term**"]
    )
    
    # Test 5: Headings
    run_test(
        "Headings",
        """== Level 2 Heading ==
=== Level 3 Heading ===
==== Level 4 Heading ====
===== Level 5 Heading =====
====== Level 6 Heading ======""",
        ["## Level 2 Heading", "### Level 3 Heading", "###### Level 6 Heading"]
    )
    
    # Test 6: Links
    run_test(
        "Internal and External Links",
        """Here are various link types:
[[Article Name]] - simple internal link
[[Article Name|Display Text]] - internal link with custom text
[[Article Name#Section|Display Text]] - link to section
[http://example.com External Link] - external with text
[http://example.com] - external without text
[[Category:Some Category]] - category link (should be removed)
[[File:Example.jpg|thumb|Caption]] - file link (should be removed)""",
        ["[Article Name](Article Name)", "[Display Text](Article Name)", "[External Link](http://example.com)"]
    )
    
    # Test 7: Templates and infoboxes
    run_test(
        "Templates and Infoboxes",
        """{{Infobox person
| name = John Doe
| birth_date = {{birth date|1980|1|1}}
| occupation = {{plainlist|
* Engineer
* Writer
}}
}}

Some text with a {{template|parameter1|parameter2}} in the middle.

{{main|Main Article}}

More text after templates.""",
        ["Some text", "in the middle", "More text after templates"]
    )
    
    # Test 8: Code and preformatted text
    run_test(
        "Code and Preformatted Text",
        """Here's some inline <code>code text</code> in a sentence.

<pre>
This is preformatted text
    with preserved spacing
        and indentation
</pre>

<syntaxhighlight lang="python">
def hello_world():
    print("Hello, World!")
    return True
</syntaxhighlight>

<nowiki>This text should not be parsed: '''no bold''' and [[no links]]</nowiki>""",
        ["`code text`", "```", "def hello_world()", "```python", "This text should not be parsed"]
    )
    
    # Test 9: HTML elements and entities
    run_test(
        "HTML Elements and Entities",
        """Text with <br> line breaks and <hr> horizontal rules.

<blockquote>
This is a blockquote
with multiple lines
</blockquote>

Special characters: &amp; &lt; &gt; &quot; &apos; &nbsp; &ndash; &mdash;

Numeric entities: &#64; &#x41; for @ and A

<!-- This is a comment and should be removed -->

Text after comment.""",
        ["> This is a blockquote", "&", "<", ">", "@", "A", "Text after comment"]
    )
    
    # Test 10: References and citations
    run_test(
        "References and Citations",
        """This is text with a reference<ref>This is a reference that should be removed</ref> in it.

More text with another reference.<ref name="example">Named reference</ref>

Text with self-closing reference.<ref name="example" />

Final text after references.""",
        ["This is text with a reference in it", "More text with another reference", "Final text after references"]
    )
    
    # Test 11: Complex nested markup
    run_test(
        "Complex Nested Markup",
        """{{complex template|
param1='''Bold text''' with ''italic'' inside
|param2=[[Link]] and [http://example.com external]
|math=<math>x^2 + y^2 = z^2</math>
}}

Text outside template with '''bold containing [[link|link text]]''' formatting.

{| class="wikitable"
|-
! Header with '''bold''' !! Header with ''italic''
|-
| Cell with [[internal link]] || Cell with <math>E=mc^2</math>
|}""",
        ["Text outside template", "**bold containing [link text](link)**"]
    )
    
    print("\n" + "="*70)
    print("🎉 ALL TESTS COMPLETED!")
    print("Review the outputs above to verify correct parsing.")
    print("="*70)


if __name__ == "__main__":
    main()
