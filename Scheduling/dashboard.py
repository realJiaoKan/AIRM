"""Render a solved scheduling plan as one offline HTML dashboard.

Notebook: generate_dashboard(result, "output/dashboard.html")
CLI:      python dashboard.py output/schedule.json -o output/dashboard.html
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from itertools import combinations
import json
from pathlib import Path

from plotly.offline import get_plotlyjs


def generate_dashboard(result: dict, output_path: str | Path) -> Path:
    """Render reviewed solver output; never run or change the scheduling model."""
    if result.get("schema_version") != 1:
        raise ValueError("Unsupported schedule format.")
    if result.get("solver", {}).get("status") != "Optimal":
        raise ValueError("The dashboard requires a proven optimal schedule.")
    if not result.get("validation", {}).get("passed"):
        raise ValueError(
            "The schedule must pass its constraint audit before rendering."
        )
    for name in ("assignments", "inputs", "source", "rules", "night_eligible"):
        if name not in result:
            raise ValueError(f"Missing result field: {name}")
    # JSON is embedded as data, so workbook text cannot close the script element.
    payload = (
        json.dumps(result, ensure_ascii=False, allow_nan=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    html = TEMPLATE.replace("__PLOTLY_RUNTIME__", get_plotlyjs()).replace(
        "__SCHEDULE_DATA__", payload
    )
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Physician scheduling</title>
<style>
:root{--bg:#f5f6f8;--paper:#fff;--ink:#17283a;--muted:#687586;--line:#e4e8ee;--accent:#1e6458;--day:#3070ba;--daybg:#edf4fc;--evening:#9b641d;--eveningbg:#fff5e5;--night:#7358a1;--nightbg:#f3effa}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:14px;line-height:1.5}button,select{font:inherit}button{cursor:pointer}button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid #47938b;outline-offset:3px}button:disabled{opacity:.5;cursor:default}main{max-width:1450px;margin:auto;padding:36px 40px 48px}.top{display:flex;justify-content:space-between;align-items:flex-start;gap:18px}.top h1{font-size:30px;line-height:1.25;letter-spacing:-.8px;margin:0 0 8px;font-weight:680}.subtitle{margin:0;color:var(--muted)}.actions{display:flex;gap:8px;flex-wrap:wrap}.button{border:1px solid var(--line);border-radius:8px;padding:9px 13px;background:var(--paper);color:var(--ink);font-weight:550}.button:hover{background:#f0f4f7}.button.primary{background:var(--ink);border-color:var(--ink);color:white}.status-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:22px 0}.badge{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:650;line-height:1.4;padding:5px 9px;border-radius:5px;color:var(--accent);background:#e6f1ec}.dot{width:6px;height:6px;background:currentColor;border-radius:50%}.status-button{border:0;cursor:pointer}.status-note{color:var(--muted);font-size:12px}.controls{display:flex;align-items:end;gap:14px;flex-wrap:wrap;background:var(--paper);border:1px solid var(--line);padding:15px 18px;border-radius:11px}.field{display:flex;flex-direction:column;gap:5px;min-width:150px}.field label{color:var(--muted);font-size:12px;font-weight:600}select{background:white;border:1px solid #d8dfe7;color:var(--ink);border-radius:7px;padding:8px 30px 8px 10px;min-height:38px;max-width:100%}.controls .reset{margin-left:auto}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:18px 0 26px}.metric{background:white;border:1px solid var(--line);border-radius:11px;padding:18px 20px}.metric-label{color:var(--muted);font-size:12px;font-weight:600;display:flex;gap:6px}.metric-value{font-size:30px;letter-spacing:-.8px;font-weight:650;margin:7px 0 2px;line-height:1.2;font-variant-numeric:tabular-nums}.metric-note{font-size:12px;color:var(--muted);min-height:18px}.tabs{display:flex;gap:22px;border-bottom:1px solid #d8dfe7;margin-bottom:20px}.tab{border:0;border-bottom:3px solid transparent;background:transparent;padding:0 1px 12px;color:var(--muted);font-weight:600}.tab[aria-selected=true]{color:var(--ink);border-bottom-color:var(--accent)}[hidden]{display:none!important}.panel{background:white;border:1px solid var(--line);border-radius:11px;overflow:hidden;margin-bottom:18px}.panel-head{padding:20px 20px 16px;display:flex;align-items:center;justify-content:space-between;gap:15px;flex-wrap:wrap}.panel-head h2{font-size:16px;font-weight:650;letter-spacing:-.2px;margin:0}.panel-head p{color:var(--muted);font-size:12px;margin:4px 0 0}.legend{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:12px}.legend i{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:5px}.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;text-align:left;white-space:normal}th{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);font-weight:650;background:#fafbfc;padding:12px 20px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}td{padding:10px 20px;border-bottom:1px solid #eff1f5;vertical-align:middle}tr:last-child td{border-bottom:none}.shift-time{display:block;font-size:11px;font-weight:400;letter-spacing:0;text-transform:none;margin-top:2px}.date-main{font-weight:600;font-size:13px}.date-sub{color:var(--muted);font-size:11px}.weekend td:first-child{background:#f8f7f4}.weekend-tag{font-size:10px;color:#857553;font-weight:500;margin-left:6px}.shift-card{display:block;text-align:left;width:100%;padding:8px 10px;border:1px solid transparent;border-left:3px solid var(--shift-color);border-radius:5px;background:var(--shift-bg);color:var(--ink);margin:3px 0;transition:filter .15s}.shift-card:hover{filter:brightness(.965);border-color:var(--shift-color)}.doctor-name{font-weight:600;font-size:12px;display:block}.shift-role{font-size:10px;color:var(--muted)}.empty-cell{font-size:12px;color:#9aa2ac}.unavailable{font-size:11px;color:#856b51;background:#faf4eb;border:1px solid #f0e1cb;border-radius:4px;padding:3px 6px}.no-results{padding:30px;color:var(--muted);text-align:center}.week-divider td{border-top:2px solid #d7dfe8}.table-note{padding:12px 20px;color:var(--muted);font-size:11px;border-top:1px solid var(--line)}.chart-grid{display:grid;grid-template-columns:1.1fr 1fr;gap:18px}.chart{height:350px;width:100%;min-width:0}.chart-grid .panel{min-width:0}.doctor-button{border:0;background:transparent;padding:0;color:var(--ink);font-weight:600;text-decoration:underline;text-decoration-color:#c7d6df;text-underline-offset:3px;text-align:left}.role{font-size:11px;color:var(--muted)}.number{font-variant-numeric:tabular-nums}.summary-table{min-width:650px}.summary-table td,.summary-table th{text-align:right}.summary-table td:first-child,.summary-table th:first-child{text-align:left;min-width:150px;white-space:nowrap}.capacity-bar{display:inline-block;height:5px;width:48px;background:#e9edf2;border-radius:8px;margin-left:7px;vertical-align:middle;overflow:hidden}.capacity-bar span{height:100%;display:block;background:#6d9389}.small-note{font-size:11px;color:var(--muted)}footer{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-top:24px;color:var(--muted);font-size:11px}.link-button{border:0;background:none;padding:0;color:var(--accent);text-decoration:underline;font:inherit}.scope-line{font-size:12px;color:var(--muted);margin-bottom:12px}dialog{border:1px solid var(--line);border-radius:13px;box-shadow:0 16px 70px #10243b24;padding:0;width:min(760px,calc(100% - 32px));max-height:85vh;color:var(--ink);background:white}dialog::backdrop{background:#17283a66}.dialog-head{position:sticky;top:0;background:white;border-bottom:1px solid var(--line);padding:18px 22px;display:flex;justify-content:space-between;align-items:center;z-index:1}.dialog-head h2{font-size:18px;margin:0}.dialog-body{padding:20px 22px}.dialog-body h3{font-size:14px;margin:22px 0 8px}.dialog-body h3:first-child{margin-top:0}.dialog-body p,.dialog-body li{font-size:13px}.dialog-body ul{padding-left:20px}.dialog-body table{font-size:12px}.dialog-body td,.dialog-body th{padding:9px 10px}.dialog-body .hash{font-family:monospace;font-size:10px;word-break:break-all}.check{display:flex;justify-content:space-between;gap:15px;padding:9px 0;border-bottom:1px solid var(--line);font-size:13px}.check span:last-child{color:var(--accent);font-weight:600}.details-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px 22px}.details-grid dt{font-size:11px;color:var(--muted)}.details-grid dd{font-size:14px;margin:3px 0 0;font-weight:600}.dialog-actions{padding-top:20px}.print-only{display:none}

@media(max-width:1000px){main{padding:28px 24px}.chart-grid{grid-template-columns:1fr}.metrics{gap:10px}.metric{padding:15px}.metric-value{font-size:26px}}
@media(max-width:650px){main{padding:22px 14px}.top{flex-direction:column}.top h1{font-size:27px}.actions{width:100%}.actions .button{font-size:12px;padding:8px 10px}.controls{padding:12px;gap:10px}.field{flex:1 1 40%;min-width:110px}.controls .reset{margin-left:0;align-self:end}.metrics{grid-template-columns:1fr 1fr;margin-bottom:22px}.metric{padding:14px}.metric-value{font-size:26px}.metric-note{font-size:11px}.panel-head{padding:16px}.legend{gap:10px}.details-grid{grid-template-columns:1fr}.status-row{margin:17px 0}.dialog-body{padding:16px}.chart{height:330px}}
@media print{body{background:white}main{padding:0;max-width:none}.actions,.controls,.tabs,.status-button,footer,.plot-container,.chart-grid{display:none!important}.panel{border:1px solid #bbb;break-inside:avoid}.scroll{overflow:visible}#roster{min-width:0}td,th{padding:7px!important}.shift-card{print-color-adjust:exact;-webkit-print-color-adjust:exact}.metrics{margin:14px 0}.metric-value{font-size:23px}.print-only{display:block}.top h1{font-size:24px}}

.menu-wrap{position:relative}.action-menu{position:absolute;top:calc(100% + 7px);right:0;z-index:20;min-width:185px;padding:5px;background:white;border:1px solid var(--line);border-radius:9px;box-shadow:0 8px 30px #17283a16}.menu-item{display:block;width:100%;text-align:left;border:0;background:white;color:var(--ink);border-radius:5px;padding:10px 12px;white-space:nowrap}.menu-item:hover,.menu-item:focus{background:#f0f4f7}.menu-item:disabled{color:var(--muted)}
#roster.calendar-table{min-width:1120px;table-layout:fixed;border-collapse:separate;border-spacing:0}
#roster.calendar-table th{width:calc(100% / 7);text-align:left;padding:13px 14px;text-transform:none;letter-spacing:0;font-size:12px;border-right:1px solid var(--line)}
#roster.calendar-table th:last-child{border-right:0}
#roster.calendar-table td.calendar-day{vertical-align:top;padding:12px 10px 14px;height:290px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
#roster.calendar-table td.calendar-day:last-child{border-right:0}
#roster.calendar-table tr:last-child td{border-bottom:0}
#roster.calendar-table .weekend-column{background:#faf9f6}
#roster.calendar-table .outside-scope{background:#f7f8fa;color:#b0b7c0}
.calendar-date{display:flex;align-items:baseline;gap:6px;padding:0 3px 8px;font-size:21px;font-weight:600;font-variant-numeric:tabular-nums}
.calendar-month-label{font-size:10px;font-weight:500;color:var(--muted)}.outside-date{font-size:20px;padding:0 3px}
.calendar-events{display:flex;flex-direction:column;gap:6px}
.shift-card.calendar-event{padding:7px 8px;margin:0;min-height:68px}
.event-shift{font-size:10px;font-weight:650;color:var(--shift-color);display:block;margin-bottom:1px}
.calendar-event .doctor-name{font-size:12px;white-space:normal;overflow-wrap:anywhere}
.event-time{display:block;font-size:10px;color:var(--muted);margin-top:1px;white-space:nowrap}
.calendar-events>.empty-cell,.calendar-events>.unavailable{margin:5px 3px;font-size:11px;align-self:flex-start}
.paid-icon{width:44px;height:44px;border-radius:11px;background:#edf3f0;color:var(--accent);display:grid;place-items:center;font-size:23px;margin:2px 0 16px}
.paid-label{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--accent);font-weight:700;margin-bottom:7px}
.dialog-body .paid-title{font-size:24px;line-height:1.3;margin:0 0 10px;letter-spacing:-.5px}.paid-description{color:var(--muted);max-width:440px;line-height:1.7}
@media(max-width:650px){.actions{justify-content:flex-end}#roster.calendar-table{min-width:1050px}#roster.calendar-table td.calendar-day{height:280px}.calendar-panel .panel-head{align-items:flex-start}}
@media print{#roster.calendar-table{min-width:0!important;width:100%}#roster.calendar-table th{padding:5px!important;font-size:9px}#roster.calendar-table td.calendar-day{height:auto;padding:5px!important}.calendar-event .doctor-name{font-size:9px}.event-time,.event-shift{font-size:8px}.calendar-date{font-size:16px}.calendar-events{gap:4px}.shift-card.calendar-event{min-height:0;padding:4px}#roster.calendar-table tr{break-inside:avoid}.calendar-panel{break-inside:auto}.menu-wrap{display:none}}


.senior-name{display:inline-flex;align-items:center;gap:4px;max-width:100%;padding:1px 5px;border:1px solid #c49a35;border-radius:5px;background:linear-gradient(115deg,#fffdf3 5%,#f6e7b3 52%,#fffaf0 95%);color:#6a4b13;box-shadow:0 0 0 1px #fff9e6aa,0 2px 6px #b58b2520;font-weight:650;line-height:1.45;vertical-align:middle;transition:box-shadow .2s,border-color .2s}
.senior-star{font-size:10px;line-height:1;color:#a67c20;text-shadow:0 0 5px #e6bc4d80}
.calendar-event:hover .senior-name,.doctor-button:hover .senior-name{border-color:#a77a18;box-shadow:0 0 0 1px #f4d37066,0 0 12px #d8af4345}
.doctor-button:has(.senior-name){text-decoration:none}
@media print{.senior-name{box-shadow:none;print-color-adjust:exact;-webkit-print-color-adjust:exact}}

</style>
<script>__PLOTLY_RUNTIME__</script>
</head>
<body>
<main>
<header class="top"><div><h1>Physician scheduling</h1><p id="horizon" class="subtitle"></p></div><div class="actions"><div class="menu-wrap"><button id="menu-button" class="button" aria-haspopup="menu" aria-expanded="false" aria-controls="dashboard-menu">Menu <span aria-hidden="true">▾</span></button><div id="dashboard-menu" class="action-menu" role="menu" aria-labelledby="menu-button" hidden><button id="source-button" class="menu-item" role="menuitem">Source &amp; rules</button><button id="print-button" class="menu-item" role="menuitem">Print calendar</button><button id="export-button" class="menu-item" role="menuitem">Export CSV</button></div></div><button id="calendar-button" class="button primary" aria-haspopup="dialog"><span aria-hidden="true">＋</span> Add to calendar</button></div></header>
<div class="status-row"><span class="badge"><span class="dot"></span>Optimal plan</span><button class="badge status-button" id="checks-button" aria-haspopup="dialog"><span class="dot"></span><span id="checks-label"></span></button><span class="status-note">Validation covers the full planning horizon</span></div>
<section class="controls" aria-label="Schedule filters"><div class="field"><label for="week-filter">Period</label><select id="week-filter"><option value="all">Full horizon</option></select></div><div class="field"><label for="doctor-filter">Doctor</label><select id="doctor-filter"><option value="all">All doctors</option></select></div><div class="field"><label for="shift-filter">Shift</label><select id="shift-filter"><option value="all">All shifts</option></select></div><button id="reset-button" class="button reset">Reset filters</button></section>
<section class="metrics" aria-label="Filtered schedule metrics" aria-live="polite">
<div class="metric"><div class="metric-label">Assignments</div><div class="metric-value" id="assigned-value"></div><div class="metric-note" id="assigned-note"></div></div>
<div class="metric"><div class="metric-label">Total workload range <span title="Minimum–maximum assignments per doctor in the selected scope. Off-duty doctors are included.">ⓘ</span></div><div class="metric-value" id="total-value"></div><div class="metric-note" id="total-note"></div></div>
<div class="metric"><div class="metric-label">Night workload range <span title="Minimum–maximum night assignments among eligible junior doctors in the selected scope.">ⓘ</span></div><div class="metric-value" id="night-value"></div><div class="metric-note" id="night-note"></div></div>
<div class="metric"><div class="metric-label">Weekend workload range <span title="Assignments whose start date is Saturday or Sunday, per selected doctor.">ⓘ</span></div><div class="metric-value" id="weekend-value"></div><div class="metric-note" id="weekend-note"></div></div>
</section>
<nav class="tabs" aria-label="Dashboard views" role="tablist"><button class="tab" id="roster-tab" role="tab" aria-selected="true" aria-controls="roster-view">Calendar</button><button class="tab" id="workload-tab" role="tab" aria-selected="false" aria-controls="workload-view" tabindex="-1">Workload</button></nav>
<div class="scope-line" id="scope" aria-live="polite"></div>
<section id="roster-view" role="tabpanel" aria-labelledby="roster-tab"><div class="panel calendar-panel"><div class="panel-head"><div><h2 id="calendar-month"></h2><p id="roster-description"></p></div><div class="legend" id="roster-legend"></div></div><div class="scroll calendar-scroll" tabindex="0" aria-label="Weekly calendar; scroll horizontally on small screens"><table id="roster" class="calendar-table" aria-label="Weekly on-call calendar"><thead id="roster-head"></thead><tbody id="roster-body"></tbody></table></div><div class="table-note">Night shifts end the next morning. Weekends are classified by the shift's start date.</div></div></section>
<section id="workload-view" role="tabpanel" aria-labelledby="workload-tab" hidden><div class="chart-grid"><div class="panel"><div class="panel-head"><div><h2>Assignments by doctor</h2><p>Selected scope, split by shift</p></div></div><div id="total-chart" class="chart" role="img" aria-label="Stacked chart of shifts assigned to each doctor"></div></div><div class="panel"><div class="panel-head"><div><h2>Night and weekend distribution</h2><p>Night shifts apply to eligible juniors only</p></div></div><div id="fairness-chart" class="chart" role="img" aria-label="Night and weekend shifts per doctor"></div></div></div><div class="panel"><div class="panel-head"><div><h2>Doctor workload</h2><p>Assignment counts and hours follow the selected scope</p></div></div><div class="scroll"><table class="summary-table" aria-label="Workload by doctor"><thead><tr><th>Doctor</th><th>Total shifts</th><th>Nights</th><th>Weekends</th><th>Hours</th><th>Horizon load / capacity</th></tr></thead><tbody id="summary-body"></tbody></table></div><div class="table-note">Horizon load and capacity always cover the full planning horizon. Night hours include time after midnight.</div></div></section>
<footer><span id="source-label"></span><span id="generated-label"></span></footer>
</main>
<dialog id="details-dialog"><div class="dialog-head"><h2 id="dialog-title"></h2><button class="button" id="close-dialog" aria-label="Close details">Close</button></div><div id="dialog-body" class="dialog-body"></div></dialog>
<script id="schedule-data" type="application/json">__SCHEDULE_DATA__</script>
<script>
'use strict';
const plan=JSON.parse(document.getElementById('schedule-data').textContent);
const input=plan.inputs, allRows=plan.assignments;
const $=id=>document.getElementById(id);
const escapeHTML=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function doctorName(name,seniority){
 return seniority==='Senior'?`<span class="senior-name" title="Senior physician"><span class="senior-star" aria-hidden="true">✦</span>${escapeHTML(name)}</span>`:escapeHTML(name);
}
const colors={Day:'#3070ba',Evening:'#b77c30',Night:'#7358a1'};
const backgrounds={Day:'#edf4fc',Evening:'#fff5e5',Night:'#f3effa'};
const fallback=['#3070ba','#b77c30','#7358a1','#577b69'];
input.shifts.forEach((s,i)=>{colors[s.id]??=fallback[i%fallback.length];backgrounds[s.id]??='#f0f3f7';});
const dateText=(iso,options={day:'numeric',month:'short'})=>new Date(iso+'T12:00:00').toLocaleDateString('en-GB',options);
const dateRange=days=>days.length?`${dateText(days[0].date)} – ${dateText(days.at(-1).date,{day:'numeric',month:'short',year:'numeric'})}`:'No dates';
const number=v=>Number.isInteger(v)?String(v):v.toFixed(1);
const counts=(rows,pid,predicate=()=>true)=>rows.filter(a=>a.doctor_id===pid&&predicate(a)).length;
const range=values=>values.length?`${Math.min(...values)}–${Math.max(...values)}`:'N/A';
const state={week:'all',doctor:'all',shift:'all',tab:'roster'};
let scopedRows=[],scopedDoctors=[],scopedDays=[];
let plotReady=false;
const options={responsive:true,displaylogo:false,displayModeBar:false};
function option(select,value,label){const o=document.createElement('option');o.value=String(value);o.textContent=label;select.appendChild(o);}
for(const week of [...new Set(input.days.map(d=>d.week))]){const days=input.days.filter(d=>d.week===week);option($('week-filter'),week,`Week ${week} · ${dateText(days[0].date)}–${dateText(days.at(-1).date)}`);}
input.doctors.forEach(p=>option($('doctor-filter'),p.id,p.name));
input.shifts.forEach(s=>option($('shift-filter'),s.id,s.name));
$('horizon').textContent=`${dateRange(input.days)} · ${input.doctors.length} doctors · ${input.days.length} days`;
$('checks-label').textContent=`${plan.validation.checks.length} checks passed`;
$('source-label').textContent=`Source: ${plan.source.file}`;
$('generated-label').textContent=`Generated ${new Date(plan.generated_at).toLocaleString('en-GB',{dateStyle:'medium',timeStyle:'short'})}`;
function selectedShifts(){return input.shifts.filter(s=>state.shift==='all'||s.id===state.shift);}
function refresh(){
 scopedDays=input.days.filter(d=>state.week==='all'||String(d.week)===state.week);
 const dayIds=new Set(scopedDays.map(d=>d.day));
 scopedDoctors=input.doctors.filter(p=>state.doctor==='all'||p.id===state.doctor);
 scopedRows=allRows.filter(a=>dayIds.has(a.day)&&(state.doctor==='all'||a.doctor_id===state.doctor)&&(state.shift==='all'||a.shift_id===state.shift));
 const required=input.demand.filter(r=>dayIds.has(r.day)&&(state.shift==='all'||r.shift_id===state.shift)).reduce((s,r)=>s+r.required,0);
 $('assigned-value').textContent=String(scopedRows.length);
 $('assigned-note').textContent=state.doctor==='all'?`${required} required in this scope`:`of ${required} positions in date / shift scope`;
 const total=scopedDoctors.map(p=>counts(scopedRows,p.id));
 const eligible=scopedDoctors.filter(p=>plan.night_eligible.includes(p.id));
 $('total-value').textContent=range(total);
 $('total-note').textContent=`shifts per ${scopedDoctors.length===1?'selected doctor':'doctor'}`;
 $('night-value').textContent=range(eligible.map(p=>counts(scopedRows,p.id,a=>a.shift_id==='Night')));
 $('night-note').textContent=eligible.length?`shifts · ${eligible.length} eligible junior${eligible.length===1?'':'s'}`:'Selected doctor is not night-eligible';
 $('weekend-value').textContent=range(scopedDoctors.map(p=>counts(scopedRows,p.id,a=>a.is_weekend)));
 $('weekend-note').textContent='weekend shifts per doctor';
 const shiftLabel=state.shift==='all'?'All shifts':input.shifts.find(s=>s.id===state.shift).name;
 const doctorLabel=state.doctor==='all'?'All doctors':scopedDoctors[0].name;
 $('scope').textContent=`${dateRange(scopedDays)} · ${doctorLabel} · ${shiftLabel}`;
 renderRoster();renderSummary();
 if(state.tab==='workload')renderCharts();
 $('export-button').disabled=scopedRows.length===0;
}
function renderRoster(){
 const shifts=selectedShifts();
 const weekdays=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
 $('roster-legend').innerHTML=shifts.map(s=>`<span><i style="background:${colors[s.id]}"></i>${escapeHTML(s.name)}</span>`).join('');
 $('roster-description').textContent=`${scopedRows.length} assignment${scopedRows.length===1?'':'s'} shown · select a shift for details`;
 const months=[...new Set(scopedDays.map(d=>dateText(d.date,{month:'long',year:'numeric'})))];
 $('calendar-month').textContent=months.join(' – ');
 $('roster-head').innerHTML='<tr>'+weekdays.map((name,i)=>`<th scope="col" class="${i>=5?'weekend-column':''}">${name}</th>`).join('')+'</tr>';
 const dateMap=new Map(scopedDays.map(d=>[d.date,d]));
 const first=new Date(scopedDays[0].date+'T00:00:00Z');
 first.setUTCDate(first.getUTCDate()-(first.getUTCDay()+6)%7);
 const last=new Date(scopedDays.at(-1).date+'T00:00:00Z');
 last.setUTCDate(last.getUTCDate()+6-(last.getUTCDay()+6)%7);
 const weeks=[];
 for(let cursor=new Date(first);cursor<=last;cursor.setUTCDate(cursor.getUTCDate()+7)){
  const cells=[];
  for(let i=0;i<7;i++){
   const dayDate=new Date(cursor);dayDate.setUTCDate(dayDate.getUTCDate()+i);
   const iso=dayDate.toISOString().slice(0,10), d=dateMap.get(iso);
   if(!d){cells.push(`<td class="calendar-day outside-scope" aria-label="${iso}, outside selected period"><span class="outside-date">${dayDate.getUTCDate()}</span></td>`);continue;}
   const rows=scopedRows.filter(a=>a.day===d.day);
   let content=rows.map(a=>{
    const shift=input.shifts.find(s=>s.id===a.shift_id), originalIndex=allRows.indexOf(a);
    const timeLabel=shift.start+'–'+shift.end+(shift.end<=shift.start?' +1d':'');
    return `<button class="shift-card calendar-event" style="--shift-color:${colors[shift.id]};--shift-bg:${backgrounds[shift.id]}" data-assignment="${originalIndex}" aria-label="${escapeHTML(a.doctor_name)}, ${escapeHTML(shift.name)}, ${escapeHTML(d.date)}, ${escapeHTML(timeLabel)}"><span class="event-shift">${escapeHTML(shift.name)}</span><span class="doctor-name">${doctorName(a.doctor_name,a.seniority)}</span><span class="event-time">${escapeHTML(timeLabel)}</span></button>`;
   }).join('');
   if(!rows.length){
    const unavailable=state.doctor!=='all'&&input.unavailability.some(u=>u.doctor_id===state.doctor&&u.day===d.day);
    const required=input.demand.filter(r=>r.day===d.day&&shifts.some(s=>s.id===r.shift_id)).reduce((sum,r)=>sum+r.required,0);
    content=unavailable?'<span class="unavailable">Unavailable</span>':`<span class="empty-cell">${required===0?'No shifts required':state.doctor!=='all'&&state.shift==='all'?'Off duty':'No matching shifts'}</span>`;
   }
   cells.push(`<td class="calendar-day ${d.is_weekend?'weekend-column':''}" data-date="${d.date}" aria-label="${escapeHTML(d.weekday)}, ${d.date}"><div class="calendar-date"><span>${dayDate.getUTCDate()}</span><span class="calendar-month-label">${dateText(d.date,{month:'short'})}</span></div><div class="calendar-events">${content}</div></td>`);
  }
  weeks.push('<tr>'+cells.join('')+'</tr>');
 }
 $('roster-body').innerHTML=weeks.join('');
}
function renderSummary(){
 $('summary-body').innerHTML=scopedDoctors.map(p=>{
  const rows=scopedRows.filter(a=>a.doctor_id===p.id), horizonCount=counts(allRows,p.id);
  const nights=plan.night_eligible.includes(p.id)?counts(rows,p.id,a=>a.shift_id==='Night'):'N/A';
  const utilization=p.max_shifts?100*horizonCount/p.max_shifts:0;
  return `<tr><td><button class="doctor-button" data-doctor="${escapeHTML(p.id)}">${doctorName(p.name,p.seniority)}</button><div class="role">${escapeHTML(p.seniority)}</div></td><td class="number">${rows.length}</td><td class="number">${nights}</td><td class="number">${rows.filter(a=>a.is_weekend).length}</td><td class="number">${number(rows.reduce((sum,a)=>sum+a.hours,0))}</td><td class="number">${horizonCount} / ${p.max_shifts}<span class="capacity-bar"><span style="width:${utilization}%"></span></span></td></tr>`;
 }).join('');
}
function renderCharts(){
 const names=scopedDoctors.map(p=>p.name), width=$('total-chart').clientWidth;
 const height=$('total-chart').clientHeight;
 const narrow=width<440;
 const layout={paper_bgcolor:'#ffffff',plot_bgcolor:'#ffffff',font:{family:'-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif',size:11,color:'#687586'},margin:{l:42,r:18,t:10,b:narrow?108:90},height,barmode:'stack',bargap:.4,showlegend:true,
  legend:{orientation:'h',x:0,y:narrow?-.43:-.25,font:{size:10}},xaxis:{fixedrange:true,tickangle:narrow?-32:0,tickfont:{size:11}},yaxis:{fixedrange:true,title:{text:'Shifts',font:{size:10}},rangemode:'tozero',dtick:1,gridcolor:'#eef1f5',zeroline:false},hovermode:'closest'};
 const totalTraces=input.shifts.map(s=>({type:'bar',name:s.name,x:names,y:scopedDoctors.map(p=>counts(scopedRows,p.id,a=>a.shift_id===s.id)),marker:{color:colors[s.id]},hovertemplate:'%{x}<br>'+escapeHTML(s.name)+': %{y} shifts<extra></extra>'}));
 const nightY=scopedDoctors.map(p=>plan.night_eligible.includes(p.id)?counts(scopedRows,p.id,a=>a.shift_id==='Night'):null);
 const fairnessTraces=[{type:'bar',name:'Night (eligible juniors)',x:names,y:nightY,marker:{color:colors.Night},hovertemplate:'%{x}<br>Night: %{y} shifts<extra></extra>'},
  {type:'bar',name:'Weekend',x:names,y:scopedDoctors.map(p=>counts(scopedRows,p.id,a=>a.is_weekend)),marker:{color:'#a18855'},hovertemplate:'%{x}<br>Weekend: %{y} shifts<extra></extra>'}];
 const maxCount=Math.max(1,...scopedDoctors.map(p=>counts(scopedRows,p.id)));
 const mainLayout={...layout,yaxis:{...layout.yaxis,range:[0,maxCount+1]}};
 const fairMax=Math.max(1,...nightY.filter(v=>v!==null),...scopedDoctors.map(p=>counts(scopedRows,p.id,a=>a.is_weekend)));
 const fairLayout={...layout,barmode:'group',yaxis:{...layout.yaxis,range:[0,fairMax+1]}};
 Plotly.react('total-chart',totalTraces,mainLayout,options);
 Plotly.react('fairness-chart',fairnessTraces,fairLayout,options);
 plotReady=true;
}
function setTab(tab){
 state.tab=tab;
 for(const name of ['roster','workload']){
  $(name+'-view').hidden=name!==tab;
  $(name+'-tab').setAttribute('aria-selected',String(name===tab));
  $(name+'-tab').tabIndex=name===tab?0:-1;
 }
 if(tab==='workload')renderCharts();
}
function showDialog(title,html){$('dialog-title').textContent=title;$('dialog-body').innerHTML=html;$('details-dialog').showModal();}
function showAssignment(index){
 const a=allRows[index],p=input.doctors.find(p=>p.id===a.doctor_id),s=input.shifts.find(s=>s.id===a.shift_id);
 const off=input.unavailability.filter(u=>u.doctor_id===p.id).map(u=>input.days.find(d=>d.day===u.day).date);
 showDialog(a.doctor_name,`<dl class="details-grid"><div><dt>Shift</dt><dd>${escapeHTML(s.name)} · ${escapeHTML(a.seniority)}</dd></div><div><dt>Start date</dt><dd>${dateText(a.date,{weekday:'long',day:'numeric',month:'short',year:'numeric'})}</dd></div><div><dt>Starts</dt><dd>${escapeHTML(a.start.replace('T',' · '))}</dd></div><div><dt>Ends</dt><dd>${escapeHTML(a.end.replace('T',' · '))}</dd></div><div><dt>Duration</dt><dd>${a.hours} hours</dd></div><div><dt>Full-horizon workload</dt><dd>${counts(allRows,p.id)} / ${p.max_shifts} shifts</dd></div></dl><h3>Unavailable dates</h3><p>${off.length?off.map(d=>dateText(d)).join(', '):'None'}</p><div class="dialog-actions"><button class="button primary" data-doctor="${escapeHTML(p.id)}">View this doctor's assignments</button></div>`);
}
function checksHTML(){return plan.validation.checks.map(c=>`<div class="check"><span>${escapeHTML(c.name)}</span><span>${c.passed?'Passed':'Failed'} · ${c.violations} violations</span></div>`).join('');}
function showSource(){
 const stages=plan.solver.stages.map((s,i)=>`<tr><td>${i+1}</td><td>${escapeHTML(s.name)}</td><td>${s.optimum}</td><td>${escapeHTML(s.status)}</td></tr>`).join('');
 const doctors=input.doctors.map(p=>`<tr><td>${doctorName(p.name,p.seniority)}</td><td>${escapeHTML(p.seniority)}</td><td>${p.max_shifts}</td></tr>`).join('');
 const unavailability=input.unavailability.map(u=>`<tr><td>${escapeHTML(input.doctors.find(p=>p.id===u.doctor_id).name)}</td><td>${dateText(input.days.find(d=>d.day===u.day).date,{day:'numeric',month:'short',year:'numeric'})}</td></tr>`).join('');
 showDialog('Source & rules',`<h3>Workbook</h3><p>${escapeHTML(plan.source.file)} · ${escapeHTML(plan.source.classification)}</p><p class="small-note">Sheets: ${plan.source.sheets.map(escapeHTML).join(', ')}</p><p class="hash">SHA-256: ${escapeHTML(plan.source.sha256)}</p><h3>Scheduling rules</h3><ul>${plan.rules.map(r=>`<li>${escapeHTML(r)}</li>`).join('')}</ul><h3>Fairness objectives · full horizon</h3><p>Each stage minimizes the maximum minus minimum assignment count while preserving earlier optima. Fairness balances shift counts, not working hours.</p><div class="scroll"><table><thead><tr><th>Priority</th><th>Objective</th><th>Spread</th><th>Status</th></tr></thead><tbody>${stages}</tbody></table></div><h3>Doctors</h3><table><thead><tr><th>Name</th><th>Seniority</th><th>Horizon capacity</th></tr></thead><tbody>${doctors}</tbody></table><h3>Unavailable dates</h3><table><thead><tr><th>Doctor</th><th>Date</th></tr></thead><tbody>${unavailability||'<tr><td colspan="2">None</td></tr>'}</tbody></table><h3>Constraint checks</h3>${checksHTML()}<h3>Source notes</h3><ul>${plan.source.readme.map(r=>`<li>${escapeHTML(r)}</li>`).join('')}</ul>`);
}
function csvValue(value){let s=String(value??'');if(/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}
function exportCSV(){
 const fields=['date','weekday','week','shift_id','doctor_id','doctor_name','seniority','start','end','hours','is_weekend'];
 const csv='\ufeff'+[fields,...scopedRows.map(a=>fields.map(f=>a[f]))].map(row=>row.map(csvValue).join(',')).join('\r\n');
 const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'}),url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='physician_schedule.csv';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
for(const [id,key] of [['week-filter','week'],['doctor-filter','doctor'],['shift-filter','shift']]){$(id).addEventListener('change',e=>{state[key]=e.target.value;refresh();});}
$('reset-button').addEventListener('click',()=>{state.week=state.doctor=state.shift='all';['week-filter','doctor-filter','shift-filter'].forEach(id=>$(id).value='all');refresh();});
$('roster-tab').addEventListener('click',()=>setTab('roster'));
$('workload-tab').addEventListener('click',()=>setTab('workload'));
document.querySelector('.tabs').addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();const tab=state.tab==='roster'?'workload':'roster';setTab(tab);$(tab+'-tab').focus();}});
function setMenu(open,focusFirst=false){
 $('dashboard-menu').hidden=!open;
 $('menu-button').setAttribute('aria-expanded',String(open));
 if(open&&focusFirst)$('dashboard-menu').querySelector('button:not(:disabled)').focus();
}
$('menu-button').addEventListener('click',()=>setMenu($('dashboard-menu').hidden,true));
$('menu-button').addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();setMenu(true,true);}});
$('dashboard-menu').addEventListener('keydown',e=>{
 const items=[...$('dashboard-menu').querySelectorAll('button:not(:disabled)')];
 const index=items.indexOf(document.activeElement);
 if(['ArrowDown','ArrowUp','Home','End'].includes(e.key)){
  e.preventDefault();
  const next=e.key==='Home'?0:e.key==='End'?items.length-1:(index+(e.key==='ArrowDown'?1:-1)+items.length)%items.length;
  items[next].focus();
 }else if(e.key==='Escape'){e.preventDefault();setMenu(false);$('menu-button').focus();}
 else if(e.key==='Tab')setMenu(false);
});
document.addEventListener('click',e=>{if(!e.target.closest('.menu-wrap')||e.target.closest('.menu-item'))setMenu(false);});
document.addEventListener('focusin',e=>{if(!e.target.closest('.menu-wrap'))setMenu(false);});
$('calendar-button').addEventListener('click',()=>showDialog('Add to calendar',
 `<div class="paid-icon" aria-hidden="true">▣</div><div class="paid-label">Paid feature</div><h3 class="paid-title">Calendar sync requires a paid plan.</h3><p class="paid-description">Add this schedule to Apple Calendar, Google Calendar or Outlook with a paid plan.</p><div class="dialog-actions"><button class="button primary" data-close-dialog>Got it</button></div>`));
document.addEventListener('click',e=>{if(e.target.closest('[data-close-dialog]'))$('details-dialog').close();});
$('source-button').addEventListener('click',showSource);
$('checks-button').addEventListener('click',()=>showDialog('Constraint checks',checksHTML()));
$('close-dialog').addEventListener('click',()=>$('details-dialog').close());
$('details-dialog').addEventListener('click',e=>{if(e.target===$('details-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
document.addEventListener('click',e=>{const assignment=e.target.closest('[data-assignment]');if(assignment)showAssignment(Number(assignment.dataset.assignment));const doctor=e.target.closest('[data-doctor]');if(doctor){if($('details-dialog').open)$('details-dialog').close();state.doctor=doctor.dataset.doctor;$('doctor-filter').value=state.doctor;refresh();}});
$('export-button').addEventListener('click',exportCSV);
$('print-button').addEventListener('click',()=>{setMenu(false);setTab('roster');window.print();});
let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(state.tab==='workload'&&plotReady)renderCharts();},150);});
refresh();
window.__dashboardReady=true;
</script>
</body>
</html>"""


