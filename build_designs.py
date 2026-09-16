"""Build alternative website designs using the existing public resume content."""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'designs'
OUT = ROOT / 'docs' / 'designs'
E = html.escape
DESIGNS = {
    'a': ('端正なドキュメント', '情報の探しやすさを重視', '白と黒、整った行、明確な見出し。担当内容をすばやく読み取れる構成。'),
    'b': ('余白のあるプロフィール', '落ち着いた読み心地', '柔らかな紙色と明朝体。強みや仕事の進め方が自然に伝わる構成。'),
    'c': ('エンジニアノート', '技術と担当範囲を見せる', '濃紺の背景と技術別の一覧。スキルと実装経験を行き来しながら読める構成。'),
    'd': ('キャリアタイムライン', '経験の流れをたどる', 'ブルーの見出しと縦の時間軸。期間・役割・案件のつながりを見せる構成。'),
}


def build_designs(data=None, output_dir=None, artifact_version=None):
    OUT = Path(output_dir) / "designs" if output_dir else ROOT / "docs" / "designs"
    data = data if data is not None else json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
    version = artifact_version or hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:12]
    design_digest = hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode() + Path(__file__).read_bytes())
    design_digest.update(version.encode())
    for asset in sorted(SOURCE.iterdir()):
        if asset.is_file():
            design_digest.update(asset.read_bytes())
    design_version = design_digest.hexdigest()[:12]
    pdf = f'../../resume.pdf?v={version}'
    OUT.mkdir(parents=True, exist_ok=True)
    for path in SOURCE.iterdir():
        if path.is_file():
            shutil.copy2(path, OUT / path.name)

    def nav(order=None):
        labels = {'summary':'概要','skills':'技術スキル','history':'職歴一覧','experience':'案件経験','about':'資格・仕事の進め方'}
        return ''.join(f'<a href="#{key}">{labels[key]}</a>' for key in (order or labels))

    def identity():
        return f'''<header class="identity" id="top"><div class="identity-name"><p class="eyebrow">PROFESSIONAL PROFILE</p><h1>{E(data['name'])}</h1><p class="name-en">{E(data['name_en'])}</p></div><div class="identity-info"><p class="role">{E(data['title'])}</p><p class="updated">更新：{E(data['updated'])}</p><div class="export-links"><a class="pdf-link" href="{pdf}">経歴PDF</a><a class="pdf-link" href="../../skillsheet.xlsx?v={version}">Excel</a><a class="pdf-link" href="../../resume.md?v={version}">Markdown</a></div></div></header>'''

    def summary():
        strengths = ''.join(f'<li><span class="strength-index">0{i+1}</span><div><h3>{E(s["title"])}</h3><p>{E(s["text"])}</p></div></li>' for i,s in enumerate(data['strengths']))
        return f'<p class="summary-text">{E(data["summary"])}</p><ul class="strengths">{strengths}</ul>'

    def skills():
        groups = []
        for group in data['skill_groups']:
            rows = ''.join(f'<div class="skill-row"><dt>{E(name)}<span>{E(years)} / {E(current)}</span></dt><dd>{E(body)}</dd></div>' for name,years,current,body in group['rows'])
            groups.append(f'<div class="skill-group"><h3>{E(group["name"])}</h3><dl class="skills">{rows}</dl></div>')
        return f'<p class="note">{E(data["experience_as_of"])}</p>' + ''.join(groups)

    def history():
        rows = ''.join(f'<li><span class="history-period">{E(period)}</span><div><h3>{E(name)}</h3><p>{E(role)}</p></div></li>' for period,name,role in data['history'])
        return f'<ol class="history">{rows}</ol><p class="note">{E(data["history_note"])}</p>'

    def projects():
        result = []
        for i,p in enumerate(data['projects']):
            items = ''.join(f'<li><h4>{E(title)}</h4><p>{E(body)}</p></li>' for title,body in p['items'])
            references = ''.join(f'<p class="note">公開資料：<a href="{E(url)}">{E(label)}</a></p>' for label, url in p.get('references', []))
            environment = '<dl class="environment">' + ''.join(f'<div><dt>{E(label)}</dt><dd>{E(body)}</dd></div>' for label,body in p['environment']) + '</dl>'
            result.append(f'''<article class="project" id="{E(p['id'])}"><div class="project-aside"><span class="project-index">{i+1:02}</span><p class="period">{E(p['period'])}</p></div><div class="project-body"><h3>{E(p['title'])}</h3><p class="project-role">{E(p['role'])}</p><p class="project-phases">担当工程：{E(p['phases'])}</p><p class="project-phases">体制・規模：{E(p['team'])}</p><p class="project-overview">{E(p['overview'])}</p><ul class="project-items">{items}</ul>{environment}<p class="tech"><span>使用技術</span>{E(p['tech'])}</p>{references}</div></article>''')
        return ''.join(result)

    content = {
        'summary': ('01','概要・自己PR','PROFILE', summary()),
        'skills': ('02','技術スキル','EXPERTISE', skills()),
        'history': ('03','職歴一覧','CAREER', history()),
        'experience': ('04','案件経験','EXPERIENCE', projects()),
        'about': ('05','資格・仕事の進め方','APPROACH',f'<p>{E(data["qualifications"])}</p><p>{E(data["approach"])}</p>'),
    }
    def section(key,number):
        _,title,en,body = content[key]
        num = f'{number:02}'
        return f'<section id="{key}" class="section section-{key}"><header class="section-heading"><span class="section-number">{num}</span><h2>{title}</h2><span class="section-en">{en}</span></header><div class="section-content">{body}</div></section>'

    for key,(title,tag,description) in DESIGNS.items():
        switches = ''.join(f'<a href="../{k}/?v={design_version}" data-switch="{k}" {"aria-current=page" if k==key else ""} aria-label="{k.upper()}案：{E(t[0])}">{k.upper()}</a>' for k,t in DESIGNS.items())
        order = ['summary','history','experience','skills','about'] if key=='d' else ['summary','skills','history','experience','about']
        rail = f'<aside class="profile-rail"><p class="rail-label">CAREER NOTES</p><p class="rail-name">{E(data["name_en"])}</p><nav aria-label="目次">{nav(order)}</nav><a class="rail-pdf" href="{pdf}">経歴PDFを開く ↗</a></aside>' if key=='c' else ''
        body = identity() + f'<nav class="page-nav" aria-label="ページ目次">{nav(order)}</nav>' + ''.join(section(s,i+1) for i,s in enumerate(order))
        page = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{key.upper()}案 {E(title)} | {E(data['name'])}</title><meta name="description" content="浜田将彰の職務経歴書・デザイン比較用ページ。"><script>if(new URLSearchParams(location.search).has('embed'))document.documentElement.dataset.embed='true';</script><link rel="stylesheet" href="../common.css?v={design_version}"><link rel="stylesheet" href="../{key}.css?v={design_version}"><script defer src="../navigation.js?v={design_version}"></script></head><body class="design-{key}"><a class="skip" href="#main">本文へ移動</a><div class="comparison-bar"><a class="back-link" href="../?v={design_version}">← 4案の比較へ</a><span class="current-design">{key.upper()} <span>{E(title)}</span></span><nav aria-label="デザインの切り替え">{switches}</nav></div><div class="resume-shell">{rail}<main id="main">{body}<footer class="resume-footer"><span>{E(data['name_en'])}</span><a href="{pdf}">経歴PDFを開く</a><a href="#top">先頭へ ↑</a></footer></main></div></body></html>'''
        target = OUT / key
        target.mkdir(exist_ok=True)
        (target / 'index.html').write_text(page, encoding='utf-8')

    cards = []
    for key,(title,tag,description) in DESIGNS.items():
        cards.append(f'''<article class="design-card"><a class="preview-link" href="{key}/?v={design_version}" aria-label="{key.upper()}案・{E(title)}を開く"><div class="preview-stage"><iframe src="{key}/?embed=1&amp;v={design_version}" title="{key.upper()}案の縮小プレビュー" tabindex="-1" aria-hidden="true" loading="eager"></iframe></div><span class="preview-open">大きく見る ↗</span></a><div class="design-card-info"><span class="letter letter-{key}">{key.upper()}</span><div><p class="design-tag">{E(tag)}</p><h2>{E(title)}</h2></div></div><p class="design-description">{E(description)}</p><a class="view-design" href="{key}/?v={design_version}">{key.upper()}案を開く <span aria-hidden="true">→</span></a></article>''')
    gallery = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>4つのデザイン案 | 浜田将彰の職務経歴書</title><meta name="description" content="同じ職務経歴を4種類のデザインで比較できます。"><link rel="stylesheet" href="gallery.css"><script defer src="gallery.js"></script></head><body><header class="gallery-top"><a href="../">← 現在の職務経歴書</a><span>MASAAKI HAMADA</span></header><main class="gallery-main"><header class="gallery-intro"><p class="gallery-eyebrow">RESUME / DESIGN STUDIES</p><h1>しっくりくる見せ方を、<br>4つの案から。</h1><p>同じ経歴で、雰囲気と情報の並べ方を変えました。<br>気になる案を開いて、読み心地を見比べてください。</p></header><div class="gallery-toolbar"><p>4 DESIGNS <span>／ 本文はすべて共通</span></p><div class="device-control" role="group" aria-label="縮小プレビューの表示サイズ"><button type="button" data-device="desktop" aria-pressed="true">PC</button><button type="button" data-device="mobile" aria-pressed="false">スマホ</button></div></div><div class="design-grid">{''.join(cards)}</div><section class="choice-help"><p class="choice-eyebrow">HOW TO CHOOSE</p><h2>気に入った記号を教えてください。</h2><p>「B案が好き」「Aの読みやすさに、Dの経歴の並べ方」など、組み合わせでも大丈夫です。</p><p class="pdf-note">各案のPDFボタンは共通の経歴PDFを開きます。採用する案が決まったら、PDFの見た目も揃えます。</p></section><footer class="gallery-footer"><span>浜田 将彰 / デザイン比較</span><a href="../resume.pdf?v={version}">経歴PDF</a></footer></main></body></html>'''
    gallery = gallery.replace('href="gallery.css"',f'href="gallery.css?v={design_version}"').replace('src="gallery.js"',f'src="gallery.js?v={design_version}"')
    (OUT / 'index.html').write_text(gallery, encoding='utf-8')
    return design_version


if __name__ == '__main__':
    raise SystemExit('Use python build.py to keep Excel, PDF, Markdown and all designs in sync.')
