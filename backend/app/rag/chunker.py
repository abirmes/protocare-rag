import re
import tiktoken
from pathlib import Path
from typing import List
from langchain.schema import Document
from app.core.config import settings

tokenizer = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))


def _is_table_line(line: str) -> bool:
    return line.strip().startswith("|")


def _split_into_protocols(text: str) -> List[str]:
   
    lines = text.split("\n")
    cleaned_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        # Supprime "PÉDIATRIE   Version : 2" si la ligne suivante contient XXXXX
        if re.match(r"^PÉDIATRIE\s+Version\s*:", line):
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if "XXXXX" in next_line:
                i += 1
                continue
        cleaned_lines.append(line)
        i += 1

    cleaned_text = "\n".join(cleaned_lines)

    # Découpe sur les lignes contenant XXXXX
    protocols = re.split(r"(?=^.*XXXXX.*$)", cleaned_text, flags=re.MULTILINE)
    return [p.strip() for p in protocols if p.strip()]


def _get_protocol_name(text: str) -> str:
    match = re.search(r"XXXXX\s+(.+?)(?:\s+Validation|\s*$)", text, re.MULTILINE)
    return match.group(1).strip() if match else "Inconnu"


def _split_markdown_blocks(text: str) -> List[dict]:
    blocks = []
    lines = text.split("\n")
    current_block = {"type": None, "lines": []}

    for line in lines:
        is_table = _is_table_line(line)

        if is_table:
            if current_block["type"] == "text" and current_block["lines"]:
                blocks.append(current_block)
                current_block = {"type": None, "lines": []}
            current_block["type"] = "table"
            current_block["lines"].append(line)
        else:
            if current_block["type"] == "table" and current_block["lines"]:
                blocks.append(current_block)
                current_block = {"type": None, "lines": []}
            current_block["type"] = "text"
            current_block["lines"].append(line)

    if current_block["lines"]:
        blocks.append(current_block)

    return blocks


def _split_by_hierarchy(text: str) -> List[str]:
    max_tokens = settings.CHUNK_SIZE
    chunks = []

    sections = re.split(r"(?=^#{2,3} .+)", text, flags=re.MULTILINE)

    for section_block in sections:
        section_block = section_block.strip()
        if not section_block:
            continue

        if _count_tokens(section_block) <= max_tokens:
            chunks.append(section_block)
            continue

        paragraphs = section_block.split("\n\n")
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            combined = current + "\n\n" + para if current else para

            if _count_tokens(combined) <= max_tokens:
                current = combined
            else:
                if current:
                    chunks.append(current.strip())

                if _count_tokens(para) <= max_tokens:
                    current = para
                else:
                    sentences = re.split(r"(?<=\.) ", para)
                    current = ""
                    for sentence in sentences:
                        combined = current + " " + sentence if current else sentence
                        if _count_tokens(combined) <= max_tokens:
                            current = combined
                        else:
                            if current:
                                chunks.append(current.strip())
                            current = sentence
                    if current:
                        chunks.append(current.strip())
                    current = ""

        if current:
            chunks.append(current.strip())

    return [c for c in chunks if c]


def chunk_markdown(markdown_text: str, source: str = "document") -> List[Document]:

    protocols = _split_into_protocols(markdown_text)
    chunks = []
    chunk_index = 0

    for protocol_text in protocols:
        protocol_name = _get_protocol_name(protocol_text)
        current_header = "Document"

        blocks = _split_markdown_blocks(protocol_text)

        for block in blocks:
            content = "\n".join(block["lines"]).strip()
            if not content:
                continue

            header_match = re.findall(r"^#{1,3} .+", content, re.MULTILINE)
            if header_match:
                current_header = header_match[-1].strip()

            if block["type"] == "table":
                chunks.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": source,
                            "chunk_index": chunk_index,
                            "type": "table",
                            "section": current_header,
                            "protocol": protocol_name,
                        },
                    )
                )
                chunk_index += 1

            else:
                sub_chunks = _split_by_hierarchy(content)
                for sub in sub_chunks:
                    if sub.strip():
                        chunks.append(
                            Document(
                                page_content=sub,
                                metadata={
                                    "source": source,
                                    "chunk_index": chunk_index,
                                    "type": "text",
                                    "section": current_header,
                                    "protocol": protocol_name,
                                    "tokens": _count_tokens(sub),
                                },
                            )
                        )
                        chunk_index += 1

    table_count = sum(1 for c in chunks if c.metadata["type"] == "table")
    text_count = sum(1 for c in chunks if c.metadata["type"] == "text")
    print(f"{len(chunks)} chunks generated ({table_count} tables, {text_count} text blocks)")
    return chunks


def chunk_markdown_file(file_path: str) -> List[Document]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    text = path.read_text(encoding="utf-8")
    return chunk_markdown(text, source=path.name)