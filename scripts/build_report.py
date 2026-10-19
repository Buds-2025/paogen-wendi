# -*- coding: utf-8 -*-
"""刨根问底 skill - HTML 报告生成器（内容 JSON -> 排版 HTML 的最短路径）

用法:
  python build_report.py content.json -o report.html [--theme white|midnight] [--pdf]
  python build_report.py part1.json part2.json -o report.html   # 多文件合并, 防长文截断

第一个 JSON 提供元信息(topic/subtitle/date/theme/thesis/final_verdict),
后续 JSON 的 chapters 按顺序追加。chapters 可为全部 11 章或子集。
"""
import argparse
import datetime
import html
import json
import pathlib
import sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "template.html"

EV_CLASS = {"事实": "ev-fact", "推断": "ev-infer", "思想实验": "ev-thought"}


def esc(s):
    return html.escape(str(s), quote=False)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate(meta, chapters):
    problems = []
    # 后续分片只含 chapters, 必填字段只检查合并后的 meta
    merged = {"topic": meta.get("topic", ""), "thesis": meta.get("thesis", ""),
              "final_verdict": meta.get("final_verdict", "")}
    for key, val in merged.items():
        if not str(val).strip():
            problems.append("缺少必填字段: %s" % key)
    for i, ch in enumerate(chapters, 1):
        for key in ("angle", "title", "lead", "points", "verdict"):
            if key == "points":
                if not ch.get("points"):
                    problems.append("第%d章缺少分析点 points" % i)
                else:
                    for p in ch["points"]:
                        if str(p.get("ev", "")).strip() not in EV_CLASS:
                            problems.append('第%d章某个分析点的 ev 必须是 事实/推断/思想实验' % i)
                        if not str(p.get("text", "")).strip():
                            problems.append("第%d章存在空分析点" % i)
            elif not str(ch.get(key, "")).strip():
                problems.append("第%d章缺少字段: %s" % (i, key))
    if problems:
        sys.exit("[build_report] 内容校验未通过:\n  - " + "\n  - ".join(problems))


ANGLE_GROUPS = [
    ("洞察", ["反常识洞察", "未来二十年", "千年文明", "后人类视角"]),
    ("路径", ["顶尖精通", "思维逆向工程", "古代智慧"]),
    ("检验", ["前提拆解", "最强反方", "失败者研究"]),
    ("行动", ["极端约束"]),
]


def render_cover(meta, chapters):
    date = meta.get("date") or datetime.date.today().strftime("%Y年%m月%d日")
    done = {ch["angle"] for ch in chapters}
    cols = []
    for gname, angles in ANGLE_GROUPS:
        items = [a for a in angles if a in done]
        if not items:
            continue
        rows = "".join(
            f'<p class="ang-item">{esc(a)}</p>' for a in items
        )
        cols.append(
            f'<div class="ang-col"><p class="ang-head">{esc(gname)}</p>{rows}</div>'
        )
    angles_html = "\n        ".join(cols)
    return f"""    <section class="cover">
      <header class="cover-top">
        <p class="meta"><span class="en">DEEP ROOT RESEARCH</span> · 刨根问底</p>
        <p class="meta">{esc(date)}</p>
      </header>
      <div class="cover-main">
        <hr class="rule-red">
        <p class="cover-kicker">深度研究 · {len(chapters)} 个角度</p>
        <h1 class="cover-title">{esc(meta["topic"])}</h1>
        <p class="cover-subtitle">{esc(meta.get("subtitle", ""))}</p>
      </div>
      <footer class="cover-bottom">
        <div class="cover-angles">
        {angles_html}
        </div>
        <div class="cover-bottom-row">
          <p class="meta">刨根问底 · 深度研究报告</p>
          <p class="meta"><span class="en">VOL.01</span></p>
        </div>
      </footer>
    </section>"""


def render_toc(chapters):
    rows = []
    for i, ch in enumerate(chapters, 1):
        rows.append(
            '      <li class="toc-row">'
            f'<p class="toc-no">{i:02d}</p>'
            f'<p class="toc-angle">{esc(ch["angle"])}</p>'
            f'<p class="toc-title">{esc(ch["title"])}</p>'
            '</li>'
        )
    return f"""    <section class="toc">
      <div class="block-head">
        <h2 class="block-title">目录</h2>
        <p class="meta"><span class="en">CONTENTS</span></p>
      </div>
      <ol class="toc-list">
{chr(10).join(rows)}
      </ol>
    </section>"""


