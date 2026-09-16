#!/usr/bin/env node
// Author the original 17-column / 5-column resume layout from public JSON.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';

const ROOT=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const HELP=`Usage: node tools/export_resume_xlsx.mjs INPUT.json OUTPUT.xlsx
  [--template FILE.xlsx] [--python PYTHON] [--layout-json FILE.json]
  [--qa-dir DIR] [--qa-range 'スキルシート!A1:Q12']
Uses @oai/artifact-tool from CODEX_ARTIFACT_NODE_MODULES or the Codex runtime.
The template contains layout and fixed headings only. The JSON owns all content.
`;

function parseArgs(argv){
  if(argv.includes('--help')||argv.includes('-h'))return {help:true};
  const result={qaRanges:[],template:path.join(ROOT,'templates/skillsheet.xlsx'),python:process.env.RESUME_PYTHON||'python3'};
  const positional=[],keys={'--template':'template','--python':'python','--layout-json':'layout','--qa-dir':'qaDir','--qa-range':'qaRange'};
  for(let i=0;i<argv.length;i++){
    const arg=argv[i];
    if(keys[arg]){
      const value=argv[++i];if(!value||value.startsWith('--'))throw Error(`Missing ${arg}`);
      if(arg==='--qa-range')result.qaRanges.push(value);else result[keys[arg]]=value;
    }else if(arg.startsWith('-'))throw Error(`Unknown option ${arg}`);else positional.push(arg);
  }
  if(positional.length!==2)throw Error(HELP);
  [result.input,result.output]=positional.map(p=>path.resolve(p));
  result.template=path.resolve(result.template);
  result.layout=path.resolve(result.layout||result.output.replace(/\.xlsx$/i,'.layout.json'));
  if(!/\.xlsx$/i.test(result.output)||result.input===result.output||result.template===result.output)throw Error('Choose a separate .xlsx output');
  if([result.input,result.output,result.template].includes(result.layout))throw Error('--layout-json must not overwrite the input, workbook or template');
  if(result.qaRanges.length&&!result.qaDir)throw Error('--qa-range requires --qa-dir');
  return result;
}
async function canonicalPath(value){
  try{return await fs.realpath(value);}catch(error){
    if(error.code!=='ENOENT')throw error;
    const parent=path.dirname(value);if(parent===value)throw error;
    return path.join(await canonicalPath(parent),path.basename(value));
  }
}
async function checkOutputPaths(args){
  const [input,output,template,layout]=await Promise.all([args.input,args.output,args.template,args.layout].map(canonicalPath));
  if(output===input||output===template)throw Error('Choose a separate .xlsx output; aliases of the source/template are not allowed');
  if([input,output,template].includes(layout))throw Error('--layout-json must not overwrite the input, workbook or template, including path aliases');
}
function month(value,key){
  if(typeof value!=='string'||!/^\d{4}-(0[1-9]|1[0-2])$/.test(value)||Number(value.slice(0,4))<1900)throw Error(`${key} must be YYYY-MM (1900 or later)`);
  return value;
}
function validate(data){
  const text=(v,k)=>{if(typeof v!=='string'||v.length>32767)throw Error(`Invalid text: ${k}`);};
  for(const k of ['name','name_en','title','updated','summary','qualifications','approach','experience_as_of','history_note'])text(data[k],k);
  month(data.as_of_month,'as_of_month');
  for(const k of ['specialty','scope','cloud_experience','engagement','focus','tools','work'])text(data.excel_profile?.[k],`excel_profile.${k}`);
  if(!Array.isArray(data.projects)||!data.projects.length)throw Error('projects must not be empty');
  if(new Set(data.projects.map(p=>p.id)).size!==data.projects.length)throw Error('Project ids must be unique');
  for(const p of data.projects){
    for(const k of ['id','title','period','role','phases','team','overview','tech'])text(p[k],`${p.id}.${k}`);
    const w=p.workbook;if(!w)throw Error(`${p.id}.workbook is required`);
    month(w.start,`${p.id}.start`);if(w.end!==null)month(w.end,`${p.id}.end`);
    if(w.start>(w.end??data.as_of_month)||(w.end&&w.end>data.as_of_month))throw Error(`${p.id}: invalid date order/as_of_month`);
    if(!Array.isArray(w.phase_flags)||w.phase_flags.length!==7||w.phase_flags.some(v=>typeof v!=='boolean'))throw Error(`${p.id}: phase_flags must contain seven booleans`);
    const displayed=[...p.period.matchAll(/\d{4}\/\d{2}/g)].map(m=>m[0].replace('/','-'));
    if(displayed[0]!==w.start||(w.end===null?!p.period.includes('現在'):displayed.at(-1)!==w.end))throw Error(`${p.id}: period disagrees with workbook start/end`);
    for(const key of ['items','environment','references']){
      if(key==='references'&&!p[key])continue;
      if(!Array.isArray(p[key]))throw Error(`${p.id}.${key} must be an array`);
      p[key].forEach(pair=>{if(!Array.isArray(pair)||pair.length!==2)throw Error(`Invalid ${key} pair`);pair.forEach(v=>text(v,key));});
    }
  }
  if(!Array.isArray(data.strengths))throw Error('strengths must be an array');
  data.strengths.forEach(s=>{text(s.title,'strength.title');text(s.text,'strength.text');});
  if(!Array.isArray(data.skill_groups)||!data.skill_groups.length)throw Error('skill_groups must not be empty');
  for(const g of data.skill_groups){text(g.name,'skill group');if(!Array.isArray(g.rows)||!g.rows.length)throw Error('Empty skill group');
    for(const row of g.rows){if(!Array.isArray(row)||row.length!==4)throw Error('Skill rows must have four values');row.forEach(v=>text(v,'skill'));if(!['使用中','過去に使用'].includes(row[2]))throw Error('Unknown skill usage status');}}
}
function lineCount(text,widthPt,fontPt){
  const capacity=Math.max(1,(widthPt-6)/fontPt);
  return String(text).split('\n').reduce((sum,line)=>sum+Math.max(1,Math.ceil([...line].reduce((n,c)=>n+(/[\u0000-\u007f]/.test(c)?0.56:1),0)/capacity)),0);
}
function serial(value){const [y,m]=value.split('-').map(Number);return (Date.UTC(y,m-1,1)-Date.UTC(1899,11,30))/86400000;}
function inclusiveMonths(start,end){const [y,m]=start.split('-').map(Number),[ey,em]=end.split('-').map(Number);return (ey-y)*12+em-m+1;}

