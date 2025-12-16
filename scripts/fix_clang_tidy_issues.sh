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

# SOME/IP Stack - Fix Common clang-tidy Issues Script
# Automatically fixes some common clang-tidy issues

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔧 SOME/IP Stack - Fixing Common clang-tidy Issues"
echo "================================================="

# Function to add braces around single statements
fix_braces() {
    echo "  Adding braces around statements..."

    # Find files with missing braces
    find "$PROJECT_ROOT/include" "$PROJECT_ROOT/src" -name "*.cpp" -o -name "*.h" | \
    while read -r file; do
        # Add braces after if statements
        sed -i '' 's/if \(([^)]*)\)\s*\([^{;]*\);$/if \1 {\n        \2;\n    }/g' "$file"

        # Add braces after else statements
        sed -i '' 's/else\s*\([^{;]*\);$/else {\n        \1;\n    }/g' "$file"
    done
}

# Function to fix redundant member initializers
fix_redundant_initializers() {
    echo "  Removing redundant member initializers..."

    # Remove redundant default initializations
    find "$PROJECT_ROOT/src" -name "*.cpp" | \
    while read -r file; do
        # Remove redundant () initializers for default-constructible types
        sed -i '' 's/: \([a-zA-Z_][a-zA-Z0-9_]*\)(),/: /g' "$file"
    done
}

# Function to replace std::endl with \n
fix_endl_usage() {
    echo "  Replacing std::endl with \\n..."

    find "$PROJECT_ROOT/src" -name "*.cpp" | \
    while read -r file; do
        # Replace std::endl with \n in cout statements
        sed -i '' 's/std::endl/\n/g' "$file"
        # Add back std::endl for cases where we need flush
        sed -i '' 's/<< \\n/<< std::endl/g' "$file"
    done
}

# Function to use scoped_lock instead of lock_guard
fix_scoped_lock() {
    echo "  Replacing std::lock_guard with std::scoped_lock..."

    find "$PROJECT_ROOT/src" -name "*.cpp" -o -name "*.h" | \
    while read -r file; do
        # Replace lock_guard with scoped_lock
        sed -i '' 's/std::lock_guard/std::scoped_lock/g' "$file"
    done
}

# Function to use = default for trivial constructors
fix_default_constructors() {
    echo "  Adding = default to trivial constructors..."

    find "$PROJECT_ROOT/src" -name "*.cpp" | \
    while read -r file; do
        # This is complex to do automatically, just print a message
        echo "    Manual fix needed for trivial constructors in $file"
    done
}

# Function to add default member initializers
fix_default_member_init() {
    echo "  Adding default member initializers..."

    # This requires manual inspection, just provide guidance
    echo "    Manual fixes needed for default member initializers"
    echo "    Look for: SessionState state; -> SessionState state{SessionState::ACTIVE};"
}

# Main execution
echo "This script will attempt to fix common clang-tidy issues automatically."
echo "Some issues require manual intervention."
echo ""

read -p "Continue with automatic fixes? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 0
fi

echo ""
echo "🔧 Applying automatic fixes..."

fix_braces
fix_redundant_initializers
fix_endl_usage
fix_scoped_lock

echo ""
echo "✅ Automatic fixes applied!"
echo ""
echo "📋 Remaining manual fixes needed:"
echo ""

fix_default_constructors
fix_default_member_init

echo ""
echo "📖 For magic numbers, add constants like:"
echo "    static constexpr uint16_t SERVICE_ID_MASK = 0xFFFF;"
echo ""
echo "📖 For variable names, change:"
echo "    auto it = ... -> auto iterator = ..."
echo "    int id = ... -> int identifier = ..."
echo ""
echo "🔄 After manual fixes, re-run:"
echo "    ./scripts/run_tests.py --static-analysis"
