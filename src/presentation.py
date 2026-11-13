"""RaceGuard's visual presentation; no inference or fabricated health metrics here."""
from html import escape
from base64 import b64encode
from math import sin,cos,pi

def esc(value):return escape(str(value),quote=True)

def hero(page,model_name=None):
    titles={'Vibration':('Analysis studio.','From vibration to an explainable diagnostic review.'),'RUL':('RUL & life planning.','Declared service allowances and conditional degradation evidence.'),'Sound':('Sound meter.','Recorded digital audio, transparent units and source-labelled results.'),'Evidence & guide':('Model & evidence.','Measured benchmark evidence, scope and operating guidance.')}
    title,subtitle=titles[page];badge='● Software ready · '+model_name if model_name else 'Software readiness unavailable'
    return f'<section class="rg-hero"><div><div class="rg-eyebrow">Machine Learning-Based Bearing Fault Classification in Induction Motors</div><h1>{title}</h1><p>{subtitle}</p></div><div class="rg-pill{chr(32)+"off" if not model_name else ""}">{esc(badge)}</div></section>'

def kpis(result=None):
    if result:
        agreement=result['window_agreement'];rms=result['stats'].get('rms')
        rows=[('ANALYSIS RESULT',result['predicted_class'],'Benchmark class' if result['classification_status']=='performed' else 'Classification not run by design'),('RMS AMPLITUDE',f'{rms:.5g}' if rms is not None else 'Unavailable',result['units']),('COMPLETE WINDOWS',result['n_windows'],f"{result['n_samples']:,} input samples · {result['fs']:g} Hz"),('WINDOW AGREEMENT',f'{agreement:.1%}' if agreement is not None else 'Not assessed','Vote consistency, NOT failure probability')]
    else:rows=[('ANALYSIS RESULT','Not assessed','Run a measured or labelled synthetic input'),('RMS AMPLITUDE','—','No current processed waveform'),('COMPLETE WINDOWS','—','No current processed input'),('WINDOW AGREEMENT','Not assessed','No equipment health is inferred from software readiness')]
    return '<div class="rg-kpis">'+''.join(f'<article class="rg-kpi"><label>{esc(a)}</label><strong>{esc(b)}</strong><small>{esc(c)}</small></article>' for a,b,c in rows)+'</div>'

def bearing(result,prefix='v'):
    gradient='rg-steel-'+esc(prefix)
    label=result['predicted_class'] if result else 'Not assessed';classified=bool(result) and result['classification_status']=='performed'
    outer='#f6b764' if classified and label=='Outer Race Fault' else '#6f9db2'
    inner='#f6b764' if classified and label=='Inner Race Fault' else '#a1c3d1'
    balls='#f6b764' if classified and label=='Rolling Element Fault' else '#84b3c4'
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 240" role="img" aria-label="Illustrative bearing component map, not a measured defect location"><defs><radialGradient id="{gradient}"><stop stop-color="#b7d2dc"/><stop offset="1" stop-color="#315264"/></radialGradient></defs>',f'<circle cx="310" cy="118" r="91" fill="#0b1822" stroke="{outer}" stroke-width="18"/>',f'<circle cx="310" cy="118" r="49" fill="#102432" stroke="{inner}" stroke-width="15"/>','<circle cx="310" cy="118" r="28" fill="#08131c" stroke="#35566a" stroke-width="2"/>']
    for i in range(9):
        a=i*2*pi/9;x=310+70*cos(a);y=118+70*sin(a);parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="12" fill="url(#{gradient})" stroke="{balls}" stroke-width="3"/>')
    parts+=['<path d="M105 61H206M414 61H515M105 177H206M414 177H515" stroke="#355768" stroke-width="1"/>','<text x="78" y="49" fill="#89a0b0" font-size="11">OUTER RACE</text><text x="460" y="49" fill="#89a0b0" font-size="11">INNER RACE</text><text x="64" y="196" fill="#89a0b0" font-size="11">ROLLING ELEMENTS</text><text x="454" y="196" fill="#89a0b0" font-size="11">SCHEMATIC ONLY</text></svg>']
    note='Highlight maps the benchmark class to an illustrative component; it is not spatial localization or a severity estimate.' if classified else 'No fault component is highlighted: signal processing succeeded, but classification was intentionally not run.'
    if classified and label=='Normal':note='Predicted benchmark class: Normal. No fault component is highlighted; safe operation is not certified.'
    if result is None:note='No current processed waveform. Run a valid input; software readiness does not assess this asset.'
    svg_image='<img class="rg-bearing-image" alt="Illustrative bearing component map, not a measured defect location" src="data:image/svg+xml;base64,'+b64encode(''.join(parts).encode()).decode()+'">'
    return '<div class="rg-bearing"><div class="rg-bearing-header"><strong>Bearing diagnostic view</strong><span>ILLUSTRATIVE · NOT TO SCALE</span></div>'+svg_image+f'<div class="rg-bearing-footer"><strong>{esc(label)}</strong>{esc(note)}</div></div>'

BRAND='<div class="rg-brand"><span class="rg-logo" aria-hidden="true"><i></i></span><div><strong>RACEGUARD</strong><small>CONDITION INTELLIGENCE</small></div></div>'

NOTICE='<div class="rg-notice"><strong>EDUCATIONAL DECISION SUPPORT</strong>Benchmark classification, declared-input life planning and uncalibrated digital sound. Not a machinery safety system.</div>'
FOOTER='<div class="rg-footer"><span>RACEGUARD · EVIDENCE BEFORE CERTAINTY</span><span>Native Streamlit · software readiness is not equipment health</span></div>'
