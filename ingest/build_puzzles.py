#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 tmp_extract/150套.txt 解析海龟汤数据，生成 puzzles/puzzles.json。

数据来源：用户提供的素材《海龟汤736套全文件》中的转录文本（题面+汤底成对，
以 59 个等号分隔，每题含两个段落：段1=汤面、段2=汤底）。
仅收录结构为「恰好两段」的题（题面与汤底分离清晰），剔除结构异常的题以保证严谨。
key_facts 与 hints 均从汤底原文按句切分得到，不新增任何文本。
"""
import re, json, sys
from pathlib import Path
from datetime import datetime, timezone

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "tmp_extract" / "150套.txt"
OUT = Path(__file__).resolve().parent.parent / "puzzles" / "puzzles.json"

SPLIT = "=" * 59

def sentences(text):
    """按中文/英文句末标点切分，过滤空串。"""
    parts = re.split(r"[。！？!?；;\n]", text)
    return [p.strip() for p in parts if p.strip()]

def difficulty(solution):
    n = len(solution)
    if n < 120:
        return "简单"
    if n < 320:
        return "中等"
    return "烧脑"

def main():
    raw = SRC.read_text(encoding="utf-8")
    blocks = [b.strip() for b in raw.split(SPLIT) if b.strip()]

    puzzles = []
    dropped = 0
    for idx, b in enumerate(blocks, 1):
        paras = [p.strip() for p in re.split(r"\n\s*\n", b) if p.strip()]
        if len(paras) != 2:        # 仅收录题面+汤底分离的干净配对
            dropped += 1
            continue
        surface, solution = paras[0], paras[1]
        if len(surface) < 8 or len(solution) < 8:   # 过短视为脏数据
            dropped += 1
            continue
        sents = sentences(solution)
        if not sents:
            dropped += 1
            continue
        # key_facts：汤底关键事实（判定「是/不是」的依据），最多 5 条，取前 5 句
        key_facts = sents[:5]
        # hints：递进式提示，仅取汤底偏前部的句子，避免直接剧透结尾反转
        hints = []
        if len(sents) >= 1:
            hints.append(sents[0])
        if len(sents) >= 4:
            mid = sents[len(sents) // 2]
            if mid not in hints:
                hints.append(mid)
        if len(sents) >= 6 and sents[-2] not in hints:
            hints.append(sents[-2])
        title = surface[:14] + ("…" if len(surface) > 14 else "")
        puzzles.append({
            "id": len(puzzles) + 1,
            "title": title,
            "difficulty": difficulty(solution),
            "surface": surface,
            "solution": solution,
            "key_facts": key_facts,
            "hints": hints,
            "source_file": "用户素材《海龟汤736套全文件》/ 150套.txt 转录",
        })

    meta = {
        "source": "用户提供的《海龟汤736套全文件》素材（经转录为纯文本）",
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": len(puzzles),
        "notes": (
            f"从原文 {len(blocks)} 个段落块中收录 {len(puzzles)} 题；"
            f"剔除 {dropped} 个结构异常块（段落数≠2 或过短），以保证每题均有完整汤底。"
            "surface 为面向玩家的谜面（不剧透），solution 为完整汤底，"
            "所有内容均来自原始转录，未新增任何情节。"
        ),
    }
    payload = {"meta": meta, "puzzles": puzzles}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    # 统计
    from collections import Counter
    dist = Counter(p["difficulty"] for p in puzzles)
    print(f"已写入 {OUT}")
    print(f"总题数: {len(puzzles)}")
    print(f"难度分布: {dict(dist)}")
    print(f"剔除异常块: {dropped}")
    avg_surface = sum(len(p["surface"]) for p in puzzles) / len(puzzles)
    print(f"汤面平均长度: {avg_surface:.0f} 字")

if __name__ == "__main__":
    main()
