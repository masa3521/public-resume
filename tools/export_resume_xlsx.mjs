#!/usr/bin/env node
// Build the two resume worksheets from the shared, publication-approved JSON.
// No project-local npm installation is used. The bundled runtime is resolved
// through a disposable node_modules symlink.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const HELP = `Usage: node export_resume_xlsx.mjs <input.json> <output.xlsx> [--qa-dir <dir>] [--qa-range 'sheet!A1:D20']

--qa-dir     Write verification results and sheet previews to this directory.
--qa-range   Render only this range; repeat for multiple ranges (requires --qa-dir).

CODEX_ARTIFACT_NODE_MODULES may point to the bundled runtime's node_modules.
The input JSON is authoritative; descriptions are never shortened or rewritten.
`;

function parseArgs(argv) {
  if (argv.includes('--help') || argv.includes('-h')) return { help: true };
  const positional = [];
  const result = { qaRanges: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--qa-dir' || arg === '--qa-range') {
      const value = argv[++i];
      if (!value || value.startsWith('--')) throw new Error(`Missing value for ${arg}`);
      if (arg === '--qa-dir') result.qaDir = path.resolve(value);
      else result.qaRanges.push(value);
    } else if (arg.startsWith('-')) throw new Error(`Unknown option: ${arg}`);
    else positional.push(arg);
  }
  if (positional.length !== 2) throw new Error(HELP);
  if (result.qaRanges.length && !result.qaDir) throw new Error('--qa-range requires --qa-dir');
  [result.input, result.output] = positional.map((value) => path.resolve(value));
  if (result.input === result.output) throw new Error('Input and output must be separate files');
  if (!result.output.toLowerCase().endsWith('.xlsx')) throw new Error('Output must end in .xlsx');
  return result;
}

function validateResume(data) {
  const text = (value, key) => {
    if (typeof value !== 'string') throw new Error(`${key} must be a string`);
    if (value.length > 32767) throw new Error(`${key} exceeds Excel's cell text limit`);
  };
  const pairs = (rows, key, length = 2) => {
    if (!Array.isArray(rows)) throw new Error(`${key} must be an array`);
    rows.forEach((row, index) => {
      if (!Array.isArray(row) || row.length !== length) throw new Error(`${key}[${index}] must have ${length} fields`);
      row.forEach((value, col) => text(value, `${key}[${index}][${col}]`));
    });
  };
  for (const key of ['name', 'name_en', 'title', 'updated', 'summary', 'qualifications', 'approach', 'experience_as_of', 'history_note']) text(data[key], key);
  if (!Array.isArray(data.strengths)) throw new Error('strengths must be an array');
  data.strengths.forEach((value, index) => {
    text(value.title, `strengths[${index}].title`);
    text(value.text, `strengths[${index}].text`);
  });
  pairs(data.history, 'history', 3);
  if (!Array.isArray(data.projects) || !data.projects.length) throw new Error('projects must contain records');
  data.projects.forEach((project, index) => {
    for (const key of ['title', 'period', 'role', 'phases', 'team', 'overview', 'tech']) text(project[key], `projects[${index}].${key}`);
    pairs(project.items, `projects[${index}].items`);
    pairs(project.environment, `projects[${index}].environment`);
    if (project.references) pairs(project.references, `projects[${index}].references`);
  });
  if (!Array.isArray(data.skill_groups) || !data.skill_groups.length) throw new Error('skill_groups must contain records');
  data.skill_groups.forEach((group, index) => {
    text(group.name, `skill_groups[${index}].name`);
    pairs(group.rows, `skill_groups[${index}].rows`, 4);
  });
}

const COLOR = { ink: '#243447', muted: '#5A6774', accent: '#204F72', line: '#CBD5DF', pale: '#EEF3F7', white: '#FFFFFF' };
const FONT = 'Arial';
const BODY_PT = 11;
const COLS = ['A', 'B', 'C', 'D'];

// Conservative CJK-aware width estimate. Values remain verbatim; only row
// heights change. Extra line space accommodates Excel's font substitution.
function lineCount(value, widthPx, fontPt = BODY_PT) {
  const maxUnits = Math.max(1, (widthPx - 20) / (fontPt * 4 / 3));
  return String(value).split('\n').reduce((sum, line) => {
    let width = 0;
    for (const char of line) width += /[\u0000-\u007f]/u.test(char) ? (/[MW@]/u.test(char) ? 0.9 : 0.57) : 1;
    return sum + Math.max(1, Math.ceil(width / maxUnits));
  }, 0);
}

