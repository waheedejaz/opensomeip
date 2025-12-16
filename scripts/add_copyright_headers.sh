#!/bin/bash
################################################################################
# Copyright (c) 2025 Vinicius Tadeu Zein
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
################################################################################

# SOME/IP Stack - Add Copyright Headers Script
# Adds Apache 2.0 license copyright headers to all source files

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Copyright header template
read -r -d '' COPYRIGHT_HEADER << 'EOF'
/*
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 */

EOF

echo "SOME/IP Stack - Adding Copyright Headers"
echo "========================================"

# Function to add copyright to a file
add_copyright() {
    local file="$1"
    local ext="${file##*.}"

    echo "Processing: $file"

    # Check if file already has copyright header
    if head -20 "$file" | grep -q "Copyright.*2024"; then
        echo "  ✓ Already has copyright header"
        return
    fi

    # Create temporary file
    local temp_file="${file}.tmp"

    # Add copyright header to all files (preserve existing structure)
    echo "$COPYRIGHT_HEADER" > "$temp_file"
    echo "" >> "$temp_file"
    cat "$file" >> "$temp_file"

    # Replace original file
    mv "$temp_file" "$file"
    echo "  ✓ Added copyright header"
}

# Process all source files
echo "Adding copyright headers to source files..."
find "$PROJECT_ROOT/include" "$PROJECT_ROOT/src" "$PROJECT_ROOT/examples" "$PROJECT_ROOT/tests" \
    -name "*.h" -o -name "*.cpp" -o -name "*.hpp" -o -name "*.cc" -o -name "*.py" | \
while read -r file; do
    add_copyright "$file"
done

echo ""
echo "Copyright headers added! 📄"
echo ""
echo "Note: Please update [Your Name/Organization] in the copyright header"
echo "      with your actual name/organization before publishing."
