#!/usr/bin/env python3

files = ['report_builder_md.py', 'report_builder_html.py', 'management_dashboard_generator.py', 'migration_helper.py', 'professional_dashboard_builder.py', 'comprehensive_dashboard_builder.py']

for filename in files:
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        cleaned_lines = []
        changes = 0

        for line in lines:
            original = line
            # Remove trailing whitespace but preserve newlines
            if line.endswith('\n'):
                cleaned = line.rstrip() + '\n'
            else:
                cleaned = line.rstrip()
            cleaned_lines.append(cleaned)
            if original != cleaned:
                changes += 1

        if changes > 0:
            with open(filename, 'w') as f:
                f.writelines(cleaned_lines)

        print(f'{filename}: {changes} lines cleaned')
    except Exception as e:
        print(f'{filename}: Error - {e}')