#!/usr/bin/env python3


def clean_file(filename):
    """
    clean_file _summary_

    Parameters
    ----------
    filename : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    try:
        with open(filename, "r") as f:
            content = f.read()

        lines = content.splitlines(keepends=True)
        cleaned_lines = []
        changes = 0
        for line in lines:
            original = line
            cleaned = line.rstrip() + "\n" if line.endswith("\n") else line.rstrip()
            cleaned_lines.append(cleaned)
            if original != cleaned:
                changes += 1

        if changes > 0:
            with open(filename, "w") as f:
                f.writelines(cleaned_lines)

        return changes
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return 0


files = [
    "management_dashboard_generator.py",
    "migration_helper.py",
    "professional_dashboard_builder.py",
    "comprehensive_dashboard_builder.py",
]

total_changes = 0
for filename in files:
    changes = clean_file(filename)
    print(f"{filename}: {changes} lines cleaned")
    total_changes += changes

print(f"Total lines cleaned: {total_changes}")