async function main(){
  const args=parseArgs(process.argv.slice(2));if(args.help){console.log(HELP);return;}
  await checkOutputPaths(args);
  const data=JSON.parse(await fs.readFile(args.input,'utf8'));validate(data);
  const native=(...parameters)=>execFileSync(args.python,[path.join(ROOT,'tools/workbook_native.py'),...parameters],{encoding:'utf8'});
  const info=JSON.parse(native('inspect',args.template));
  const modules=path.resolve(process.env.CODEX_ARTIFACT_NODE_MODULES||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'));
  try{await fs.access(path.join(modules,'@oai/artifact-tool'));}catch{throw Error('artifact-tool is unavailable. See README: set CODEX_ARTIFACT_NODE_MODULES to an installed Codex runtime.');}
  const runtime=await fs.mkdtemp(path.join(os.tmpdir(),'resume-xlsx-runtime-'));
  try{
    await fs.symlink(modules,path.join(runtime,'node_modules'),'dir');
    const req=createRequire(path.join(runtime,'resolve.cjs'));
    const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
    const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(args.template));
    const main=wb.worksheets.getItem('スキルシート'),skills=wb.worksheets.getItem('技術スキル一覧');
    const expected=[],formulas=[];
    const put=(sheet,cell,value)=>{if(String(value).length>32767)throw Error(`${sheet.name}!${cell} exceeds Excel text limit`);sheet.getRange(cell).values=[[value]];expected.push({sheet:sheet.name,cell,value});};
    const rowHeight=(sheet,row,height)=>{if(height>409)throw Error(`${sheet.name} row ${row}: text exceeds the template capacity; split the project in the source.`);sheet.getRange(`A${row}:${sheet===main?'Q':'E'}${row}`).format.rowHeight=height;};
    const width=(sheet,col)=>sheet.getRange(`${col}1`).format.columnWidthPx*.75;
    const layout={version:1,sheets:[{name:main.name,kind:'projects',header_rows:[11,12],profile_end_row:10,row_height_print_factor:4/3,last_row:12+data.projects.length*4,projects:[]},{name:skills.name,kind:'skills',header_rows:[1,1],row_height_print_factor:1,groups:[]}]};
    for(const ref of info.sheets[0].merges)if(Number(ref.match(/\d+/)[0])>=13)main.unmergeCells(ref);
    for(let i=1;i<data.projects.length;i++){const r=13+4*i;main.getRange(`A${r}:Q${r+3}`).copyFrom(main.getRange('A13:Q16'),'all');}
    main.getRange(`A13:Q${Math.max(info.sheets[0].last_row,layout.sheets[0].last_row)}`).clear({applyTo:'contents'});
    const profile=data.excel_profile;
    const header={C2:data.name,H2:data.title,C3:profile.specialty,H3:data.updated,C4:data.qualifications,H4:profile.scope,C5:profile.cloud_experience,H5:profile.engagement,C6:profile.focus,C7:profile.tools,C8:profile.work};
    for(const [cell,value] of Object.entries(header))put(main,cell,value);
    for(const row of [2,3,4,5]){
      const left='CDE'.split('').reduce((n,c)=>n+width(main,c),0),right='HIJKLMNOPQ'.split('').reduce((n,c)=>n+width(main,c),0);
      rowHeight(main,row,Math.max(info.sheets[0].heights[row],lineCount(header[`C${row}`],left,11)*15+6,lineCount(header[`H${row}`],right,11)*15+6));
    }
    const intro=[data.title,`【職務要約】\n${data.summary}`,...data.strengths.map(s=>`【${s.title}】\n${s.text}`),data.approach,data.history_note,`更新：${data.updated}。現在案件の期間は${data.as_of_month.replace('-','年')}月まで。`].join('\n\n');
    put(main,'C9',intro);
    const introWidth='CDEFGHIJKLMNOPQ'.split('').reduce((n,c)=>n+width(main,c),0);
    const introHeight=Math.max(240,lineCount(intro,introWidth,11)*15+20);
    rowHeight(main,9,introHeight/2);rowHeight(main,10,introHeight/2);
    data.projects.forEach((p,index)=>{
      const r=13+index*4,w=p.workbook;
      for(const ref of [`A${r}:A${r+3}`,`B${r}:B${r+2}`,`C${r}:C${r+2}`,`D${r}:D${r+2}`,`B${r+3}:D${r+3}`,`E${r+1}:E${r+3}`,`F${r+1}:F${r+3}`,...'GHIJKLMNOPQ'.split('').map(c=>`${c}${r}:${c}${r+3}`)])main.mergeCells(ref);
      put(main,`A${r}`,index+1);put(main,`B${r}`,serial(w.start));put(main,`C${r}`,'-');put(main,`D${r}`,serial(w.end??data.as_of_month));
      main.getRange(`B${r}`).setNumberFormat('yyyy/mm');main.getRange(`D${r}`).setNumberFormat(w.end===null?'"現在"':'yyyy/mm');
      const formula=`=DATEDIF(B${r},D${r},"M")+1&"ヶ月"`;
      main.getRange(`B${r+3}`).formulas=[[formula]];formulas.push({cell:`B${r+3}`,formula,value:`${inclusiveMonths(w.start,w.end??data.as_of_month)}ヶ月`});
      const overview=`■${p.title}\n${p.overview}`;
      const body=['≪担当業務≫',...p.items.map(([title,text])=>`【${title}】\n${text}`),...(/開発：/.test(p.period)?[`≪開発・保守の内訳≫\n${p.period}`]:[]),...(p.references||[]).map(([label,url])=>`≪公開資料≫\n${label}\n${url}`)].join('\n\n');
      put(main,`E${r}`,overview);put(main,`E${r+1}`,body);put(main,`F${r}`,p.role);put(main,`F${r+1}`,p.team);
      const env=Object.fromEntries(p.environment),known=new Set(['OS・仮想化','データベース','ミドルウェア','クラウド・ツール']);
      let j=env['クラウド・ツール']||'';
      for(const [label,text] of p.environment)if(!known.has(label))j+=`${j?'\n\n':''}${label}：\n${text}`;
      const existing=new Set(p.environment.flatMap(([,s])=>s.split(/\s*\/\s*/)).map(s=>s.trim()));
      const extra=p.tech.split(/\s+\/\s+/).filter(s=>!existing.has(s.trim()));
      if(extra.length)j+=`${j?'\n\n':''}追加の使用技術：\n${[...new Set(extra)].join(' / ')}`;
      const environment={G:env['OS・仮想化']||'—',H:env['データベース']||'—',I:env['ミドルウェア']||'—',J:j||'—'};
      for(const [c,text] of Object.entries(environment))put(main,`${c}${r}`,text.replace(/ \/ /g,'\n'));
      w.phase_flags.forEach((flag,i)=>put(main,`${String.fromCharCode(75+i)}${r}`,flag?'●':''));
      const top=Math.max(65,lineCount(overview,width(main,'E'),10)*14+10,lineCount(p.role,width(main,'F'),9)*12.5+12);
      const bodyLines=lineCount(body,width(main,'E'),9);
      const otherHeight=Math.max(...Object.entries(environment).map(([col,s])=>lineCount(s.replace(/ \/ /g,'\n'),width(main,col),9)*12.5+14))-top;
      const remaining=Math.max(184.5,bodyLines*13+14,lineCount(p.team,width(main,'F'),9)*12.5+12,otherHeight);
      const heights={[r]:top,[r+1]:(remaining-20)/2,[r+2]:(remaining-20)/2,[r+3]:20};
      Object.entries(heights).forEach(([row,h])=>rowHeight(main,Number(row),h));
      // Keep fonts unchanged; only spare vertical padding is reduced for PDF.
      const pdfRemaining=Math.max(184.5,bodyLines*11.5+6,lineCount(p.team,width(main,'F'),9)*11.5+8,otherHeight);
      const pdfHeights={[r+1]:(Math.min(remaining,pdfRemaining)-20)/2,[r+2]:(Math.min(remaining,pdfRemaining)-20)/2};
      layout.sheets[0].projects.push({id:p.id,start_row:r,end_row:r+3,row_heights:heights,pdf_row_heights:pdfHeights});
    });
    for(const ref of info.sheets[1].merges)skills.unmergeCells(ref);
    const count=data.skill_groups.reduce((n,g)=>n+g.rows.length,0);
    for(let row=3;row<=count+1;row++)skills.getRange(`A${row}:E${row}`).copyFrom(skills.getRange('A2:E2'),'all');
    skills.getRange(`A2:E${Math.max(count+3,info.sheets[1].last_row)}`).clear({applyTo:'contents'});
    let row=2;
    for(const g of data.skill_groups){
      const start=row;
      for(const [name,years,current,usage] of g.rows){
        put(skills,`B${row}`,name);put(skills,`C${row}`,years);put(skills,`D${row}`,current==='使用中'?'●':'');put(skills,`E${row}`,usage);
        rowHeight(skills,row,Math.max(info.sheets[1].heights[row]||30,lineCount(name,width(skills,'B'),10)*13+6,lineCount(usage,width(skills,'E'),10)*13+6));row++;
      }
      put(skills,`A${start}`,g.name);if(row-start>1)skills.mergeCells(`A${start}:A${row-1}`);
      layout.sheets[1].groups.push({start_row:start,end_row:row-1});
    }
    if(data.experience_as_of){
      row++;skills.mergeCells(`A${row}:E${row}`);put(skills,`A${row}`,data.experience_as_of);
      const note=skills.getRange(`A${row}:E${row}`);
      note.format.font={name:'Arial',size:8,color:'#808080'};note.format.borders={preset:'none'};note.format.wrapText=true;
      rowHeight(skills,row,Math.max(55,lineCount(data.experience_as_of,'ABCDE'.split('').reduce((n,c)=>n+width(skills,c),0),8)*11+8));
    }
    layout.sheets[1].last_row=data.experience_as_of?row:row-1;
    wb.recalculate();
    const check=(book)=>{
      for(const e of expected){const actual=book.worksheets.getItem(e.sheet).getRange(e.cell).values[0][0]??'';if(actual!==e.value)throw Error(`Value mismatch ${e.sheet}!${e.cell}`);}
      for(const e of formulas){const cell=book.worksheets.getItem(main.name).getRange(e.cell);if(cell.formulas[0][0]!==e.formula||cell.values[0][0]!==e.value)throw Error(`Formula mismatch ${e.cell}`);}
    };
    check(wb);
    await fs.mkdir(path.dirname(args.output),{recursive:true});await fs.mkdir(path.dirname(args.layout),{recursive:true});
    await fs.writeFile(args.layout,JSON.stringify(layout,null,2)+'\n');
    await (await SpreadsheetFile.exportXlsx(wb)).save(args.output);
    native('patch',args.template,args.output,args.layout);
    const saved=await SpreadsheetFile.importXlsx(await FileBlob.load(args.output));check(saved);
    const errors=await saved.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20}});
    const summary={projects:data.projects.length,skillRows:count,verifiedValues:expected.length,verifiedDurations:formulas.length};
    if(args.qaDir){
      await fs.mkdir(args.qaDir,{recursive:true});
      const ranges=args.qaRanges.length?args.qaRanges:[`${main.name}!A1:Q12`,...layout.sheets[0].projects.map(p=>`${main.name}!A${p.start_row}:Q${p.end_row}`),...layout.sheets[1].groups.map(g=>`${skills.name}!A${g.start_row}:E${g.end_row}`)];
      for(const [i,spec] of ranges.entries()){
        const at=spec.lastIndexOf('!'),sheetName=spec.slice(0,at),range=spec.slice(at+1);if(at<1)throw Error('Invalid QA range');
        const image=await saved.render({sheetName,range,scale:1.25,format:'png'});
        await fs.writeFile(path.join(args.qaDir,`preview-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await image.arrayBuffer()));
      }
      await fs.writeFile(path.join(args.qaDir,'verification.json'),JSON.stringify({...summary,ranges,formulaErrors:errors.ndjson},null,2)+'\n');
    }
    try{if(args.qaDir)await fs.rename(`${args.output}.inspect.ndjson`,path.join(args.qaDir,'export-inspect.ndjson'));else await fs.unlink(`${args.output}.inspect.ndjson`);}catch(e){if(e.code!=='ENOENT')throw e;}
    console.log(JSON.stringify({output:args.output,...summary}));
  }finally{await fs.rm(runtime,{recursive:true,force:true});}
}
main().catch(error=>{console.error(error.stack||String(error));process.exitCode=1;});
