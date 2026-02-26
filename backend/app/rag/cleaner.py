

import re
from pathlib import Path


def _normalize_tables(text: str) -> str:
   
    lines = text.split("\n")
    cleaned_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Si on est dans un tableau
        if line.strip().startswith("|"):
            merged_line = line.rstrip()

            # Fusionner les lignes suivantes tant qu'elles appartiennent à la même cellule
            while i + 1 < len(lines):
                next_line = lines[i + 1]

                if next_line.strip().startswith("|"):
                    break
                if not next_line.strip():
                    break

                merged_line += " " + next_line.strip()
                i += 1

            # Nettoyage des espaces multiples
            merged_line = re.sub(r"\s{2,}", " ", merged_line)
            cleaned_lines.append(merged_line)

        else:
            cleaned_lines.append(line)

        i += 1

    return "\n".join(cleaned_lines)


def _remove_page_noise(text: str) -> str:
 
    # Supprime les lignes du type : "Guide des Protocoles ... 12"
    text = re.sub(r"^Guide des Protocoles.*\d+\s*$", "", text, flags=re.MULTILINE)

    # Supprime les lignes contenant uniquement un numéro (pagination)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    lines = text.split("\n")
    filtered_lines = []
    i = 0

    while i < len(lines):
        # Détection d'un bloc de titres successifs (page de couverture)
        if lines[i].strip().startswith("#"):
            j = i
            while j < len(lines) and (
                lines[j].strip().startswith("#") or not lines[j].strip()
            ):
                j += 1

            title_count = sum(
                1 for line in lines[i:j] if line.strip().startswith("#")
            )

            # Si trop de titres d'affilée → on considère que c'est du bruit
            if title_count >= 3:
                i = j
                continue

        filtered_lines.append(lines[i])
        i += 1

    text = "\n".join(filtered_lines)

    # Supprime les lignes vides en excès
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_markdown(text: str) -> str:
  
    text = _remove_page_noise(text)
    text = _normalize_tables(text)
    return text


def clean_markdown_file(input_path: str, output_path: str = None) -> str:

    input_file = Path(input_path)
    original_text = input_file.read_text(encoding="utf-8")

    cleaned_text = clean_markdown(original_text)

    output_file = Path(output_path) if output_path else input_file
    output_file.write_text(cleaned_text, encoding="utf-8")

    print(f"✓ Markdown nettoyé : {output_file}")
    print(f"  Avant : {len(original_text)} caractères")
    print(f"  Après : {len(cleaned_text)} caractères")

    return cleaned_text