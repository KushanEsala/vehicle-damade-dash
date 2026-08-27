import re

def clean_script():
    script_path = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\generate_final_thesis_docx.py"
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Replacements for safe typography
    replacements = {
        "—": " - ",
        "–": " - ",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
    }

    for k, v in replacements.items():
        code = code.replace(k, v)

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Cleaned punctuation and special characters in generator script.")

if __name__ == "__main__":
    clean_script()
