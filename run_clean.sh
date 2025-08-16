#!/bin/bash
# Simple script to clean trailing whitespace

# Clean each file using sed
sed -i 's/[[:space:]]*$//' report_builder_md.py
sed -i 's/[[:space:]]*$//' report_builder_html.py  
sed -i 's/[[:space:]]*$//' management_dashboard_generator.py
sed -i 's/[[:space:]]*$//' migration_helper.py
sed -i 's/[[:space:]]*$//' professional_dashboard_builder.py
sed -i 's/[[:space:]]*$//' comprehensive_dashboard_builder.py

echo "Trailing whitespace cleaned from all files"