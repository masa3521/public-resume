#!/usr/bin/env python3
"""Export the original-format workbook as an optional A3 landscape PDF on macOS.

Requires Microsoft Excel and macOS Automation permission for osascript. The input
workbook is never opened or modified: Excel receives a unique temporary copy.
The regular build's A4 resume.pdf is independent of this optional exporter.

Optional layout JSON (otherwise inferred from the workbook's print titles):
  {"sheets": [{"name": "スキルシート", "kind": "projects",
    "header_rows": [11, 12], "profile_end_row": 10,
    "projects": [{"id": "own-service", "start_row": 13, "end_row": 16,
                  "pdf_row_heights": {"14": 241, "15": 241}}]},
   {"name": "技術スキル一覧", "kind": "skills", "header_rows": [1, 1],
    "groups": [{"start_row": 2, "end_row": 6}]}]}

Projects are packed one or two per page. Skill groups stay on the same page.
Row heights are read from the actual workbook; pdf_row_heights is an explicit
print-copy-only override, never an automatic text-shrinking operation. Oversized
blocks fail before Excel starts, so a PDF with a split merged cell is not silently
delivered. Inspect the resulting PDF after changing text or the source template.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import quoteattr
from zipfile import BadZipFile, ZipFile


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"s": MAIN_NS}
A3_HEIGHT_PT = 297 * 72 / 25.4
CHILD_ORDER = """sheetPr dimension sheetViews sheetFormatPr cols sheetData
sheetCalcPr sheetProtection protectedRanges scenarios autoFilter sortState
dataConsolidate customSheetViews mergeCells phoneticPr conditionalFormatting
dataValidations hyperlinks printOptions pageMargins pageSetup headerFooter
rowBreaks colBreaks customProperties cellWatches ignoredErrors smartTags drawing
legacyDrawing legacyDrawingHF picture oleObjects controls webPublishItems tableParts
extLst""".split()


class ExportError(ValueError):
    """An actionable input, layout or export error."""


def positive_number(value, label, maximum=None):
    if isinstance(value, bool):
        raise ExportError(f"{label} must be a number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ExportError(f"{label} must be a number") from exc
    if not math.isfinite(number) or number <= 0 or (maximum and number > maximum):
        raise ExportError(f"{label} is outside the supported range")
    return number


def row_number(value, label):
    number = positive_number(value, label, 1_048_576)
    if number != int(number):
        raise ExportError(f"{label} must be an integer")
    return int(number)


@dataclass
class Sheet:
    name: str
    path: str
    raw: bytes
    root: ET.Element
    cells: dict
    heights: dict
    default_height: float
    final_row: int
    header_rows: tuple[int, int] | None

    def height(self, first, last, overrides):
        return sum(overrides.get(r, self.heights.get(r, self.default_height))
                   for r in range(first, last + 1))


def load_workbook(path):
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in relationships
                   if r.get("TargetMode") != "External"}
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(t.text or "" for t in item.iter(f"{{{MAIN_NS}}}t"))
                      for item in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        names = workbook.findall("s:definedNames/s:definedName", NS)
        result = []
        for index, metadata in enumerate(workbook.findall("s:sheets/s:sheet", NS)):
            if metadata.get("state", "visible") != "visible":
                raise ExportError("Hidden sheets are not supported; supply an export-only workbook")
            target = targets.get(metadata.get(f"{{{REL_NS}}}id"))
            if not target:
                raise ExportError(f"Missing worksheet relationship: {metadata.get('name')}")
            member = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            if not member.startswith("xl/worksheets/"):
                raise ExportError("Only ordinary worksheet tabs are supported")
            raw = archive.read(member)
            root = ET.fromstring(raw)
            cells = {}
            for cell in root.findall("s:sheetData/s:row/s:c", NS):
                value = cell.find("s:v", NS)
                text = value.text if value is not None else ""
                if cell.get("t") == "s" and text:
                    text = shared[int(text)]
                elif cell.get("t") == "inlineStr":
                    text = "".join(t.text or "" for t in cell.findall("s:is//s:t", NS))
                cells[cell.get("r")] = text or ""
            sheet_format = root.find("s:sheetFormatPr", NS)
            default = float(sheet_format.get("defaultRowHeight", "15")) if sheet_format is not None else 15
            heights = {int(row.get("r")): (0 if row.get("hidden") == "1" else float(row.get("ht", default)))
                       for row in root.findall("s:sheetData/s:row", NS)}
            header = None
            final = max(heights, default=1)
            for name in names:
                if name.get("localSheetId") != str(index):
                    continue
                if name.get("name") == "_xlnm.Print_Titles":
                    match = re.search(r"!\$?(\d+):\$?(\d+)$", name.text or "")
                    if match:
                        header = tuple(map(int, match.groups()))
                elif name.get("name") == "_xlnm.Print_Area":
                    match = re.search(r"!\$?A\$?1:\$?[A-Z]+\$?(\d+)$", name.text or "")
                    if not match:
                        raise ExportError(f"{metadata.get('name')}: a single print area beginning at A1 is required")
                    final = int(match.group(1))
            result.append(Sheet(metadata.get("name"), member, raw, root, cells, heights, default, final, header))
        return result


def infer_layout(sheets):
    entries = []
    for sheet in sheets:
        if sheet.header_rows is None:
            raise ExportError(f"{sheet.name}: print-title rows are missing; supply --layout-json")
        first, last = sheet.header_rows
        entry = {"name": sheet.name, "header_rows": [first, last]}
        if sheet.name == "スキルシート":
            starts = [r for r in range(last + 1, sheet.final_row + 1)
                      if sheet.cells.get(f"E{r}", "").startswith("■")]
            if not starts or any(b - a != 4 for a, b in zip(starts, starts[1:])):
                raise ExportError(f"{sheet.name}: could not infer four-row project blocks; supply --layout-json")
            entry.update(kind="projects", profile_end_row=first - 1,
                         projects=[{"start_row": r, "end_row": r + 3} for r in starts])
        elif sheet.name == "技術スキル一覧":
            starts = [r for r in range(last + 1, sheet.final_row + 1)
                      if sheet.cells.get(f"A{r}") and sheet.cells.get(f"B{r}")]
            rows = [r for r in range(last + 1, sheet.final_row + 1) if sheet.cells.get(f"B{r}")]
            if not starts or not rows:
                raise ExportError(f"{sheet.name}: could not infer skill groups; supply --layout-json")
            entry.update(kind="skills", groups=[{"start_row": r, "end_row": starts[i + 1] - 1
                          if i + 1 < len(starts) else max(rows)} for i, r in enumerate(starts)])
        else:
            raise ExportError(f"{sheet.name}: unknown sheet; supply --layout-json with its layout")
        entries.append(entry)
    return {"sheets": entries}


def plan_sheet(sheet, entry):
    kind = entry.get("kind")
    if kind not in ("projects", "skills"):
        raise ExportError(f"{sheet.name}: kind must be projects or skills")
    header = entry.get("header_rows", sheet.header_rows)
    if not isinstance(header, (list, tuple)) or len(header) != 2:
        raise ExportError(f"{sheet.name}: header_rows must contain start and end rows")
    first, last = [row_number(r, "header row") for r in header]
    if first > last or sheet.header_rows != (first, last):
        raise ExportError(f"{sheet.name}: header_rows must match the workbook's print-title rows")
    scale = positive_number(entry.get("scale", 90 if kind == "projects" else 100), "scale", 400)
    if scale < 10:
        raise ExportError(f"{sheet.name}: Excel print scale must be at least 10%")
    # Empirical macOS Excel mapping for the retained 17-column template. The
    # factor is configurable for a different template/printer definition.
    factor = positive_number(entry.get("row_height_print_factor", 4 / 3 if kind == "projects" else 1),
                             "row_height_print_factor", 4)
    margins = {"left": 0.25, "right": 0.25, "top": 0.25, "bottom": 0.25, "header": 0, "footer": 0}
    if kind == "skills":
        original = sheet.root.find("s:pageMargins", NS)
        if original is not None:
            margins.update({key: float(value) for key, value in original.attrib.items()})
    margins.update(entry.get("margins", {}))
    if any(key not in ("left", "right", "top", "bottom", "header", "footer")
           or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0
           for key, value in margins.items()):
        raise ExportError(f"{sheet.name}: margins must be nonnegative inch values")
    available = A3_HEIGHT_PT - 72 * (margins["top"] + margins["bottom"])
    conversion = factor * scale / 100
    if available <= 0:
        raise ExportError(f"{sheet.name}: margins leave no printable page height")
    blocks = entry.get("projects" if kind == "projects" else "groups")
    if not isinstance(blocks, list) or not blocks:
        raise ExportError(f"{sheet.name}: project/group blocks are required")
    overrides = {}
    ranges = []
    previous = last
    for block in blocks:
        if not isinstance(block, dict):
            raise ExportError(f"{sheet.name}: each block must be an object")
        start = row_number(block.get("start_row"), "block start")
        end = row_number(block.get("end_row"), "block end")
        if start != previous + 1 or start > end or end > sheet.final_row:
            raise ExportError(f"{sheet.name}: blocks must cover consecutive rows after the header, within the print area")
        row_overrides = block.get("pdf_row_heights", {})
        if not isinstance(row_overrides, dict):
            raise ExportError(f"{sheet.name}: pdf_row_heights must map row numbers to heights")
        for key, value in row_overrides.items():
            row = row_number(key, "PDF row-height row")
            if not start <= row <= end:
                raise ExportError(f"{sheet.name}: PDF row-height override is outside its block")
            overrides[row] = positive_number(value, "PDF row height", 409)
        ranges.append((start, end, str(block.get("id", f"rows {start}-{end}"))))
        previous = end
    header_height = sheet.height(first, last, overrides) * conversion
    capacity = available - header_height
    breaks = []
    if kind == "projects":
        profile_end = row_number(entry.get("profile_end_row", first - 1), "profile end row")
        if profile_end != first - 1:
            raise ExportError(f"{sheet.name}: profile_end_row must immediately precede the header")
        if sheet.height(1, profile_end, overrides) * conversion > available:
            raise ExportError(f"{sheet.name}: profile exceeds one A3 page; revise profile row spacing")
        breaks.append(profile_end)
    page_start = ranges[0][0]
    page_end = page_start - 1
    count = 0
    max_blocks = 2 if kind == "projects" else len(ranges)
    for start, end, label in ranges:
        block_height = sheet.height(start, end, overrides) * conversion
        if block_height > capacity + 0.01:
            raise ExportError(f"{sheet.name}: {label} needs {block_height:.1f} pt, but {capacity:.1f} pt fits "
                              "below the header. Provide verified pdf_row_heights to remove spare row space; "
                              "do not reduce text size or hide content.")
        combined = sheet.height(page_start, end, overrides) * conversion
        if count and (count == max_blocks or combined > capacity + 0.01):
            breaks.append(page_end)
            page_start = start
            count = 0
        page_end = end
        count += 1
    if sheet.height(page_start, sheet.final_row, overrides) * conversion > capacity + 0.01:
        raise ExportError(f"{sheet.name}: trailing notes exceed the final page; revise the footer layout")
    return {"name": sheet.name, "path": sheet.path, "kind": kind, "scale": scale,
            "margins": margins, "row_breaks": breaks, "pdf_row_heights": overrides,
            "row_height_print_factor": factor,
            "estimated_pages": len(breaks) + 1}


def xml_prefix(xml):
    match = re.search(r"<((?:[\w.-]+:)?)(?:worksheet)\b", xml)
    if not match:
        raise ExportError("Worksheet XML root is missing")
    return match.group(1)


def attributes(tag, values, remove=()):
    for key in set(values) | set(remove):
        tag = re.sub(r"\s+" + re.escape(key) + r"\s*=\s*(?:\"[^\"]*\"|'[^']*')", "", tag)
    end = "/>" if tag.rstrip().endswith("/>") else ">"
    return tag.rstrip()[:-len(end)] + "".join(f" {key}={quoteattr(str(value))}" for key, value in values.items()) + end


def upsert_node(xml, name, replacement):
    prefix = xml_prefix(xml)
    tag = re.escape(prefix + name)
    pattern = rf"<{tag}\b[^>]*(?:/>|>.*?</{tag}>)"
    if re.search(pattern, xml, flags=re.S):
        return re.sub(pattern, lambda _: replacement, xml, count=1, flags=re.S)
    for later in CHILD_ORDER[CHILD_ORDER.index(name) + 1:]:
        match = re.search(r"<" + re.escape(prefix + later) + r"\b", xml)
        if match:
            return xml[:match.start()] + replacement + xml[match.start():]
    return xml.replace(f"</{prefix}worksheet>", replacement + f"</{prefix}worksheet>")


def patch_sheet(sheet, plan):
    xml = sheet.raw.decode("utf-8")
    prefix = xml_prefix(xml)
    setup_pattern = rf"<{re.escape(prefix)}pageSetup\b[^>]*/>"
    setup = re.search(setup_pattern, xml)
    tag = setup.group(0) if setup else f"<{prefix}pageSetup/>"
    tag = attributes(tag, {"paperSize": 8, "orientation": "landscape", "scale": f"{plan['scale']:g}"},
                     ("fitToHeight", "fitToWidth"))
    xml = upsert_node(xml, "pageSetup", tag)
    properties = f'<{prefix}pageSetUpPr fitToPage="0"/>'
    prop_pattern = rf"<{re.escape(prefix)}pageSetUpPr\b[^>]*/>"
    if re.search(prop_pattern, xml):
        xml = re.sub(prop_pattern, properties, xml, count=1)
    elif f"</{prefix}sheetPr>" in xml:
        xml = xml.replace(f"</{prefix}sheetPr>", properties + f"</{prefix}sheetPr>", 1)
    else:
        old = re.search(rf"<{re.escape(prefix)}sheetPr\b[^>]*/>", xml)
        replacement = (old.group(0)[:-2] + ">" if old else f"<{prefix}sheetPr>")
        xml = upsert_node(xml, "sheetPr", replacement + properties + f"</{prefix}sheetPr>")
    xml = upsert_node(xml, "printOptions", f'<{prefix}printOptions horizontalCentered="1" verticalCentered="0"/>')
    xml = upsert_node(xml, "pageMargins", attributes(f"<{prefix}pageMargins/>", plan["margins"]))
    for row, height in plan["pdf_row_heights"].items():
        pattern = rf'<{re.escape(prefix)}row\b(?=[^>]*\br="{row}")[^>]*>'
        xml, count = re.subn(pattern, lambda m: attributes(m.group(0), {"ht": f"{height:g}", "customHeight": 1}), xml)
        if count != 1:
            raise ExportError(f"{sheet.name}: override row {row} is absent")
    breaks = plan["row_breaks"]
    node = f'<{prefix}rowBreaks count="{len(breaks)}" manualBreakCount="{len(breaks)}">'
    node += "".join(f'<{prefix}brk id="{r}" min="0" max="16383" man="1"/>' for r in breaks)
    xml = upsert_node(xml, "rowBreaks", node + f"</{prefix}rowBreaks>")
    # Compare XML trees after removing only explicitly permitted print changes.
    before, after = copy.deepcopy(sheet.root), ET.fromstring(xml)
    for root in (before, after):
        for name in ("printOptions", "pageMargins", "pageSetup", "rowBreaks"):
            for child in root.findall(f"s:{name}", NS):
                root.remove(child)
        props = root.find("s:sheetPr", NS)
        if props is not None:
            for child in props.findall("s:pageSetUpPr", NS):
                props.remove(child)
            if not len(props) and not props.attrib:
                root.remove(props)
        for row in root.findall("s:sheetData/s:row", NS):
            if int(row.get("r")) in plan["pdf_row_heights"]:
                row.attrib.pop("ht", None)
                row.attrib.pop("customHeight", None)
    if ET.tostring(before) != ET.tostring(after):
        raise ExportError(f"{sheet.name}: print-copy patch changed unexpected workbook content")
    return xml.encode("utf-8")


def make_preview(source, target, sheets, plans):
    patched = {sheet.path: patch_sheet(sheet, plan) for sheet, plan in zip(sheets, plans)}
    with ZipFile(source) as original, ZipFile(target, "w") as output:
        for info in original.infolist():
            output.writestr(info, patched.get(info.filename, original.read(info.filename)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--layout-json", type=Path, help="Layout manifest; input.layout.json is auto-detected")
    parser.add_argument("--dry-run", action="store_true", help="Print page plan without opening Excel or writing files")
    parser.add_argument("--timeout", type=int, default=30, help="Excel Apple-event timeout in seconds (default: 30)")
    args = parser.parse_args(argv)
    source, destination = args.input.resolve(), args.output.resolve()
    if source.suffix.lower() != ".xlsx" or destination.suffix.lower() != ".pdf":
        raise ExportError("Input must be .xlsx and output must be .pdf")
    if not source.is_file():
        raise ExportError(f"Input workbook does not exist: {source}")
    if not args.dry_run and sys.platform != "darwin":
        raise ExportError("Native Excel PDF export requires macOS and Microsoft Excel; regular resume.pdf is cross-platform")
    if not 10 <= args.timeout <= 600:
        raise ExportError("--timeout must be between 10 and 600 seconds")
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    sheets = load_workbook(source)
    if args.layout_json and not args.layout_json.is_file():
        raise ExportError(f"Layout JSON does not exist: {args.layout_json}")
    layout_path = args.layout_json or source.with_suffix(".layout.json")
    layout = json.loads(layout_path.read_text(encoding="utf-8")) if layout_path.exists() else infer_layout(sheets)
    if not isinstance(layout, dict) or not isinstance(layout.get("sheets"), list):
        raise ExportError("Layout JSON must contain a sheets array")
    entries = layout.get("sheets", [])
    if not all(isinstance(entry, dict) for entry in entries):
        raise ExportError("Every layout sheet must be an object")
    if len(entries) != len(sheets) or {entry.get("name") for entry in entries} != {s.name for s in sheets}:
        raise ExportError("Layout JSON must describe every worksheet exactly once")
    by_name = {entry["name"]: entry for entry in entries}
    plans = [plan_sheet(sheet, by_name[sheet.name]) for sheet in sheets]
    if args.dry_run:
        print(json.dumps({"sheets": plans, "estimated_pages": sum(p["estimated_pages"] for p in plans)},
                         ensure_ascii=False, indent=2))
        return 0
    executable = shutil.which("osascript")
    script = Path(__file__).with_suffix(".applescript")
    if not executable or not script.is_file():
        raise ExportError("osascript or tools/export_excel_pdf.applescript is missing")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Use a short, visible temporary path outside build directories. Stage the
    # finished PDF beside the destination for atomic replacement even across
    # filesystems.
    with tempfile.TemporaryDirectory(prefix="resume-excel-pdf-", dir="/private/tmp") as temporary:
        directory = Path(temporary)
        preview = directory / f"resume-pdf-{uuid.uuid4().hex}.xlsx"
        pending = directory / "export.pdf"
        make_preview(source, preview, sheets, plans)
        try:
            result = subprocess.run([executable, str(script), str(preview), str(pending), str(args.timeout)],
                                    capture_output=True, text=True, timeout=args.timeout * 4 + 30, check=False)
        except subprocess.TimeoutExpired as exc:
            raise ExportError("Excel export timed out. Check Excel for an Automation or file-access dialog; "
                              "the existing output PDF has not been replaced") from exc
        if result.returncode:
            raise ExportError("Excel PDF export failed: " + (result.stderr.strip() or result.stdout.strip()))
        if not pending.is_file() or pending.stat().st_size < 100 or pending.read_bytes()[:5] != b"%PDF-":
            raise ExportError("Excel did not create a valid PDF; the existing output has not been replaced")
        if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
            raise ExportError("Input workbook changed during export; output was not replaced. Run again with the latest file")
        with tempfile.NamedTemporaryFile(prefix=".resume-excel-pdf-", suffix=".pdf",
                                         dir=destination.parent, delete=False) as staged:
            staged_path = Path(staged.name)
        try:
            shutil.copyfile(pending, staged_path)
            os.replace(staged_path, destination)
        finally:
            staged_path.unlink(missing_ok=True)
    print(f"Created {destination}")
    print(f"Input workbook unchanged: SHA-256 {source_hash}")
    print("A3 landscape preview. Verify text wrapping and page breaks before sharing.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ExportError, OSError, BadZipFile, ET.ParseError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