function makePlan(name, widths) {
  return { name, widths, rows: [], blocks: [], freeze: 0 };
}

function pushRow(plan, kind, cells, spans = []) {
  const row = { kind, cells: [...cells], spans };
  while (row.cells.length < 4) row.cells.push(null);
  plan.rows.push(row);
  return plan.rows.length;
}

function full(plan, value, kind = 'body') {
  return pushRow(plan, kind, [value, null, null, null], [[0, 3]]);
}

function keyValue(plan, label, value, kind = 'key') {
  return pushRow(plan, kind, [label, value, null, null], [[1, 3]]);
}

function blank(plan) { pushRow(plan, 'blank', [null, null, null, null]); }

function buildPlans(data) {
  const main = makePlan('スキルシート', [190, 230, 230, 360]);
  blank(main);
  full(main, data.name, 'title');
  full(main, data.name_en, 'muted');
  full(main, data.title, 'subheading');
  full(main, `更新日：${data.updated}`, 'muted');
  main.freeze = 5;
  blank(main);
  full(main, '職務概要', 'section');
  full(main, data.summary);
  full(main, data.experience_as_of, 'muted');
  blank(main);
  full(main, '強み', 'section');
  for (const strength of data.strengths) {
    full(main, strength.title, 'item');
    full(main, strength.text);
  }
  blank(main);
  full(main, '職歴一覧', 'section');
  pushRow(main, 'header', ['期間', '事業・領域', null, '役割'], [[1, 2]]);
  for (const row of data.history) pushRow(main, 'history', [row[0], row[1], null, row[2]], [[1, 2]]);
  full(main, data.history_note, 'muted');
  blank(main);
  full(main, '案件経験', 'section');
  for (const [index, project] of data.projects.entries()) {
    const start = main.rows.length + 1;
    full(main, `${String(index + 1).padStart(2, '0')}  ${project.title}`, 'project');
    keyValue(main, '期間', project.period);
    keyValue(main, '役割', project.role);
    keyValue(main, '担当工程', project.phases);
    keyValue(main, '体制・規模', project.team);
    keyValue(main, '概要', project.overview);
    for (const [label, body] of project.items) {
      full(main, label, 'item');
      full(main, body);
    }
    if (project.environment.length) {
      full(main, '開発・運用環境', 'subheading');
      for (const [category, value] of project.environment) keyValue(main, category, value, 'environment');
    }
    keyValue(main, '使用技術', project.tech, 'technology');
    for (const [label, url] of project.references || []) {
      full(main, `公開資料：${label}`, 'reference');
      full(main, url, 'url');
    }
    main.blocks.push({ type: 'project', index: index + 1, start, end: main.rows.length });
    blank(main);
  }
  full(main, '資格・仕事の進め方', 'section');
  full(main, data.qualifications);
  full(main, data.approach);

  const skills = makePlan('技術スキル一覧', [310, 105, 125, 540]);
  blank(skills);
  full(skills, '技術スキル一覧', 'title');
  full(skills, `${data.name}　更新日：${data.updated}`, 'muted');
  full(skills, data.experience_as_of, 'muted');
  pushRow(skills, 'header', ['技術', '経験の目安', '利用状況', '経験した内容・使用場面']);
  skills.freeze = 5;
  for (const group of data.skill_groups) {
    const start = skills.rows.length + 1;
    full(skills, group.name, 'section');
    for (const row of group.rows) pushRow(skills, 'skill', row);
    skills.blocks.push({ type: 'skill_group', start, end: skills.rows.length });
  }
  return [main, skills];
}

function measureRow(plan, row) {
  if (row.kind === 'blank') return 12;
  const size = row.kind === 'title' ? 17 : BODY_PT;
  let lines = 1;
  for (let col = 0; col < 4; col += 1) {
    if (row.cells[col] === null) continue;
    const span = row.spans.find(([start]) => start === col);
    const end = span ? span[1] : col;
    const width = plan.widths.slice(col, end + 1).reduce((total, val) => total + val, 0);
    lines = Math.max(lines, lineCount(row.cells[col], width, size));
  }
  const extra = ['section', 'project', 'item', 'title', 'subheading'].includes(row.kind) ? 17 : 13;
  const height = Math.ceil(lines * size * 4 / 3 * 1.48 + extra);
  if (height > 540) throw new Error(`A ${plan.name} row is too tall for Excel; split the source item into shorter records`);
  return height;
}

