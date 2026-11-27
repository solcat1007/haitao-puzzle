#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海龟汤题库工具 v2.0 — 分类检索 / 提示系统 / 随机抽题
=====================================================
零依赖，仅用 Python 标准库，读取 puzzles/puzzles.json。

注意：本工具**不新增、不改写任何谜题内容**，只读取现有题库，
严格遵守 DATA_NOTICE.md 中的使用边界。

用法示例：
  python puzzle_tools.py --stats                     # 题库统计
  python puzzle_tools.py --list --difficulty 简单     # 按难度列出
  python puzzle_tools.py --search "医院"              # 关键词检索
  python puzzle_tools.py --id 42 --no-solution       # 只看汤面（防剧透）
  python puzzle_tools.py --id 42 --hint 1            # 逐级提示（第 1 条）
  python puzzle_tools.py --random --difficulty 烧脑   # 随机抽题
  python puzzle_tools.py --easter                    # 隐藏彩蛋
"""

import argparse
import json
import random
import sys
from pathlib import Path

PUZZLE_FILE = Path(__file__).resolve().parent / "puzzles" / "puzzles.json"


def load_puzzles(path=PUZZLE_FILE):
    """加载题库，返回 (meta, puzzles)"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("meta", {}), data.get("puzzles", [])


def cmd_stats(puzzles):
    """v2.0：题库统计（按难度 / 提示数 / 关键事实数）"""
    from collections import Counter
    by_diff = Counter(p.get("difficulty", "未知") for p in puzzles)
    print(f"题库总数：{len(puzzles)}")
    for diff in ("简单", "中等", "烧脑"):
        if diff in by_diff:
            print(f"  {diff}：{by_diff[diff]} 道")
    avg_hints = sum(len(p.get("hints", [])) for p in puzzles) / max(1, len(puzzles))
    avg_facts = sum(len(p.get("key_facts", [])) for p in puzzles) / max(1, len(puzzles))
    print(f"平均提示数：{avg_hints:.1f}    平均关键事实数：{avg_facts:.1f}")
    no_solution = [p["id"] for p in puzzles if not p.get("solution")]
    print(f"缺少汤底的题目：{len(no_solution)}" +
          (f"（id: {no_solution[:10]}）" if no_solution else " — 全部完整"))


def cmd_list(puzzles, difficulty=None, limit=20):
    """v2.0：按难度分类检索题目列表"""
    items = [p for p in puzzles if not difficulty or p.get("difficulty") == difficulty]
    for p in items[:limit]:
        print(f"#{p['id']:<4} [{p.get('difficulty', '?')}] {p.get('title', '')}")
    if len(items) > limit:
        print(f"... 还有 {len(items) - limit} 道（可调 --limit）")


def cmd_search(puzzles, keyword, field="all", limit=20):
    """v2.0：关键词检索，可指定字段 surface/title/solution/all"""
    fields = {"surface", "title", "solution", "all"}
    if field not in fields:
        raise ValueError(f"未知字段: {field}")
    hits = []
    for p in puzzles:
        haystack = " ".join(str(p.get(f, "")) for f in
                            (("surface", "title", "solution") if field == "all" else (field,)))
        if keyword.lower() in haystack.lower():
            hits.append(p)
    print(f"检索“{keyword}”命中 {len(hits)} 道：")
    for p in hits[:limit]:
        print(f"#{p['id']:<4} [{p.get('difficulty', '?')}] {p.get('title', '')}")
    if len(hits) > limit:
        print(f"... 还有 {len(hits) - limit} 道")


def cmd_show(p, show_solution=False, hint=0):
    """v2.0：展示题目。默认不剧透汤底；--hint N 只给出第 N 条递进提示"""
    print(f"#{p['id']} [{p.get('difficulty', '?')}] {p.get('title', '')}")
    print("【汤面】", p.get("surface", ""))
    hints = p.get("hints", [])
    if hint:
        if not hints:
            print("（本题暂无提示）")
        else:
            idx = min(hint, len(hints)) - 1
            print(f"【提示 {idx + 1}/{len(hints)}】", hints[idx])
            if idx + 1 < len(hints):
                print(f"（还有 {len(hints) - idx - 1} 条更明确的提示，用 --hint {idx + 2} 查看）")
    if show_solution:
        print("【汤底】", p.get("solution", ""))
    elif not hint:
        print("（汤底已隐藏；加 --solution 查看，或用 --hint 1 逐级提示）")