def shift_interval(calendar_date, shift):
    start = datetime.combine(
        date.fromisoformat(str(calendar_date)[:10]), time.fromisoformat(shift["start"])
    )
    end = datetime.combine(
        date.fromisoformat(str(calendar_date)[:10]), time.fromisoformat(shift["end"])
    )
    if end <= start:
        end += timedelta(days=1)
    return start, end


def collect_result(data, x, stages, night_doctors):
    doctors, days, shifts = data["doctors"], data["days"], data["shifts"]
    assignments = []
    for d in days:
        for s in shifts:
            start, end = shift_interval(d["date"], s)
            for p in doctors:
                if x[p["id"], d["day"], s["id"]].value() > 0.5:
                    assignments.append(
                        {
                            "doctor_id": p["id"],
                            "doctor_name": p["name"],
                            "seniority": p["seniority"],
                            "day": d["day"],
                            "date": d["date"],
                            "weekday": d["weekday"],
                            "week": d["week"],
                            "is_weekend": d["is_weekend"],
                            "shift_id": s["id"],
                            "shift_name": s["name"],
                            "start": start.isoformat(timespec="minutes"),
                            "end": end.isoformat(timespec="minutes"),
                            "hours": (end - start).total_seconds() / 3600,
                        }
                    )
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": data["source"],
        "inputs": {
            k: data[k]
            for k in ("doctors", "shifts", "days", "demand", "unavailability")
        },
        "solver": {"name": "PuLP / CBC", "status": "Optimal", "stages": stages},
        "rules": [
            "Cover each day and shift exactly as required by Demand.",
            "Senior doctors cannot work Night shifts.",
            "Respect every doctor's MaxShifts and unavailable dates.",
            "At most one shift per doctor per start date; no overlapping shifts.",
            "Fairness priority: total shift spread, junior night shift spread, then weekend shift spread.",
            "Weekend assignments use the shift's start date.",
            "No additional minimum rest period or consecutive-day limit is imposed.",
        ],
        "night_eligible": [p["id"] for p in night_doctors],
        "assignments": assignments,
    }


