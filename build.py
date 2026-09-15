"""Generate Excel, PDF, Markdown and five web layouts from content.json."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

ROOT = Path(__file__).resolve().parent
E = html.escape
NAV = [("summary", "概要"), ("skills", "技術スキル"), ("history", "職歴一覧"), ("experience", "案件経験"), ("about", "資格・仕事の進め方")]


def revision(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


def table_html(headings, rows, cls):
    return (f'<div class="table-wrap"><table class="{cls}"><thead><tr>' +
            ''.join(f'<th scope="col">{E(h)}</th>' for h in headings) +
            '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{E(c)}</td>' for c in row) + '</tr>' for row in rows) + '</tbody></table></div>')


def project_html(p):
    references = ''.join(f'<p class="note">公開資料：<a href="{E(url)}">{E(label)}</a></p>' for label, url in p.get('references', []))
    environment = '<dl class="environment">' + ''.join(f'<div><dt>{E(label)}</dt><dd>{E(body)}</dd></div>' for label, body in p['environment']) + '</dl>'
    return f'''<article class="project" id="{E(p['id'])}">
      <p class="period">{E(p['period'])}</p><h3>{E(p['title'])}</h3>
      <p class="project-meta">{E(p['role'])}<br>担当工程：{E(p['phases'])}<br>体制・規模：{E(p['team'])}</p>
      <p>{E(p['overview'])}</p><ul>{''.join(f'<li><strong>{E(title)}</strong>{E(body)}</li>' for title, body in p['items'])}</ul>
      {environment}<p class="tech"><span>使用技術</span>{E(p['tech'])}</p>{references}</article>'''


def build_html(data, out):
    version = revision(data)
    css_version = hashlib.sha256((ROOT/'style.css').read_bytes()).hexdigest()[:12]
    pdf_link = f'resume.pdf?v={version}'
    exports = f'<a href="{pdf_link}">PDF</a><a href="skillsheet.xlsx?v={version}">Excel</a><a href="resume.md?v={version}">Markdown</a>'
    nav = ''.join(f'<a href="#{key}">{label}</a>' for key, label in NAV)
    strengths = ''.join(f'<li><h3>{E(s["title"])}</h3><p>{E(s["text"])}</p></li>' for s in data['strengths'])
    skills = ''.join(f'<div class="skill-group"><h3>{E(g["name"])}</h3>{table_html(["技術","経験の目安","利用状況","経験した内容・使用場面"],g["rows"],"skills-detail")}</div>' for g in data['skill_groups'])
    project_nav = ''.join(f'<li><a href="#{E(p["id"])}">{E(p["title"])}</a></li>' for p in data['projects'])
    page = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(data['name'])} | {E(data['title'])}</title>
<meta name="description" content="浜田将彰の職務経歴書。クラウド基盤・IaC・自社サービスの開発運用。案件の体制・担当工程・環境と技術スキルを掲載。Excel・PDF・Markdownでも閲覧できます。">
<meta name="theme-color" content="#225b89"><link rel="stylesheet" href="style.css?v={css_version}"></head>
<body><a class="skip" href="#main">本文へ移動</a>
<header class="topbar"><div class="topbar-inner"><a class="brand" href="#">MASAAKI HAMADA / RESUME</a>
<a class="download" href="{pdf_link}">PDF版を開く</a></div></header>
<div class="layout"><aside class="sidebar"><p class="nav-label">CONTENTS</p><nav aria-label="目次">{nav}</nav><p class="small">更新：{E(data['updated'])}</p><div class="export-links">{exports}</div></aside>
<main id="main"><header class="identity"><p class="eyebrow">職務経歴書</p><h1>{E(data['name'])}</h1><p class="name-en">{E(data['name_en'])}</p><p class="role">{E(data['title'])}</p><p class="updated">最終更新：{E(data['updated'])}</p><div class="export-links" aria-label="ファイルで読む">{exports}</div></header>
<nav class="mobile-nav" aria-label="モバイル目次">{nav}</nav>
<section id="summary"><h2><span class="number">01</span>概要</h2><p>{E(data['summary'])}</p><ul class="strengths">{strengths}</ul></section>
<section id="skills"><h2><span class="number">02</span>技術スキル</h2><p class="note">{E(data['experience_as_of'])}</p>{skills}</section>
<section id="history"><h2><span class="number">03</span>職歴一覧</h2>{table_html(['期間','事業・領域','役割'],data['history'],'history')}<p class="note">{E(data['history_note'])}</p></section>
<section id="experience"><h2><span class="number">04</span>案件経験</h2><ol class="project-index">{project_nav}</ol>{''.join(project_html(p) for p in data['projects'])}</section>
<section id="about" class="closing"><h2><span class="number">05</span>資格・仕事の進め方</h2><p>{E(data['qualifications'])}</p><p>{E(data['approach'])}</p></section>
<footer class="footer"><span>{E(data['name_en'])}</span><div class="export-links">{exports}</div><a href="#">先頭へ戻る ↑</a></footer></main></div>
</body></html>'''
    (out / 'index.html').write_text(page, encoding='utf-8')
    shutil.copyfile(ROOT / 'style.css', out / 'style.css')
    (out / '.nojekyll').touch()
    from build_designs import build_designs
    build_designs(data, out)


def build_markdown(data, out):
    def md(text):
        return text.replace('\\', '\\\\').replace('|', '\\|').replace('\n', '<br>')
    def table(headers, rows):
        return ['| ' + ' | '.join(map(md, headers)) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |', *['| ' + ' | '.join(map(md, row)) + ' |' for row in rows], '']
    lines = [f'# {data["name"]} — 職務経歴書', '', data['name_en'], '', data['title'], '', '更新：' + data['updated'], '', '## 概要', '', data['summary'], '']
    for s in data['strengths']:
        lines += ['### ' + s['title'], '', s['text'], '']
    lines += ['## 技術スキル', '', data['experience_as_of'], '']
    for group in data['skill_groups']:
        lines += ['### ' + group['name'], '', *table(['技術', '経験の目安', '利用状況', '経験した内容・使用場面'], group['rows'])]
    lines += ['## 職歴一覧', '', *table(['期間', '事業・領域', '役割'], data['history']), data['history_note'], '', '## 案件経験', '']
    for p in data['projects']:
        lines += ['### ' + p['title'], '', '- 期間：' + p['period'], '- 役割：' + p['role'], '- 担当工程：' + p['phases'], '- 体制・規模：' + p['team'], '', p['overview'], '']
        for title, body in p['items']:
            lines += ['#### ' + title, '', body, '']
        if p['environment']:
            lines += ['#### 開発・運用環境', '', *table(['分類', '環境'], p['environment'])]
        lines += ['使用技術：' + p['tech'], '']
        for label, url in p.get('references', []):
            lines += [f'公開資料：[{label}]({url})', '']
    lines += ['## 資格・仕事の進め方', '', data['qualifications'], '', data['approach'], '']
    (out / 'resume.md').write_text('\n'.join(lines), encoding='utf-8')


def build_pdf(data, out, font_path):
    pdfmetrics.registerFont(TTFont('Japanese', str(font_path)))
    ink, muted, accent, line = [colors.HexColor(v) for v in ['#202b39','#596576','#225b89','#dce3e9']]
    base = dict(fontName='Japanese', textColor=ink, wordWrap='CJK', alignment=TA_LEFT, splitLongWords=True, allowWidows=0, allowOrphans=0)
    styles = {
        'body': ParagraphStyle('body', fontSize=9.3, leading=14.3, spaceAfter=6, **base),
        'small': ParagraphStyle('small', fontSize=8, leading=11.5, spaceAfter=5, **{**base,'textColor':muted}),
        'meta': ParagraphStyle('meta', fontSize=8, leading=11.5, spaceAfter=4, keepWithNext=True, **{**base,'textColor':muted}),
        'title': ParagraphStyle('title', fontSize=24, leading=32, spaceAfter=6, **base),
        'h2': ParagraphStyle('h2', fontSize=13, leading=20, spaceBefore=12, spaceAfter=8, keepWithNext=True, **{**base,'textColor':accent}),
        'h3': ParagraphStyle('h3', fontSize=11.2, leading=17, spaceBefore=10, spaceAfter=6, keepWithNext=True, **base),
        'label': ParagraphStyle('label', fontSize=9.3, leading=14.3, spaceAfter=3, keepWithNext=True, **{**base,'textColor':accent}),
        'cell': ParagraphStyle('cell', fontSize=8.3, leading=12.3, **base),
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
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LINEBELOW',(0,0),(-1,-1),0.4,line)
        ]))
        return t
    def project(p):
        parts = [para(p['title'],'h3'), para(f"{p['period']}  |  {p['role']}",'meta'),para('担当工程：'+p['phases'],'meta'),para('体制・規模：'+p['team'],'meta'),para(p['overview'])]
        for title, body in p['items']:
            parts += [para(title,'label'), para(body)]
        tail_start = len(parts)
        if p['environment']:
            parts += [para('開発・運用環境','label'), grid(['分類','環境'],p['environment'],[93,398]),Spacer(1,6)]
        parts += [para('使用技術：'+p['tech'],'small')]
        for label, url in p.get('references', []):
            parts.append(Paragraph(f'公開資料：<link href="{E(url)}" color="#225b89">{E(label)}</link>', styles['small']))
        parts[tail_start:] = [KeepTogether(parts[tail_start:])]
        parts.append(Spacer(1,9))
        return parts
    story = [para('職務経歴書','label'),para(data['name'],'title'),para(data['name_en'],'small'),para(data['title']),para('更新：'+data['updated'],'small'),heading('01  概要'),para(data['summary'])]
    for s in data['strengths']:
        story += [para(s['title'],'label'),para(s['text'])]
    story += [heading('02  技術スキル'),para(data['experience_as_of'],'small')]
    for group in data['skill_groups']:
        story += [para(group['name'],'h3'),grid(['技術','経験','利用状況','経験した内容・使用場面'],group['rows'],[142,55,60,234])]
    story += [heading('03  職歴一覧'),grid(['期間','事業・領域','役割'],data['history'],[108,173,210]),Spacer(1,7),para(data['history_note'],'small'),heading('04  案件経験')]
    for p in data['projects']:
        story += project(p)
    story += [heading('05  資格・仕事の進め方'),para(data['qualifications']),para(data['approach'])]
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(line)
        canvas.line(18*mm,16*mm,A4[0]-18*mm,16*mm)
        canvas.setFont('Japanese',7)
        canvas.setFillColor(muted)
        canvas.drawString(18*mm,11*mm,data['name']+' / 職務経歴書')
        canvas.drawRightString(A4[0]-18*mm,11*mm,str(doc.page))
        canvas.restoreState()
    doc = SimpleDocTemplate(str(out/'resume.pdf'),pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=15*mm,bottomMargin=21*mm,title=data['name']+' 職務経歴書',author=data['name'])
    doc.build(story,onFirstPage=footer,onLaterPages=footer)


def build_excel(source, out, node, qa_dir=None):
    command = [str(node), str(ROOT / 'tools' / 'export_resume_xlsx.mjs'), str(source), str(out / 'skillsheet.xlsx')]
    if qa_dir:
        command += ['--qa-dir', str(qa_dir)]
    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'content.json', help='Shared professional resume data.')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'docs')
    parser.add_argument('--font', type=Path, help='Japanese TrueType font to embed in the PDF.')
    parser.add_argument('--node', type=Path, help='Node runtime with artifact-tool available; CODEX_ARTIFACT_NODE_MODULES can point to its dependencies.')
    parser.add_argument('--xlsx-qa-dir', type=Path, help='Save full workbook previews and verification reports.')
    args = parser.parse_args()
    font_candidates = [args.font] if args.font else [Path('/Library/Fonts/Arial Unicode.ttf'),Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'),Path('/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'),Path('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf')]
    font = next((p for p in font_candidates if p and p.is_file()),None)
    if font is None:
        parser.error('Supply a Japanese TrueType font with --font.')
    bundled_node = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
    node = args.node or (bundled_node if bundled_node.is_file() else shutil.which('node'))
    if not node:
        parser.error('Supply Node.js with --node.')
    source = args.source.resolve()
    source_bytes = source.read_bytes()
    data = json.loads(source_bytes)
    if len({p['id'] for p in data['projects']}) != len(data['projects']):
        parser.error('Project ids must be unique.')
    out = args.output_dir.resolve()
    if out == ROOT or out in ROOT.parents or source == out or out in source.parents:
        parser.error('Output directory must not contain the source or repository.')
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        previous_manifest = out/'manifest.json'
        if not previous_manifest.is_file():
            parser.error('Existing output needs manifest.json; choose a new output directory.')
        tracked_outputs = set(json.loads(previous_manifest.read_text())['files']) | {'manifest.json'}
        unknown_outputs = {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()} - tracked_outputs
        if unknown_outputs:
            parser.error('Output contains files outside the manifest: '+', '.join(sorted(unknown_outputs)))
    # Stage all formats before replacing any published output. A failed export
    # leaves the previous docs intact, so partially built versions are not pushed.
    with tempfile.TemporaryDirectory(prefix='.resume-build-',dir=out.parent) as staging:
        stage = Path(staging)
        snapshot = stage/'input.json'
        snapshot.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        build_excel(snapshot,stage,node,args.xlsx_qa_dir)
        snapshot.unlink()
        build_pdf(data,stage,font)
        build_markdown(data,stage)
        build_html(data,stage)
        manifest = {
            'revision':revision(data),
            'source_sha256':hashlib.sha256(source_bytes).hexdigest(),
            'projects':len(data['projects']),
            'skills':sum(len(g['rows']) for g in data['skill_groups']),
            'files':{str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*')) if p.is_file()}
        }
        (stage/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        backup = stage.with_name(stage.name+'-previous')
        try:
            if out.exists():
                out.rename(backup)
            stage.rename(out)
        except BaseException:
            if backup.exists() and not out.exists():
                backup.rename(out)
            raise
        else:
            if backup.exists():
                shutil.rmtree(backup)
    print(f'Built Excel, PDF, Markdown and Web: {out}; revision={revision(data)}')


if __name__ == '__main__':
    main()
