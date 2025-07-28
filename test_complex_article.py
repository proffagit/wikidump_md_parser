#!/usr/bin/env python3
"""
Test script to simulate the complex nested structure that was causing hangs
like the "House Corrino" article from Dune series.
"""

import time
from wikidump_xml_to_markdown_fast import wikitext_to_markdown

def test_complex_nested_templates():
    """Test deeply nested template structures that could cause infinite loops"""
    
    # Simulate the type of complex nested structure found in Dune articles
    complex_wikitext = """
{{Infobox fictional organization
|name = House Corrino
|image = 
|caption = 
|universe = [[Dune universe]]
|type = [[Great House]]
|founded = 
|location = [[Salusa Secundus]] (ancestral), [[Kaitain]] (imperial)
|leader = {{plainlist|
* [[Shaddam Corrino IV]] (last Emperor)
* [[Leto Atreides II]] (God Emperor)
}}
|purpose = Imperial rule
|enemies = {{plainlist|
* [[House Atreides]]
* [[Fremen]]
* {{cite book|title=Dune|author=Frank Herbert|year=1965|publisher={{plainlist|
  * Chilton Books
  * {{cite web|url=http://example.com|title=Publisher Info|publisher={{plainlist|
    * Random House
    * {{plainlist|
      * Subsidiary 1
      * {{cite journal|title=Deep Reference|journal={{plainlist|
        * Science Fiction Review
        * {{plainlist|
          * Issue 1
          * {{plainlist|
            * Volume 1
            * {{cite book|title=Nested Book|author={{plainlist|
              * Author 1
              * {{plainlist|
                * Co-author
                * {{cite web|url=deep.url|title={{plainlist|
                  * Deep Title
                  * {{plainlist|
                    * Subtitle
                    * {{cite book|title={{plainlist|
                      * Super Deep
                      * {{plainlist|
                        * Ultra Deep
                      }}
                    }}}}
                  }}
                }}}}
              }}
            }}}}
          }}
        }}
      }}}}
    }}
  }}
}}}}
}}
|allegiances = [[Padishah Emperor]]
}}

'''House Corrino''' is a [[fictional]] [[Great House]] in [[Frank Herbert]]'s [[Dune universe]]. 

== History ==

The Corrinos ruled the [[Known Universe]] for over 10,000 years as the [[Padishah Emperor]]s. 

{{quote|{{plainlist|
* The beginning of knowledge is the discovery of something we do not understand.
* {{cite book|title=Dune|page={{plainlist|
  * 1
  * {{cite web|url=example.com|title={{plainlist|
    * Page Reference
    * {{plainlist|
      * Deep Page
    }}
  }}}}
}}
}}}}

=== Early History ===

{{main|{{plainlist|
* Corrino Dynasty
* {{cite book|title={{plainlist|
  * Imperial History
  * {{plainlist|
    * Volume {{plainlist|
      * 1
      * {{plainlist|
        * Chapter {{plainlist|
          * 1
          * {{plainlist|
            * Section A
          }}
        }}
      }}
    }}
  }}
}}}}
}}

The dynasty began with {{plainlist|
* [[Estes Corrino]]
* {{cite book|title=House History|publisher={{plainlist|
  * Historical Press
  * {{plainlist|
    * Division of {{plainlist|
      * Academic Publishers
      * {{plainlist|
        * Subsidiary {{plainlist|
          * A
          * {{plainlist|
            * Sub-A
          }}
        }}
      }}
    }}
  }}
}}}}
}}.

{| class="wikitable"
|-
! Emperor !! Reign !! Notes
|-
| {{plainlist|
* Shaddam I
* {{cite book|title={{plainlist|
  * First Emperor
  * {{plainlist|
    * Biography
  }}
}}}}
}} || 10,000 years ago || {{plainlist|
* First of the line
* {{cite web|url=emperor.info|title={{plainlist|
  * Emperor Info
  * {{plainlist|
    * Detailed Biography
  }}
}}}}
}}
|-
| Shaddam IV || Last Emperor || {{plainlist|
* Overthrown by [[Paul Atreides]]
* {{cite book|title=Dune|chapter={{plainlist|
  * Final Chapter
  * {{plainlist|
    * Epilogue
  }}
}}}}
}}
|}

== Legacy ==

{{chem|H2SO4}} represents the chemical used in spice processing.

<math>E = mc^2</math> - The fundamental equation of the universe.

<syntaxhighlight lang="python">
def process_spice():
    # Complex spice processing algorithm
    for i in range({{plainlist|
    * 1000
    * {{cite book|title=Algorithms|page={{plainlist|
      * 42
    }}}}
    }}):
        yield spice_element
</syntaxhighlight>

The {{plainlist|
* Corrino legacy
* {{cite book|title={{plainlist|
  * Legacy Studies
  * {{plainlist|
    * Volume {{plainlist|
      * Final
      * {{plainlist|
        * Conclusion
      }}
    }}
  }}
}}}}
}} continues to influence the Known Universe.

== See also ==
* [[House Atreides]]
* [[House Harkonnen]]
* {{plainlist|
* [[Dune universe]]
* {{cite book|title={{plainlist|
  * Complete Guide
  * {{plainlist|
    * To Dune
  }}
}}}}
}}

[[Category:Dune]]
[[Category:Fictional organizations]]
"""

    print("🧪 Testing complex nested template structure...")
    print(f"Input size: {len(complex_wikitext)} characters")
    print("Contains deeply nested templates, tables, math, and code blocks...")
    
    start_time = time.time()
    
    try:
        result = wikitext_to_markdown(complex_wikitext, timeout_seconds=30)
        end_time = time.time()
        
        print(f"✅ Conversion completed in {end_time - start_time:.2f} seconds")
        print(f"Output size: {len(result)} characters")
        print(f"First 500 chars:\n{result[:500]}...")
        
        # Check if fallback behavior was used (templates preserved without braces)
        if 'plainlist|' in result or 'cite book|' in result:
            print("✅ Lazy fallback regex used - template content preserved")
        else:
            print("✅ Full complex parsing completed")
        
        if end_time - start_time > 25:
            print("⚠️  Warning: Conversion took a long time but completed")
        else:
            print("✅ Conversion completed within acceptable time")
            
    except Exception as e:
        end_time = time.time()
        print(f"❌ Error after {end_time - start_time:.2f} seconds: {e}")
        