def audit_schedule(result):
    inputs, assignments = result["inputs"], result["assignments"]
    doctors = {p["id"]: p for p in inputs["doctors"]}
    days = {d["day"]: d for d in inputs["days"]}
    shifts = {s["id"]: s for s in inputs["shifts"]}
    unavailable = {(r["doctor_id"], r["day"]) for r in inputs["unavailability"]}
    errors = {
        name: []
        for name in (
            "Assignment data",
            "Exact coverage",
            "Daily limit",
            "Capacity",
            "Unavailability",
            "Night eligibility",
            "No overlap",
        )
    }
    by_slot, by_doctor, by_day = Counter(), {p: [] for p in doctors}, Counter()
    seen = set()
    for a in assignments:
        pid, day, sid = a["doctor_id"], a["day"], a["shift_id"]
        key = (pid, day, sid)
        if pid not in doctors or day not in days or sid not in shifts:
            errors["Assignment data"].append(f"Unknown assignment key: {key}")
            continue
        if key in seen:
            errors["Assignment data"].append(f"Duplicate assignment: {key}")
        seen.add(key)
        start, end = shift_interval(days[day]["date"], shifts[sid])
        expected = {
            "date": days[day]["date"],
            "weekday": days[day]["weekday"],
            "week": days[day]["week"],
            "is_weekend": days[day]["is_weekend"],
            "doctor_name": doctors[pid]["name"],
            "seniority": doctors[pid]["seniority"],
            "shift_name": shifts[sid]["name"],
            "start": start.isoformat(timespec="minutes"),
            "end": end.isoformat(timespec="minutes"),
            "hours": (end - start).total_seconds() / 3600,
        }
        if any(a.get(k) != v for k, v in expected.items()):
            errors["Assignment data"].append(f"Incorrect assignment metadata: {key}")
        by_slot[day, sid] += 1
        by_doctor[pid].append((start, end))
        by_day[pid, day] += 1
        if (pid, day) in unavailable:
            errors["Unavailability"].append(str(key))
        if doctors[pid]["seniority"] == "Senior" and sid == "Night":
            errors["Night eligibility"].append(str(key))
    required = {(r["day"], r["shift_id"]): r["required"] for r in inputs["demand"]}
    for key in set(required) | set(by_slot):
        if by_slot[key] != required.get(key, 0):
            errors["Exact coverage"].append(
                f"{key}: assigned {by_slot[key]}, required {required.get(key, 0)}"
            )
    for key, count in by_day.items():
        if count > 1:
            errors["Daily limit"].append(str(key))
    for pid, intervals in by_doctor.items():
        if len(intervals) > doctors[pid]["max_shifts"]:
            errors["Capacity"].append(pid)
        for first, second in combinations(sorted(intervals), 2):
            if first[0] < second[1] and second[0] < first[1]:
                errors["No overlap"].append(pid)
    checks = [
        {
            "name": name,
            "passed": not messages,
            "violations": len(messages),
            "details": messages,
        }
        for name, messages in errors.items()
    ]
    return {
        "passed": all(c["passed"] for c in checks),
        "checks": checks,
        "total_violations": sum(c["violations"] for c in checks),
    }


def save_schedule(data, x, stages, night_doctors, output_dir):
    """Format the solved variables, audit the result and write the dashboard files."""
    result = collect_result(data, x, stages, night_doctors)
    result["validation"] = audit_schedule(result)
    if not result["validation"]["passed"]:
        raise RuntimeError(json.dumps(result["validation"], indent=2))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "schedule.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return result, generate_dashboard(result, output_dir / "dashboard.html")


def main() -> None:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Render the solved scheduling dashboard."
    )
    parser.add_argument(
        "result", nargs="?", type=Path, default=base / "output" / "schedule.json"
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=base / "output" / "dashboard.html"
    )
    args = parser.parse_args()
    result = json.loads(args.result.read_text(encoding="utf-8"))
    print(generate_dashboard(result, args.output))


if __name__ == "__main__":
    main()
