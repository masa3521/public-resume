"""Generate the public website and A4 resume from one content.json source."""
import argparse
import html
import json
from pathlib import Path
import shutil

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
DATA = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
E = html.escape
NAV = [("summary", "概要"), ("skills", "技術スキル"), ("history", "職歴一覧"), ("experience", "案件経験"), ("about", "資格・仕事の進め方")]


def table_html(headings, rows, cls, caption=None):
    return (f'<div class="table-wrap"><table class="{cls}">' +
            (f'<caption>{E(caption)}</caption>' if caption else '') +
            '<thead><tr>' + ''.join(f'<th scope="col">{E(h)}</th>' for h in headings) +
            '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{E(c)}</td>' for c in row) + '</tr>' for row in rows) + '</tbody></table></div>')


def project_html(p):
    return f'''<article class="project" id="{p['id']}">
      <p class="period">{E(p['period'])}</p><h3>{E(p['title'])}</h3>
      <p class="project-meta">{E(p['role'])}<br>担当工程：{E(p['phases'])}</p>
      <p>{E(p['overview'])}</p><ul>{''.join(f'<li><strong>{E(title)}</strong>{E(body)}</li>' for title, body in p['items'])}</ul>
      <p class="tech"><span>使用技術</span>{E(p['tech'])}</p></article>'''


def build_html():
    nav = ''.join(f'<a href="#{key}">{label}</a>' for key, label in NAV)
    strengths = ''.join(f'<li><h3>{E(s["title"])}</h3><p>{E(s["text"])}</p></li>' for s in DATA['strengths'])
    page = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(DATA['name'])} | {E(DATA['title'])}</title>
