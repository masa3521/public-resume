"""Integration checks for source-driven expansion and the public XLSX template.

Run with: python3 -m unittest discover -s tests -v
Workbook exports require the Codex artifact runtime. Set RESUME_NODE and
CODEX_ARTIFACT_NODE_MODULES to override its default locations.
"""
from copy import deepcopy
from datetime import date
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
HEADINGS = {
    1: {
        'A1': 'スキルシート', 'A2': '技術者名', 'F2': '職種',
        'A3': '経験領域', 'F3': '更新日', 'A4': '資格', 'F4': '担当工程',
        'A5': 'クラウド経験', 'F5': '業務形態', 'A6': '得意分野',
        'A7': '得意技術', 'A8': '得意業務', 'A9': '自己PR',
        'A11': '期間', 'E11': '業務内容', 'F11': '役割\n\n規模',
        'G11': 'サーバ\nOS', 'H11': 'DBサーバ', 'I11': 'ミドル\nウェア',
        'J11': 'NW機器\nストレージ\nパッケージ\nツール\nPG言語',
        'K11': '担当工程', 'K12': '要件定義', 'L12': '基本設計',
        'M12': '詳細設計', 'N12': '構築・設定', 'O12': '運用設計',
        'P12': '保守・運用', 'Q12': '障害対応',
    },
    2: {'A1': '分類', 'B1': '技術', 'C1': '経験', 'D1': '現在', 'E1': '使用場面'},
}


def serial(month):
    return (date.fromisoformat(month + '-01') - date(1899, 12, 30)).days


def months(start, end):
    sy, sm = map(int, start.split('-'))
    ey, em = map(int, end.split('-'))
    return (ey - sy) * 12 + em - sm + 1


