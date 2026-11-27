"""Evidence-only exports. Never insert invented results or AI commentary."""
from __future__ import annotations
import csv
from io import BytesIO, StringIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
import json


def report_record(experiment: dict, run: dict) -> dict:
    return {'report_version':'axiom-report-v1', 'experiment':{
        'id':experiment['id'],'name':experiment['name'],
        'dataset_id':experiment['dataset_id'],'dataset_sha256':experiment['dataset_sha256'],
        'created_at':experiment['created_at']},
        'run':run,
        'limitations':['A saved computation is not evidence of causality.',
                       'Chart point coordinates represent observation order, not time.',
                       'Data integrity is verified on import/replay; exporting this historical record does not re-read source bytes.']}


def json_report(record: dict) -> bytes:
    return json.dumps(record,sort_keys=True,indent=2,allow_nan=False).encode('utf-8')


def csv_report(record: dict) -> bytes:
    out=StringIO(newline='')
    writer=csv.writer(out)
    writer.writerow(('observation_index','recorded_value'))
    for point in record['run']['result']['points']:
        # Numeric coordinates only; text cells are never interpolated as spreadsheet formulas.
        writer.writerow((point['x'],point['y']))
    return out.getvalue().encode('utf-8-sig')


def pdf_report(record: dict) -> bytes:
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,leftMargin=46,rightMargin=46,topMargin=50,bottomMargin=50)
    styles=getSampleStyleSheet()
    story=[]
    def paragraph(label: str, value:object) -> None:
        story.append(Paragraph(f'<b>{escape(label)}:</b> {escape(str(value))}',styles['BodyText']))
        story.append(Spacer(1,4))
    story.append(Paragraph('AXIOM LAB / Scientific Run Record',styles['Title']))
    story.append(Spacer(1,9))
    e=record['experiment'];run=record['run'];result=run['result']
    for key in ('name','id','dataset_id','dataset_sha256','created_at'):
        paragraph(key.replace('_',' ').title(), e[key])
    for key in ('id','revision','method','created_at','status'):
        paragraph('Run '+key.replace('_',' ').title(), run[key])
    paragraph('Parameters (recorded)',json.dumps(run['configuration'],ensure_ascii=True,sort_keys=True))
    paragraph('Execution environment (recorded)',json.dumps(run['environment'],ensure_ascii=True,sort_keys=True))
    paragraph('Column',result.get('column','N/A'))
    paragraph('Original observations',result.get('original_point_count'))
    paragraph('Chart points exported',result.get('shown_point_count'))
    paragraph('Sampled display',result.get('sampled'))
    paragraph('Missing observations',result.get('missing_count'))
    paragraph('Method note',result.get('note','No method notes provided.'))
    story.append(Paragraph('Recorded plot values (first 20)',styles['Heading2']))
    table_data=[['Observation index','Recorded value']]
    table_data += [[str(p['x']),str(p['y'])] for p in result.get('points',[])[:20]]
    table=Table(table_data,colWidths=[130,290],hAlign='LEFT')
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E6ECEA')),
                               ('GRID',(0,0),(-1,-1),0.3,colors.grey),
                               ('BOTTOMPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4)]))
    story.append(table)
    story.append(Spacer(1,12))
    story.append(Paragraph('Limitations',styles['Heading2']))
    for item in record['limitations']:
        story.append(Paragraph('- '+escape(item),styles['BodyText']))
    doc.build(story)
    return buffer.getvalue()