def render_summary(meta):
    return f"""    <section class="summary">
      <div class="block-head">
        <h2 class="block-title">总论</h2>
        <p class="meta"><span class="en">THESIS</span></p>
      </div>
      <p class="thesis">{esc(meta["thesis"])}</p>
    </section>"""


def render_chapter(i, ch):
    lead = str(ch["lead"]).strip()
    dropcap, lead_rest = lead[0], lead[1:]
    points = []
    for p in ch["points"]:
        ev = str(p.get("ev", "推断")).strip()
        texts = p["text"] if isinstance(p["text"], list) else [p["text"]]
        paras = "".join(f'<p class="point-text">{esc(t)}</p>' for t in texts)
        points.append(
            f"""      <div class="point">
        <div class="point-head">
          <p class="ev {EV_CLASS[ev]}">{esc(ev)}</p>
          <h4 class="point-title">{esc(p.get("title", ""))}</h4>
        </div>
{paras}
      </div>"""
        )
    return f"""    <section class="chapter" id="ch-{i:02d}">
      <div class="ch-head">
        <p class="ch-no">{i:02d}</p>
        <div class="ch-head-text">
          <p class="ch-label"><span class="en">ANGLE {i:02d}</span> · {esc(ch["angle"])}</p>
          <h3 class="ch-title">{esc(ch["title"])}</h3>
        </div>
      </div>
      <p class="ch-question">{esc(ch.get("question", ""))}</p>
      <p class="lead"><span class="dropcap">{esc(dropcap)}</span>{esc(lead_rest)}</p>
{chr(10).join(points)}
      <div class="verdict">
        <p class="v-label">判断</p>
        <p class="v-text">{esc(ch["verdict"])}</p>
      </div>
    </section>"""


def render_final(meta):
    date = meta.get("date") or datetime.date.today().strftime("%Y年%m月%d日")
    return f"""    <section class="final">
      <div class="block-head">
        <h2 class="block-title">综合判断</h2>
        <p class="meta"><span class="en">VERDICT</span></p>
      </div>
      <hr class="rule-red">
      <p class="final-text">{esc(meta["final_verdict"])}</p>
      <div class="doc-footer">
        <p class="meta">刨根问底 · {esc(meta["topic"])}</p>
        <p class="meta">{esc(date)}</p>
      </div>
    </section>"""


def build(meta, chapters, theme):
    body = "\n".join(
        [render_cover(meta, chapters), render_toc(chapters), render_summary(meta)]
        + [render_chapter(i, ch) for i, ch in enumerate(chapters, 1)]
        + [render_final(meta)]
    )
    tpl = TEMPLATE.read_text(encoding="utf-8")
    title = "刨根问底 · %s" % meta["topic"]
    out = (
        tpl.replace("{{THEME}}", theme)
        .replace("{{TITLE}}", esc(title))
        .replace("{{BODY}}", body)
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="内容 JSON, 可多个按序合并")
    ap.add_argument("-o", "--out", required=True, help="输出 HTML 路径")
    ap.add_argument("--theme", choices=["white", "midnight"], default=None,
                    help="覆盖 JSON 里的 theme")
    ap.add_argument("--pdf", action="store_true", help="生成后立即转 PDF")
    args = ap.parse_args()

    meta, chapters = {}, []
    for path in args.inputs:
        data = load_json(path)
        # 首个文件提供元信息, 后续文件的顶层字段合并进来(允许任一分片携带 final_verdict 等)
        if not meta:
            meta = data
        else:
            for k, v in data.items():
                if k != "chapters" and (k not in meta or not str(meta.get(k, "")).strip()):
                    meta[k] = v
        chapters.extend(data.get("chapters", []))

    validate(meta, chapters)
    theme = args.theme or meta.get("theme") or "white"
    out_html = pathlib.Path(args.out)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(build(meta, chapters, theme), encoding="utf-8")
    print("[build_report] OK -> %s (theme=%s, %d chapters)" % (out_html, theme, len(chapters)))

    if args.pdf:
        out_pdf = out_html.with_suffix(".pdf")
        sys.exit(
            __import__("make_pdf").html_to_pdf(out_html, out_pdf, cwd=pathlib.Path(__file__).parent)
        )


if __name__ == "__main__":
    main()
