#!/usr/bin/env python3
import subprocess
import sys

# Test if docling-tools recognizes qwenvl
result = subprocess.run(['docling-tools', 'models', 'download', '--help'], 
                       capture_output=True, text=True)

print("Output:", result.stdout)
print("Error:", result.stderr)

# Check if qwenvl is in the help text
if 'qwenvl' in result.stdout or 'qwenvl' in result.stderr:
    print("\n✓ qwenvl is recognized by docling-tools")
    sys.exit(0)
else:
    print("\n✗ qwenvl is NOT recognized by docling-tools")
    sys.exit(1)