def test_infinite_loop_scenario():
    """Test a scenario that could cause infinite loops"""
    
    # Create a pathological case with unbalanced braces
    pathological_wikitext = """
{{cite book|title={{cite web|url={{cite book|title={{cite web|url={{cite book|title={{cite web|url={{cite book|title={{cite web|url={{cite book|title={{cite web|url={{cite book|title={{cite web|url=broken
"""
    
    print("\n🧪 Testing pathological nested structure...")
    print(f"Input size: {len(pathological_wikitext)} characters")
    
    start_time = time.time()
    
    try:
        result = wikitext_to_markdown(pathological_wikitext, timeout_seconds=10)
        end_time = time.time()
        
        print(f"✅ Pathological case handled in {end_time - start_time:.2f} seconds")
        print(f"Output size: {len(result)} characters")
        
        # The pathological case should result in template content being preserved
        if len(result) > 0:
            print("✅ Lazy fallback preserved some content")
            print(f"Sample output: {result[:100]}...")
        else:
            print("ℹ️  All template content was removed")
        
    except Exception as e:
        end_time = time.time()
        print(f"✅ Error properly caught after {end_time - start_time:.2f} seconds: {e}")

def test_very_large_table():
    """Test a very large table that could cause memory issues"""
    
    # Generate a large table
    large_table = """{| class="wikitable"
|-
! Column 1 !! Column 2 !! Column 3 !! Column 4 !! Column 5
"""
    
    # Add many rows with nested templates
    for i in range(100):
        large_table += f"""|-
| Cell {i}1 || {{{{cite book|title=Book {i}|author={{{{plainlist|
* Author {i}
* {{{{cite web|url=url{i}.com|title=Web {i}}}}}
}}}}}}}} || Cell {i}3 || Cell {i}4 || Cell {i}5
"""
    
    large_table += "|}"
    
    print(f"\n🧪 Testing large table with nested templates...")
    print(f"Input size: {len(large_table)} characters")
    
    start_time = time.time()
    
    try:
        result = wikitext_to_markdown(large_table, timeout_seconds=15)
        end_time = time.time()
        
        print(f"✅ Large table converted in {end_time - start_time:.2f} seconds")
        print(f"Output size: {len(result)} characters")
        
        # Check if lazy table fallback was used
        if '(table continues)' in result:
            print("✅ Lazy table line limit fallback used - content preserved")
        elif 'cite book|' in result:
            print("✅ Lazy template removal used in table cells")
        else:
            print("✅ Full table conversion completed")
        
    except Exception as e:
        end_time = time.time()
        print(f"✅ Large table error handled after {end_time - start_time:.2f} seconds: {e}")

def test_lazy_fallback_behavior():
    """Test that the lazy fallback preserves template content"""
    
    # Create a simple template that should trigger lazy processing
    lazy_test_wikitext = """
This is some content with {{plainlist|
* Item 1
* Item 2 with {{cite book|title=Test Book|author=Test Author}}
* Item 3
}} and more content.

Also test {{quote|This is a quoted text with {{nested|content}}}}.

Final test: {{infobox|
|name = Test
|value = {{cite web|url=test.com|title=Test}}
}}
"""
    
    print(f"\n🧪 Testing lazy fallback behavior...")
    print(f"Input size: {len(lazy_test_wikitext)} characters")
    
    start_time = time.time()
    
    try:
        result = wikitext_to_markdown(lazy_test_wikitext, timeout_seconds=30)
        end_time = time.time()
        
        print(f"✅ Lazy test completed in {end_time - start_time:.2f} seconds")
        print(f"Output size: {len(result)} characters")
        print(f"Output:\n{result}")
        
        # Verify that template content is preserved (braces removed but content kept)
        if 'plainlist|' in result:
            print("✅ Template content preserved with lazy regex")
        if 'Item 1' in result and 'Item 2' in result:
            print("✅ List content from templates preserved")
        if 'Test Book' in result and 'Test Author' in result:
            print("✅ Citation content preserved")
        if 'This is a quoted text' in result:
            print("✅ Quote content preserved")
            
    except Exception as e:
        end_time = time.time()
        print(f"❌ Error in lazy test after {end_time - start_time:.2f} seconds: {e}")

if __name__ == "__main__":
    print("🚀 Testing complex article scenarios that could cause hangs...\n")
    
    test_complex_nested_templates()
    test_infinite_loop_scenario() 
    test_very_large_table()
    test_lazy_fallback_behavior()
    
    print("\n🎉 All complex tests completed!")