<meta name="description" content="浜田将彰の職務経歴書。AWS・Azure・Terraformによるクラウド基盤設計と、自社サービスの開発・運用経験。PDF版も閲覧できます。">
<meta name="theme-color" content="#225b89"><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#main">本文へ移動</a>
<header class="topbar"><div class="topbar-inner"><a class="brand" href="#">MASAAKI HAMADA / RESUME</a>
<a class="download" href="resume.pdf"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></svg>PDF版を開く</a></div></header>
<div class="layout"><aside class="sidebar"><p class="nav-label">CONTENTS</p><nav aria-label="目次">{nav}</nav><p class="small">更新：{E(DATA['updated'])}<br>Web版・PDF版は同じ内容です。</p></aside>
<main id="main"><header class="identity"><p class="eyebrow">職務経歴書</p><h1>{E(DATA['name'])}</h1><p class="name-en">{E(DATA['name_en'])}</p><p class="role">{E(DATA['title'])}</p><p class="updated">最終更新：{E(DATA['updated'])}</p></header>
<nav class="mobile-nav" aria-label="モバイル目次">{nav}</nav>
<section id="summary"><h2><span class="number">01</span>概要</h2><p>{E(DATA['summary'])}</p><ul class="strengths">{strengths}</ul></section>
<section id="skills"><h2><span class="number">02</span>技術スキル</h2>{table_html(['技術・領域','経験の目安','担当できること・使用技術'],DATA['skills'],'skills')}<p class="note">{E(DATA['experience_as_of'])}</p></section>
<section id="history"><h2><span class="number">03</span>職歴一覧</h2>{table_html(['期間','事業・領域','役割'],DATA['history'],'history')}<p class="note">{E(DATA['history_note'])}</p></section>
<section id="experience"><h2><span class="number">04</span>案件経験</h2>{''.join(project_html(p) for p in DATA['projects'])}</section>
<section id="about" class="closing"><h2><span class="number">05</span>資格・仕事の進め方</h2><p>{E(DATA['qualifications'])}</p><p>{E(DATA['approach'])}</p></section>
<footer class="footer"><span>{E(DATA['name_en'])}</span><a href="resume.pdf">PDF版を開く</a><a href="#">先頭へ戻る ↑</a></footer></main></div>
</body></html>'''
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    shutil.copyfile(ROOT / 'style.css', OUT / 'style.css')
    (OUT / '.nojekyll').touch()


def build_pdf(font_path):
    pdfmetrics.registerFont(TTFont('Japanese', str(font_path)))
    ink, muted, accent, line = [colors.HexColor(v) for v in ['#202b39','#596576','#225b89','#dce3e9']]
    base = dict(fontName='Japanese', textColor=ink, wordWrap='CJK', alignment=TA_LEFT, splitLongWords=True)
    styles = {
        'body': ParagraphStyle('body', fontSize=9.1, leading=13.6, spaceAfter=5, **base),
        'small': ParagraphStyle('small', fontSize=7.7, leading=10.5, spaceAfter=4, **{**base,'textColor':muted}),
        'title': ParagraphStyle('title', fontSize=24, leading=32, spaceAfter=6, **base),
        'h2': ParagraphStyle('h2', fontSize=13, leading=20, spaceBefore=12, spaceAfter=8, keepWithNext=True, **{**base,'textColor':accent}),
        'h3': ParagraphStyle('h3', fontSize=11.2, leading=17, spaceBefore=8, spaceAfter=5, keepWithNext=True, **base),
        'label': ParagraphStyle('label', fontSize=9.1, leading=14, spaceAfter=2, keepWithNext=True, **{**base,'textColor':accent}),
        'cell': ParagraphStyle('cell', fontSize=7.5, leading=11.3, **base),
    }
    def para(text, style='body'):
        return Paragraph(E(text), styles[style])
    def heading(text):
        return para(text, 'h2')
    def grid(headers, rows, widths):
        content = [[para(c, 'cell') for c in row] for row in [headers, *rows]]
        t = Table(content, colWidths=widths, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#f0f4f7')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LINEBELOW',(0,0),(-1,-1),0.4,line)
        ]))
        return t
    def project(p):
        parts = [para(p['title'],'h3'), para(f"{p['period']}  |  {p['role']}",'small'),para('担当工程：'+p['phases'],'small'),para(p['overview'])]
        for title, body in p['items']:
            parts += [para(title,'label'), para(body)]
        parts += [para('使用技術：'+p['tech'],'small'),Spacer(1,7)]
        return parts
    story = [para('職務経歴書','label'),para(DATA['name'],'title'),para(DATA['title']),para('更新：'+DATA['updated'],'small'),heading('01  概要'),para(DATA['summary'])]
    for s in DATA['strengths']:
        story += [para(s['title'],'label'),para(s['text'])]
    story += [heading('02  技術スキル'),grid(['技術・領域','経験の目安','担当できること・使用技術'],DATA['skills'],[90,99,302]),Spacer(1,7),para(DATA['experience_as_of'],'small'),PageBreak()]
    story += [heading('03  職歴一覧'),grid(['期間','事業・領域','役割'],DATA['history'],[112,175,204]),Spacer(1,7),para(DATA['history_note'],'small'),heading('04  案件経験')]
    story += project(DATA['projects'][0])
    for p in DATA['projects'][1:]:
        if p['id'] == 'telecom':
            story.append(PageBreak())
        story += [KeepTogether(project(p))]
    story += [heading('05  資格・仕事の進め方'),para(DATA['qualifications']),para(DATA['approach'])]
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(line)
        canvas.line(18*mm,16*mm,A4[0]-18*mm,16*mm)
        canvas.setFont('Japanese',7)
        canvas.setFillColor(muted)
        canvas.drawString(18*mm,11*mm,DATA['name']+' / 職務経歴書')
        canvas.drawRightString(A4[0]-18*mm,11*mm,str(doc.page))
        canvas.restoreState()
    doc = SimpleDocTemplate(str(OUT/'resume.pdf'),pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=15*mm,bottomMargin=21*mm,title=DATA['name']+' 職務経歴書',author=DATA['name'])
    doc.build(story,onFirstPage=footer,onLaterPages=footer)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font',type=Path,help='Japanese TrueType font; embedded in the PDF, never copied into the repository.')
    args = parser.parse_args()
    candidates = [args.font] if args.font else [Path('/Library/Fonts/Arial Unicode.ttf'),Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'),Path('/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'),Path('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf')]
    font = next((p for p in candidates if p and p.is_file()),None)
    if font is None:
        parser.error('Supply a Japanese TrueType font with --font.')
    OUT.mkdir(exist_ok=True)
    build_html()
    build_pdf(font)
    print('Built docs/index.html and docs/resume.pdf from content.json')