function populateSheet(workbook, plan) {
  const sheet = workbook.worksheets.add(plan.name);
  sheet.showGridLines = false;
  sheet.tabColor = plan.name === 'スキルシート' ? COLOR.accent : '#668AA5';
  const whole = sheet.getRange(`A1:D${plan.rows.length}`);
  whole.values = plan.rows.map((row) => row.cells);
  whole.format.font = { name: FONT, size: BODY_PT, color: COLOR.ink };
  whole.format.wrapText = true;
  whole.format.verticalAlignment = 'top';
  whole.format.horizontalAlignment = 'left';
  whole.setNumberFormat('@');
  for (let col = 0; col < 4; col += 1) sheet.getRange(`${COLS[col]}1:${COLS[col]}${plan.rows.length}`).format.columnWidthPx = plan.widths[col];
  for (const [index, row] of plan.rows.entries()) {
    const rowNum = index + 1;
    const range = sheet.getRange(`A${rowNum}:D${rowNum}`);
    row.height = measureRow(plan, row);
    range.format.rowHeightPx = row.height;
    for (const [start, end] of row.spans) sheet.mergeCells(`${COLS[start]}${rowNum}:${COLS[end]}${rowNum}`);
    if (row.kind === 'title') {
      range.format.font = { name: FONT, size: 17, bold: true, color: COLOR.ink };
      range.format.borders = { bottom: { style: 'thin', color: COLOR.line } };
    } else if (row.kind === 'section' || row.kind === 'project') {
      range.format.fill = row.kind === 'project' ? COLOR.accent : COLOR.pale;
      range.format.font = { name: FONT, size: BODY_PT, bold: true, color: row.kind === 'project' ? COLOR.white : COLOR.accent };
      range.format.verticalAlignment = 'center';
    } else if (row.kind === 'header') {
      range.format.fill = COLOR.accent;
      range.format.font = { name: FONT, size: BODY_PT, bold: true, color: COLOR.white };
      range.format.horizontalAlignment = 'center';
      range.format.verticalAlignment = 'center';
      range.format.borders = { insideVertical: { style: 'thin', color: COLOR.white } };
    } else if (row.kind === 'item' || row.kind === 'subheading') {
      range.format.font = { name: FONT, size: BODY_PT, bold: true, color: COLOR.ink };
    } else if (row.kind === 'muted') {
      range.format.font = { name: FONT, size: BODY_PT, color: COLOR.muted };
    } else if (row.kind === 'reference' || row.kind === 'url') {
      range.format.font = { name: FONT, size: BODY_PT, color: COLOR.accent };
    }
    if (['key', 'environment', 'technology', 'history', 'skill'].includes(row.kind)) {
      range.format.borders = { bottom: { style: 'thin', color: COLOR.line } };
      sheet.getRange(`A${rowNum}`).format.font = { name: FONT, size: BODY_PT, bold: true, color: COLOR.ink };
    }
    if (['key', 'environment', 'technology'].includes(row.kind)) sheet.getRange(`A${rowNum}`).format.fill = COLOR.pale;
    if (row.kind === 'skill') {
      sheet.getRange(`B${rowNum}:C${rowNum}`).format.horizontalAlignment = 'center';
      sheet.getRange(`B${rowNum}:C${rowNum}`).format.font = { name: FONT, size: BODY_PT, color: COLOR.muted };
    }
  }
  if (plan.freeze) sheet.freezePanes.freezeRows(plan.freeze);
  return sheet;
}

function verifyValues(sheet, plan) {
  const values = sheet.getRange(`A1:D${plan.rows.length}`).values;
  let textCells = 0;
  plan.rows.forEach((row, index) => row.cells.forEach((expected, col) => {
    const actual = values[index]?.[col] ?? null;
    if (actual !== expected) throw new Error(`Content changed at ${plan.name}!${COLS[col]}${index + 1}`);
    if (expected !== null) textCells += 1;
  }));
  return { sheet: plan.name, rows: plan.rows.length, populatedCells: textCells, blocks: plan.blocks };
}

