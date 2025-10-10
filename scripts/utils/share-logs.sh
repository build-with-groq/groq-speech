#!/bin/bash

# Script to help share verbose logs for analysis

echo "🔍 Finding latest verbose log file..."

# Find the most recent verbose log file
LATEST_LOG=$(ls -t logs/verbose-*.log 2>/dev/null | head -n 1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ No verbose log files found in logs/ directory"
    echo "💡 Make sure to run: ./run-dev.sh --verbose"
    exit 1
fi

echo "📄 Latest log file: $LATEST_LOG"
echo "📊 Log file size: $(du -h "$LATEST_LOG" | cut -f1)"
echo "📅 Created: $(stat -f "%Sm" "$LATEST_LOG")"
echo ""

# Show last 20 lines as preview
echo "🔍 Last 20 lines of the log:"
echo "----------------------------------------"
tail -20 "$LATEST_LOG"
echo "----------------------------------------"
echo ""

# Ask if user wants to copy the file path
echo "📋 To share this log file for analysis:"
echo "   1. Copy the file: $LATEST_LOG"
echo "   2. Or run: cat $LATEST_LOG | pbcopy (to copy to clipboard)"
echo "   3. Or run: cat $LATEST_LOG (to display full content)"
echo ""

# Option to copy to clipboard if on macOS
if command -v pbcopy >/dev/null 2>&1; then
    read -p "📋 Copy log content to clipboard? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cat "$LATEST_LOG" | pbcopy
        echo "✅ Log content copied to clipboard!"
    fi
fi
