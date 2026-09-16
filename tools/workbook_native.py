"""Preserve Excel features not round-tripped by artifact-tool.

Cell content is authored by artifact-tool. This helper restores print metadata,
stacked headings and styles on rows appended beyond the imported used range.
It uses the Python standard library only.
"""
import argparse
from copy import deepcopy
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET

URI = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
NS = {'s': URI}
ET.register_namespace('', URI)


def read_zip(path):
    with ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def xml_bytes(node):
    return ET.tostring(node, encoding='utf-8', xml_declaration=True)


def inspect_template(path):
    files = read_zip(path)
    sheets = []
    for index, name in enumerate(['スキルシート', '技術スキル一覧'], 1):
        root = ET.fromstring(files[f'xl/worksheets/sheet{index}.xml'])
        sheets.append({'name': name,
                       'merges': [e.get('ref') for e in root.findall('s:mergeCells/s:mergeCell', NS)],
                       'heights': {e.get('r'): float(e.get('ht', 15)) for e in root.findall('s:sheetData/s:row', NS)},
                       'last_row': max(int(e.get('r')) for e in root.findall('s:sheetData/s:row', NS))})
    return {'sheets': sheets}


def replace_print_metadata(src, dst):
    tags = ['printOptions', 'pageMargins', 'pageSetup', 'headerFooter']
    for tag in tags:
        old = dst.find('s:' + tag, NS)
        if old is not None:
            dst.remove(old)
    late = ['rowBreaks', 'colBreaks', 'customProperties', 'cellWatches', 'ignoredErrors', 'smartTags',
            'drawing', 'legacyDrawing', 'legacyDrawingHF', 'picture', 'oleObjects', 'controls', 'webPublishItems', 'tableParts', 'extLst']
    pos = next((i for i, e in enumerate(dst) if e.tag.rsplit('}', 1)[-1] in late), len(dst))
    for tag in tags:
        original = src.find('s:' + tag, NS)
        if original is not None:
            dst.insert(pos, deepcopy(original))
            pos += 1
    props = dst.find('s:sheetPr', NS)
    if props is None:
        props = ET.Element(f'{{{URI}}}sheetPr')
        dst.insert(0, props)
    original = src.find('s:sheetPr/s:pageSetUpPr', NS)
    if original is not None:
        old = props.find('s:pageSetUpPr', NS)
        if old is not None:
            props.remove(old)
        props.append(deepcopy(original))


def patch_export(template, target, layout):
    original, result = read_zip(template), read_zip(target)
    styles = ET.fromstring(result['xl/styles.xml'])
    xfs = styles.find('s:cellXfs', NS)
    style_cache = {}
    for index, sheet in enumerate(layout['sheets'], 1):
        filename = f'xl/worksheets/sheet{index}.xml'
        src, dst = ET.fromstring(original[filename]), ET.fromstring(result[filename])
        replace_print_metadata(src, dst)
        cells = {e.get('r'): e for e in dst.findall('s:sheetData/s:row/s:c', NS)}
        template_last = max(int(e.get('r')) for e in src.findall('s:sheetData/s:row', NS))
        repair_start, repair_end = template_last + 1, sheet['last_row']
        if index == 2:
            # The template's trailing blank/note rows are not formatted skill
            # rows, even though they are inside its imported used range.
            group_ends = [int(match.group(1)) for merge in src.findall('s:mergeCells/s:mergeCell', NS)
                          if (match := re.fullmatch(r'A\d+:A(\d+)', merge.get('ref', '')))]
            repair_start = min(repair_start, max(group_ends, default=template_last) + 1)
            repair_end = sheet['groups'][-1]['end_row']
        for row in range(repair_start, repair_end + 1):
            base_row = 13 + (row - 13) % 4 if index == 1 else 2
            for col in ('ABCDEFGHIJKLMNOPQ' if index == 1 else 'ABCDE'):
                cell, baseline = cells.get(f'{col}{row}'), cells.get(f'{col}{base_row}')
                if cell is None or baseline is None:
                    continue
                base_style = int(baseline.get('s', '0'))
                current_style = int(cell.get('s', '0'))
                # Preserve per-project date formats, including the ongoing label.
                num_fmt = xfs[current_style].get('numFmtId', '0') if index == 1 and col in 'BD' and (row - 13) % 4 == 0 else None
                key = (base_style, num_fmt)
                if key not in style_cache:
                    xf = deepcopy(xfs[base_style])
                    if num_fmt is not None:
                        xf.set('numFmtId', num_fmt)
                    xfs.append(xf)
                    style_cache[key] = len(xfs) - 1
                cell.set('s', str(style_cache[key]))
        if index == 1:
            for col in 'KLMNOPQ':
                cell = cells[f'{col}12']
                xf = deepcopy(xfs[int(cell.get('s', '0'))])
                alignment = xf.find('s:alignment', NS)
                if alignment is None:
                    alignment = ET.SubElement(xf, f'{{{URI}}}alignment')
                alignment.set('textRotation', '255')
                xfs.append(xf)
                cell.set('s', str(len(xfs) - 1))
            for rule in dst.findall('s:dataValidations/s:dataValidation', NS):
                if rule.get('type') == 'list':
                    rule.set('sqref', f'K13:Q{sheet["last_row"]}')
        # Empty styled template rows outside the new content must not extend the sheet.
        data = dst.find('s:sheetData', NS)
        for row in list(data):
            if int(row.get('r')) > sheet['last_row']:
                data.remove(row)
        dimension = dst.find('s:dimension', NS)
        if dimension is not None:
            dimension.set('ref', f'A1:{"Q" if index == 1 else "E"}{sheet["last_row"]}')
        result[filename] = xml_bytes(dst)
    xfs.set('count', str(len(xfs)))
    result['xl/styles.xml'] = xml_bytes(styles)
    workbook = ET.fromstring(result['xl/workbook.xml'])
    names = workbook.find('s:definedNames', NS)
    if names is not None:
        workbook.remove(names)
    names = ET.Element(f'{{{URI}}}definedNames')
    for index, sheet in enumerate(layout['sheets']):
        name = sheet['name']
        end_col = 'Q' if index == 0 else 'E'
        ET.SubElement(names, f'{{{URI}}}definedName', name='_xlnm.Print_Area', localSheetId=str(index)).text = f"'{name}'!$A$1:${end_col}${sheet['last_row']}"
        first, last = sheet['header_rows']
        ET.SubElement(names, f'{{{URI}}}definedName', name='_xlnm.Print_Titles', localSheetId=str(index)).text = f"'{name}'!${first}:${last}"
    pos = next((i for i, e in enumerate(workbook) if e.tag.rsplit('}', 1)[-1] == 'calcPr'), len(workbook))
    workbook.insert(pos, names)
    result['xl/workbook.xml'] = xml_bytes(workbook)
    temporary = target.with_suffix('.native.xlsx')
    with ZipFile(temporary, 'w', ZIP_DEFLATED) as archive:
        for name, content in result.items():
            archive.writestr(name, content)
    temporary.replace(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    inspect = sub.add_parser('inspect')
    inspect.add_argument('template', type=Path)
    patch = sub.add_parser('patch')
    patch.add_argument('template', type=Path)
    patch.add_argument('target', type=Path)
    patch.add_argument('layout', type=Path)
    args = parser.parse_args()
    if args.operation == 'inspect':
        print(json.dumps(inspect_template(args.template), ensure_ascii=False))
    else:
        patch_export(args.template, args.target, json.loads(args.layout.read_text()))


if __name__ == '__main__':
    main()