function defaultPreviews(plan) {
  const previews = [];
  let start = 1;
  let height = 0;
  for (let index = 0; index < plan.rows.length; index += 1) {
    const next = plan.rows[index].height;
    if (height + next > 1350 && index + 1 > start) {
      previews.push(`${plan.name}!A${start}:D${index}`);
      start = index + 1;
      height = 0;
    }
    height += next;
  }
  previews.push(`${plan.name}!A${start}:D${plan.rows.length}`);
  return previews;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) { console.log(HELP); return; }
  const data = JSON.parse(await fs.readFile(args.input, 'utf8'));
  validateResume(data);
  const plans = buildPlans(data);
  const runtimeModules = path.resolve(process.env.CODEX_ARTIFACT_NODE_MODULES || path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'));
  await fs.access(path.join(runtimeModules, '@oai', 'artifact-tool'));
  const runtimeDir = await fs.mkdtemp(path.join(os.tmpdir(), 'resume-xlsx-runtime-'));
  try {
    await fs.symlink(runtimeModules, path.join(runtimeDir, 'node_modules'), 'dir');
    const runtimeRequire = createRequire(path.join(runtimeDir, 'resolve.cjs'));
    const { FileBlob, Workbook, SpreadsheetFile } = await import(pathToFileURL(runtimeRequire.resolve('@oai/artifact-tool')).href);
    const workbook = Workbook.create();
    const sheets = plans.map((plan) => populateSheet(workbook, plan));
    workbook.recalculate();
    const verification = plans.map((plan, index) => verifyValues(sheets[index], plan));
    const checks = await workbook.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options: { useRegex: true, maxResults: 20 }, summary: 'Formula error scan' });
    const inspection = await workbook.inspect({ kind: 'table', range: '技術スキル一覧!A5:D9', include: 'values,formulas', tableMaxRows: 5, tableMaxCols: 4, tableMaxCellChars: 100, maxChars: 3000 });
    if (args.qaDir) {
      await fs.mkdir(args.qaDir, { recursive: true });
      await fs.writeFile(path.join(args.qaDir, 'inspection.ndjson'), `${inspection.ndjson}\n${checks.ndjson}\n`);
      const previewRanges = args.qaRanges.length ? args.qaRanges : plans.flatMap(defaultPreviews);
      const previews = [];
      for (const [index, spec] of previewRanges.entries()) {
        const separator = spec.lastIndexOf('!');
        if (separator < 1) throw new Error(`Invalid --qa-range: ${spec}`);
        const sheetName = spec.slice(0, separator);
        const range = spec.slice(separator + 1);
        if (!plans.some((plan) => plan.name === sheetName)) throw new Error(`Unknown QA sheet: ${sheetName}`);
        const blob = await workbook.render({ sheetName, range, scale: 1.4, format: 'png' });
        const filename = `preview-${String(index + 1).padStart(2, '0')}.png`;
        await fs.writeFile(path.join(args.qaDir, filename), new Uint8Array(await blob.arrayBuffer()));
        previews.push({ file: filename, range: spec });
        console.log(`Rendered ${spec}`);
      }
      await fs.writeFile(path.join(args.qaDir, 'verification.json'), JSON.stringify({ input: args.input, output: args.output, projects: data.projects.length, skillRows: data.skill_groups.reduce((sum, group) => sum + group.rows.length, 0), sheets: verification, previews }, null, 2) + '\n');
    }
    await fs.mkdir(path.dirname(args.output), { recursive: true });
    const output = await SpreadsheetFile.exportXlsx(workbook);
    await output.save(args.output);
    // Verify the saved XLSX, not just the in-memory workbook. This also catches
    // accidental changes caused by merges or serialization of literal strings.
    const roundtrip = await SpreadsheetFile.importXlsx(await FileBlob.load(args.output));
    const savedVerification = plans.map((plan) => verifyValues(roundtrip.worksheets.getItem(plan.name), plan));
    const summary = { output: args.output, projects: data.projects.length, skillRows: data.skill_groups.reduce((sum, group) => sum + group.rows.length, 0), roundtripValuesVerified: true, sheets: savedVerification.map(({ sheet, rows, populatedCells }) => ({ sheet, rows, populatedCells })) };
    if (args.qaDir) await fs.writeFile(path.join(args.qaDir, 'roundtrip-verification.json'), JSON.stringify(summary, null, 2) + '\n');
    // The library may emit its own diagnostic sidecar next to the export.
    // Keep diagnostics with QA files rather than in the publication folder.
    const diagnosticPath = `${args.output}.inspect.ndjson`;
    try {
      if (args.qaDir) await fs.rename(diagnosticPath, path.join(args.qaDir, 'export-inspect.ndjson'));
      else await fs.unlink(diagnosticPath);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
    console.log(JSON.stringify(summary));
  } finally {
    await fs.rm(runtimeDir, { recursive: true, force: true });
  }
}

main().catch((error) => { console.error(error.stack || String(error)); process.exitCode = 1; });