def print_easter_egg():
    """v2.0：--easter 隐藏彩蛋 —— SOLCAT ASCII 署名"""
    art = r"""
  ____             _   _       _   _
 / ___|  ___  _ __| |_(_) __ _| |_| |__
 \___ \ / _ \| '__| __| |/ _` | __| '_ \
  ___) | (_) | |  | |_| | (_| | |_| | |
 |____/ \___/|_|   \__|_|\__,_|\__|_| |_|
"""
    print(art)
    print("  SOLCAT EASTER EGG PROTOCOL v2.0 — 你找到了隐藏入口")
    print("  提示：↑↑↓↓←→←→BA · 连点标题 5 次 · 输入 solcat · Ctrl+Shift+T")
    print("  海龟汤彩蛋：试试 --id 42，答案也许就藏在编号里 ;)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="puzzle_tools.py",
        description="海龟汤题库工具 v2.0 — 分类检索 / 关键词搜索 / 逐级提示 / 随机抽题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  puzzle_tools.py --stats\n"
               "  puzzle_tools.py --list --difficulty 简单 --limit 5\n"
               "  puzzle_tools.py --search 医院 --no-solution\n"
               "  puzzle_tools.py --id 42 --hint 2\n"
               "  puzzle_tools.py --random --difficulty 烧脑\n"
               "  puzzle_tools.py --easter\n"
    )
    parser.add_argument("--stats", action="store_true", help="题库统计")
    parser.add_argument("--list", action="store_true", help="列出题目")
    parser.add_argument("--search", metavar="关键词", help="关键词检索")
    parser.add_argument("--field", default="all", choices=("all", "surface", "title", "solution"),
                        help="检索字段（默认 all）")
    parser.add_argument("--id", type=int, help="按题号查看")
    parser.add_argument("--random", action="store_true", help="随机抽题")
    parser.add_argument("--difficulty", choices=("简单", "中等", "烧脑"), help="按难度筛选")
    parser.add_argument("--limit", type=int, default=20, help="列表/检索显示条数")
    parser.add_argument("--hint", type=int, default=0, help="显示第 N 条递进提示（从 1 起）")
    parser.add_argument("--solution", action="store_true", help="显示汤底（默认隐藏，防剧透）")
    parser.add_argument("--no-solution", action="store_true", help="强制不显示汤底")
    parser.add_argument("--easter", action="store_true", help="隐藏彩蛋（嘘……）")
    return parser


def run_cli(argv=None):
    args = build_parser().parse_args(argv)
    if args.easter:
        print_easter_egg()
        return 0

    meta, puzzles = load_puzzles()
    if not puzzles:
        print("错误：题库为空", file=sys.stderr)
        return 1

    if args.stats:
        cmd_stats(puzzles)
        return 0

    if args.search:
        cmd_search(puzzles, args.search, field=args.field, limit=args.limit)
        return 0

    if args.list:
        cmd_list(puzzles, difficulty=args.difficulty, limit=args.limit)
        return 0

    if args.id:
        target = next((p for p in puzzles if p["id"] == args.id), None)
        if not target:
            print(f"错误：没有编号为 {args.id} 的题目", file=sys.stderr)
            return 1
        cmd_show(target, show_solution=args.solution and not args.no_solution, hint=args.hint)
        return 0

    if args.random:
        pool = [p for p in puzzles if not args.difficulty or p.get("difficulty") == args.difficulty]
        if not pool:
            print("错误：该难度下没有题目", file=sys.stderr)
            return 1
        cmd_show(random.choice(pool), show_solution=args.solution, hint=args.hint)
        return 0

    build_parser().print_help()
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
