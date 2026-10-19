# -*- coding: utf-8 -*-
"""刨根问底 skill - HTML 转 PDF（Edge 无头打印, 本机最短路径）

用法:
  python make_pdf.py report.html report.pdf
  python make_pdf.py report.html                # 输出同名 .pdf

要点:
- Edge 打不开含中文的 file:// 地址, 所以先把 HTML 复制到纯 ASCII 临时目录,
  打印完再把 PDF 拷回目标位置。
- --virtual-time-budget 给 Google Fonts 思源字体留出加载时间。
- --print-to-pdf-no-header / --no-pdf-header-footer 去掉页眉页脚。
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    pathlib.Path.home() / r"AppData\Local\Microsoft\Edge\Application\msedge.exe",
]


def find_edge():
    for p in EDGE_CANDIDATES:
        p = pathlib.Path(p)
        if p.is_file():
            return str(p)
    sys.exit("[make_pdf] 未找到 msedge.exe, 请确认本机已安装 Microsoft Edge")


def html_to_pdf(html_path, pdf_path=None, cwd=None, timeout=120):
    html_path = pathlib.Path(html_path).resolve()
    if pdf_path is None:
        pdf_path = html_path.with_suffix(".pdf")
    pdf_path = pathlib.Path(pdf_path).resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if not html_path.is_file():
        sys.exit("[make_pdf] 找不到 HTML: %s" % html_path)

    edge = find_edge()
    with tempfile.TemporaryDirectory(prefix="pgwd_pdf_") as tmp:
        tmp = pathlib.Path(tmp)
        # 复制到纯 ASCII 临时路径, 规避 Edge 的中文 file:// 问题
        tmp_html = tmp / "report.html"
        tmp_pdf = tmp / "report.pdf"
        shutil.copyfile(html_path, tmp_html)
        url = tmp_html.as_uri()

        base = [
            edge, "--headless", "--disable-gpu", "--no-first-run",
            "--hide-scrollbars", "--user-data-dir=%s" % (tmp / "profile"),
            "--virtual-time-budget=15000",
            "--print-to-pdf-no-header", "--no-pdf-header-footer",
        ]
        variants = [
            base + ["--print-to-pdf=%s" % tmp_pdf, url],
            base[:1] + ["--headless=new"] + base[2:]
            + ["--print-to-pdf=%s" % tmp_pdf, url],
        ]
        for cmd in variants:
            subprocess.run(cmd, timeout=timeout,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if tmp_pdf.is_file() and tmp_pdf.stat().st_size > 1024:
                shutil.copyfile(tmp_pdf, pdf_path)
                print("[make_pdf] OK -> %s (%d KB)" % (pdf_path, pdf_path.stat().st_size // 1024))
                return 0
    sys.exit("[make_pdf] 转换失败, 请检查 Edge 是否可用, 或直接用浏览器打开 HTML 手动打印")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    html_to_pdf(args[0], args[1] if len(args) > 1 else None)
