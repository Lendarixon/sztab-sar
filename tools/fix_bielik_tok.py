"""Naprawa tokenizera Bielik v3 w pliku GGUF (BPE merge ranks + add_space_prefix=True)."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def fix_bielik_gguf(src: Path, dst: Path, tok_json: Path) -> bool:
    import gguf
    sys.path.insert(0, str(Path(gguf.__file__).parent / "scripts"))
    from gguf_new_metadata import MetadataDetails, copy_with_new_metadata  # type: ignore

    tj = json.loads(tok_json.read_text(encoding="utf-8"))
    rank: dict[str, int] = {}
    for i, m in enumerate(tj["model"]["merges"]):
        a, b = m.split(" ", 1) if isinstance(m, str) else m
        rank.setdefault(a + b, i)

    reader = gguf.GGUFReader(str(src), "r")
    tokens = reader.fields["tokenizer.ggml.tokens"].contents()
    scores = list(reader.fields["tokenizer.ggml.scores"].contents())
    changed = 0
    for i, t in enumerate(tokens):
        if t in rank:
            scores[i] = float(-rank[t])
            changed += 1

    arch = reader.fields["general.architecture"].contents()
    tmp = dst.with_suffix(".tmp.gguf")
    writer = gguf.GGUFWriter(str(tmp), arch=arch, endianess=reader.endianess)
    new_md = {
        "tokenizer.ggml.scores": MetadataDetails(gguf.GGUFValueType.ARRAY, scores, sub_type=gguf.GGUFValueType.FLOAT32),
        "tokenizer.ggml.add_space_prefix": MetadataDetails(gguf.GGUFValueType.BOOL, True),
    }
    copy_with_new_metadata(reader, writer, new_md, [])
    tmp.replace(dst)
    print(f"[fix_bielik_tok] {len(tokens)} tokenow, naprawiono {changed} -> {dst.name}")
    return True


if __name__ == "__main__":
    fix_bielik_gguf(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
