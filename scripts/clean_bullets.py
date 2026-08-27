import re

def clean_bullets():
    script_path = r"d:\FinalProject 2026\vehicle_damade_dash_cloned\scripts\generate_final_thesis_docx.py"
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Replace all unicode bullets and strange markers with clean ASCII bullet points
    code = code.replace("•", "-")
    code = code.replace("", "-")
    code = code.replace("\u2022", "-")
    code = code.replace("\ufffd", "-")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Successfully replaced all bullets with clean ASCII dashes.")

if __name__ == "__main__":
    clean_bullets()