class Workbook:
    """Read saved OOXML directly, independently of the authoring library."""

    def __init__(self, path):
        with ZipFile(path) as archive:
            self.files = {name: archive.read(name) for name in archive.namelist()}
        shared = ET.fromstring(self.files['xl/sharedStrings.xml'])
        self.strings = [''.join(node.itertext()) for node in shared]
        self.sheets = {
            n: ET.fromstring(self.files[f'xl/worksheets/sheet{n}.xml']) for n in (1, 2)
        }
        self.cells = {
            n: {cell.get('r'): cell for cell in root.findall('s:sheetData/s:row/s:c', NS)}
            for n, root in self.sheets.items()
        }
        self.styles = ET.fromstring(self.files['xl/styles.xml'])
        self.xfs = self.styles.find('s:cellXfs', NS)
        formats = self.styles.find('s:numFmts', NS)
        self.formats = {} if formats is None else {
            node.get('numFmtId'): node.get('formatCode') for node in formats
        }
        self.book = ET.fromstring(self.files['xl/workbook.xml'])

    def value(self, sheet, address):
        cell = self.cells[sheet].get(address)
        if cell is None:
            return ''
        if cell.get('t') == 'inlineStr':
            return ''.join(cell.find('s:is', NS).itertext())
        value = cell.find('s:v', NS)
        text = '' if value is None else value.text or ''
        return self.strings[int(text)] if cell.get('t') == 's' else text

    def style(self, sheet, address):
        return self.xfs[int(self.cells[sheet][address].get('s', '0'))]

    def number_format(self, sheet, address):
        identifier = self.style(sheet, address).get('numFmtId', '0')
        return self.formats.get(identifier, identifier)

    def print_area(self, sheet_index):
        return self.book.find(
            f's:definedNames/s:definedName[@name="_xlnm.Print_Area"]'
            f'[@localSheetId="{sheet_index - 1}"]', NS,
        ).text

    def merges(self, sheet):
        return {node.get('ref') for node in self.sheets[sheet].findall('s:mergeCells/s:mergeCell', NS)}


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / 'content.json').read_text())
        selected = os.environ.get('RESUME_NODE')
        cls.node = selected or (str(RUNTIME / 'bin/node') if (RUNTIME / 'bin/node').exists() else shutil.which('node'))
        cls.modules = Path(os.environ.get('CODEX_ARTIFACT_NODE_MODULES', str(RUNTIME / 'node_modules')))

    def export(self, source, directory, expect_success=True):
        if not self.node:
            self.skipTest('Node is unavailable; set RESUME_NODE')
        if expect_success and not (self.modules / '@oai/artifact-tool').exists():
            self.skipTest('Codex artifact runtime is unavailable; set CODEX_ARTIFACT_NODE_MODULES')
        folder = Path(directory)
        source_path, output = folder / 'source.json', folder / 'result.xlsx'
        source_path.write_text(json.dumps(source, ensure_ascii=False))
        result = subprocess.run(
            [self.node, str(ROOT / 'tools/export_resume_xlsx.mjs'), str(source_path), str(output), '--python', sys.executable],
            cwd=ROOT, capture_output=True, text=True, timeout=240,
        )
        if expect_success:
            self.assertEqual(result.returncode, 0, result.stderr[-6000:] + result.stdout[-2000:])
            self.assertTrue(output.is_file())
            return Workbook(output), json.loads(output.with_suffix('.layout.json').read_text())
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists(), 'Invalid source must be rejected before an XLSX is written')
        self.assertFalse(output.with_suffix('.layout.json').exists())
        return result.stderr

    def test_dynamic_growth_and_reordered_ongoing_project(self):
        source = deepcopy(self.source)
        ongoing = next(project for project in source['projects'] if project['workbook']['end'] is None)
        other = [project for project in source['projects'] if project is not ongoing]
        fixture = deepcopy(other[0])
        fixture.update(id='integration-fixture', title='生成器検証用案件', period='2024/01 - 2024/03')
        fixture['workbook'] = {'start': '2024-01', 'end': '2024-03', 'phase_flags': [False, True, False, True, False, True, False]}
        source['projects'] = [*other, fixture, ongoing]
        self.assertGreater(len(source['projects']), 10)
        source['skill_groups'].append({
            'name': '生成器検証用グループ',
            'rows': [[f'検証技術{i}', '1年未満', '使用中' if i % 2 else '過去に使用', f'動的追加の検証{i}'] for i in range(9)],
        })
        source['experience_as_of'] = '生成器検証用注記：追加技術行の後ろに折り返して表示します。'
        with TemporaryDirectory(prefix='resume-export-growth-') as directory:
            book, layout = self.export(source, directory)
            projects = layout['sheets'][0]['projects']
            self.assertEqual([p['id'] for p in projects], [p['id'] for p in source['projects']])
            for index, project in enumerate(source['projects']):
                row, metadata = 13 + 4 * index, project['workbook']
                self.assertEqual(book.value(1, f'A{row}'), str(index + 1))
                self.assertIn(project['title'], book.value(1, f'E{row}'))
                for label, body in project['items']:
                    self.assertIn(label, book.value(1, f'E{row + 1}'))
                    self.assertIn(body, book.value(1, f'E{row + 1}'))
                end = metadata['end'] or source['as_of_month']
                self.assertEqual(float(book.value(1, f'B{row}')), serial(metadata['start']))
                self.assertEqual(float(book.value(1, f'D{row}')), serial(end))
                self.assertEqual(book.number_format(1, f'D{row}'), '"現在"' if metadata['end'] is None else 'yyyy/mm')
                formula = book.cells[1][f'B{row + 3}'].find('s:f', NS)
                self.assertEqual(formula.text, f'DATEDIF(B{row},D{row},"M")+1&"ヶ月"')
                self.assertEqual(book.value(1, f'B{row + 3}'), f'{months(metadata["start"], end)}ヶ月')
                for col, flag in zip('KLMNOPQ', metadata['phase_flags']):
                    self.assertEqual(book.value(1, f'{col}{row}'), '●' if flag else '')
                style = book.style(1, f'E{row + 1}')
                self.assertNotEqual(style.get('borderId', '0'), '0', f'Project body E{row + 1} lost its border')
                self.assertEqual(style.find('s:alignment', NS).get('wrapText'), '1', f'Project body E{row + 1} lost wrapping')
                self.assertIn(f'A{row}:A{row + 3}', book.merges(1))
            last_project_row = 12 + 4 * len(source['projects'])
            self.assertTrue(book.print_area(1).endswith(f'$Q${last_project_row}'))
            self.assertEqual(layout['sheets'][0]['last_row'], last_project_row)
            rows = [(group['name'], skill) for group in source['skill_groups'] for skill in group['rows']]
            self.assertGreater(len(rows), 39)
            for row, (_, skill) in enumerate(rows, 2):
                self.assertEqual(book.value(2, f'B{row}'), skill[0])
                self.assertEqual(book.value(2, f'E{row}'), skill[3])
                self.assertEqual(book.value(2, f'D{row}'), '●' if skill[2] == '使用中' else '')
                style = book.style(2, f'E{row}')
                self.assertNotEqual(style.get('borderId', '0'), '0', f'Skill E{row} lost its border')
                self.assertEqual(style.find('s:alignment', NS).get('wrapText'), '1', f'Skill E{row} lost wrapping')
            note_row = len(rows) + 3
            self.assertEqual(book.value(2, f'A{note_row}'), source['experience_as_of'])
            self.assertIn(f'A{note_row}:E{note_row}', book.merges(2))
            self.assertEqual(book.style(2, f'A{note_row}').find('s:alignment', NS).get('wrapText'), '1')
            self.assertEqual(len(layout['sheets'][1]['groups']), len(source['skill_groups']))
            self.assertTrue(book.print_area(2).endswith(f'$E${note_row}'))

    def test_skill_groups_can_shrink_without_stale_rows(self):
        source = deepcopy(self.source)
        source['skill_groups'] = [deepcopy(source['skill_groups'][-1])]
        source['experience_as_of'] = ''
        with TemporaryDirectory(prefix='resume-export-shrink-') as directory:
            book, layout = self.export(source, directory)
            count = len(source['skill_groups'][0]['rows'])
            last_row = count + 1
            self.assertEqual(len(layout['sheets'][1]['groups']), 1)
            self.assertEqual(layout['sheets'][1]['last_row'], last_row)
            self.assertEqual(max(int(row.get('r')) for row in book.sheets[2].findall('s:sheetData/s:row', NS)), last_row)
            self.assertTrue(book.print_area(2).endswith(f'$E${last_row}'))
            self.assertEqual(book.merges(2), {f'A2:A{count + 1}'})
            self.assertEqual(book.value(2, 'A2'), source['skill_groups'][0]['name'])
            self.assertEqual(book.value(2, 'B2'), source['skill_groups'][0]['rows'][0][0])
            self.assertNotIn(self.source['skill_groups'][0]['rows'][0][0], [book.value(2, a) for a in book.cells[2]])

    def test_inconsistent_dates_and_invalid_phase_flags_are_rejected(self):
        for mode in ('period', 'phase_length', 'phase_type'):
            with self.subTest(mode=mode), TemporaryDirectory(prefix='resume-export-invalid-') as directory:
                source = deepcopy(self.source)
                project = source['projects'][0]
                if mode == 'period':
                    project['period'] = '1900/01 - 現在'
                elif mode == 'phase_length':
                    project['workbook']['phase_flags'] = [True] * 6
                else:
                    project['workbook']['phase_flags'][0] = 'true'
                error = self.export(source, directory, expect_success=False)
                self.assertIn('period disagrees' if mode == 'period' else 'phase_flags', error)

    def test_symlink_aliases_cannot_overwrite_source_or_template(self):
        if not self.node:
            self.skipTest('Node is unavailable; set RESUME_NODE')
        for mode in ('layout_input_alias', 'output_template_alias'):
            with self.subTest(mode=mode), TemporaryDirectory(prefix='resume-export-paths-') as directory:
                folder = Path(directory)
                source = folder / 'source.json'
                source_bytes = json.dumps(self.source, ensure_ascii=False).encode('utf-8')
                source.write_bytes(source_bytes)
                template = folder / 'template.xlsx'
                template_bytes = (ROOT / 'templates/skillsheet.xlsx').read_bytes()
                template.write_bytes(template_bytes)
                alias = folder / 'alias'
                alias.symlink_to(folder, target_is_directory=True)
                output = folder / 'result.xlsx' if mode == 'layout_input_alias' else alias / 'template.xlsx'
                layout = alias / 'source.json' if mode == 'layout_input_alias' else folder / 'result.layout.json'
                # A collision must be rejected before any native processing runs.
                native_sentinel = folder / 'native-processing-must-not-run'
                result = subprocess.run(
                    [self.node, str(ROOT / 'tools/export_resume_xlsx.mjs'), str(source), str(output),
                     '--template', str(template), '--layout-json', str(layout), '--python', str(native_sentinel)],
                    cwd=ROOT, capture_output=True, text=True, timeout=15,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, r'(?i)(same file|overwrite|separate|colli)')
                self.assertNotIn(str(native_sentinel), result.stderr, 'Native processing started before the path collision was rejected')
                self.assertEqual(source.read_bytes(), source_bytes)
                self.assertEqual(template.read_bytes(), template_bytes)
                self.assertFalse((folder / 'result.xlsx').exists())
                self.assertFalse((folder / 'result.layout.json').exists())
                self.assertEqual({file.name for file in folder.glob('*.xlsx')}, {'template.xlsx'})

    def test_public_template_contains_only_layout_and_fixed_headings(self):
        book = Workbook(ROOT / 'templates/skillsheet.xlsx')
        for sheet, headings in HEADINGS.items():
            nonempty = {address: book.value(sheet, address) for address in book.cells[sheet] if book.value(sheet, address)}
            self.assertEqual(nonempty, headings)
            self.assertFalse(book.sheets[sheet].findall('.//s:f', NS), 'The template must not contain cached source formulas')
        self.assertEqual(book.strings, [], 'Unused original shared strings must also be removed')
        self.assertEqual(set(book.files), {
            'xl/workbook.xml', 'xl/styles.xml', 'xl/theme/theme1.xml',
            'xl/sharedStrings.xml', 'xl/worksheets/sheet1.xml', 'xl/worksheets/sheet2.xml',
            '_rels/.rels', 'xl/_rels/workbook.xml.rels', '[Content_Types].xml',
        }, 'No original metadata, comments, hidden sheets, or external-link parts should survive')
        for name, payload in book.files.items():
            text = payload.decode('utf-8')
            self.assertNotIn('/Users/', text, name)
            self.assertNotIn('file://', text, name)
            self.assertNotIn('TargetMode="External"', text, name)


if __name__ == '__main__':
    unittest.main()
