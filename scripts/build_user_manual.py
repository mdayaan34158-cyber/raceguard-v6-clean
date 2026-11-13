"""Regenerate the current two-page Streamlit user guide (requirements-docs.txt)."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'docs/USER_MANUAL.pdf'
ink=colors.HexColor('#152b3b');mint=colors.HexColor('#007f73')
styles={'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=22,leading=26,textColor=ink,spaceAfter=10),'sub':ParagraphStyle('sub',fontSize=10,leading=14,textColor=colors.HexColor('#506779'),spaceAfter=12),'h':ParagraphStyle('h',fontName='Helvetica-Bold',fontSize=12,leading=15,textColor=mint,spaceBefore=9,spaceAfter=5),'p':ParagraphStyle('p',fontSize=9.3,leading=12.5,textColor=ink,spaceAfter=6),'small':ParagraphStyle('small',fontSize=8.6,leading=11.5,textColor=colors.HexColor('#506779'),spaceAfter=5)}
story=[]
def add(t,s='p'):story.append(Paragraph(t,styles[s]))
def box(t):
 tab=Table([[Paragraph(t,styles['p'])]],colWidths=[499]);tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#e8f5f1')),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#adcec5')),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.append(tab)
def footer(c,doc):
 w,h=A4;c.setFillColor(mint);c.rect(0,h-12,w,12,fill=1,stroke=0);c.setFont('Helvetica-Bold',8);c.setFillColor(ink);c.drawString(48,h-35,'RACEGUARD / STREAMLIT v6 / USER GUIDE');c.setStrokeColor(colors.HexColor('#cfdee3'));c.line(48,40,w-48,40);c.setFont('Helvetica',8);c.drawString(48,26,'Educational decision support | Cross-checked release v6');c.drawRightString(w-48,26,f'{doc.page} / 2')
add('Run & deploy in Streamlit','title');add('Machine Learning-Based Bearing Fault Classification in Induction Motors<br/>RaceGuard-style native Streamlit interface - main implementation: app.py.','sub')
box('<b>Important:</b> software readiness is not equipment health. Classification does not establish severity, safe operation or remaining life. RUL is conditional on supplied assumptions/history; sound is digital amplitude, not certified SPL/dBA.')
add('01  Extract and start locally','h')
add('Extract the complete ZIP. Open <b>bearing-streamlit</b>, containing <b>app.py</b> and requirements.txt. Install Python <b>3.13</b>. Keep assets/, src/, models/, data/, docs/ and .streamlit/ folders together.')
add('Windows: run <b>RUN_WINDOWS.bat</b>. macOS/Linux: run <b>sh RUN_MAC_LINUX.sh</b>. They create an environment, install pinned dependencies and launch Streamlit. Internet is needed for installation. Alternatively install requirements.txt and run <b>python -m streamlit run app.py</b>.')
add('Open <b>http://localhost:8501/</b>. Keep the terminal running; Ctrl+C stops it. Do not run with plain python app.py and do not use the older launch.py/Gradio commands in the archived previous source.')
add('02  Deploy to Streamlit Community Cloud','h')
add('Put the extracted project <b>contents</b> in a repository accessible to your Streamlit Community Cloud account. Keep app.py, requirements.txt and .streamlit/config.toml at the project root. Review DATA_RIGHTS.md before making benchmark excerpts public.')
add('Create a new app in Community Cloud; select the repository/branch and <b>app.py</b> as the main file. In advanced settings select Python <b>3.13</b> where available. Wait for build logs, then open and verify the actual assigned URL. Keep assets/raceguard.css for the RaceGuard styling. No Gradio SDK, GPU, app secret or second backend is required.')
add('If Python3.13 is unavailable on your host, use the supplied Python3.13 Dockerfile on a compatible container host or retest a supported runtime; do not assume compatibility. Remote account publication and Docker/Windows/macOS execution were not performed here. Detailed instructions: START_HERE_DEPLOYMENT.md.','small')
add('03  Analyse vibration evidence','h')
add('Select <b>Vibration</b> in the sidebar. Start with CWRU benchmark / Normal and <b>Run vibration analysis</b>. For measured data choose CSV upload, preview columns and select the actual signal; or paste measured samples. Enter the <b>true sampling rate</b> and optional known RPM.')
add('The stored classifier requires compatible <b>48kHz drive-end acceleration in g</b>, with 4,096-sample windows. Declare compatibility only if true. Otherwise use signal mode. No silent resampling, missing-row removal or imputation is applied.')
add('Synthetic illustration / numeric builder generate actual waveforms but are always signal-only. Success says <b>Signal analysis complete</b>, not an invented fault class. Optional actual geometry changes explanatory bearing-frequency markers, not the trained classifier.')
add('Inspect source/status, waveform, FFT, features and complete formula ledger. Window agreement is not failure probability. Download JSON, feature CSV, printable HTML and pasted/generated waveform when available. Session history retains five successful runs, explicitly labelled historical.')
add('Changing inputs hides stale output until you run again. A failed calculation clears the current result/downloads; correct the stated error, not the physical measurements just to force a prediction.','small')
story.append(PageBreak())
add('Life planning & recorded sound','title');add('Use the sidebar to change workspace. Export before closing: session results are not a persistent telemetry database.','sub')
add('04  RUL & life planning','h')
add('<b>Budget:</b> choose hours/days/cycles consistently; enter actual accumulated operating age and justified nominal total service life. Paired min/max totals must bracket nominal. Age200 / total1,000 hours gives <b>800 hours allowance</b>; totals900-1,200 give a700-1,000-hour scenario range. These are assumptions, not measured bearing life.')
add('<b>Trend:</b> upload/paste <b>age,indicator</b> CSV with at least six unique increasing cumulative operating ages from the same asset/regime and a higher-is-worse indicator. Enter a justified healthy reference, higher maintenance limit and fit gate. The downloadable synthetic example demonstrates format only.')
add('Read current/projected operating age, remaining estimate, supported bounds, observed/fit/limit and prefix-history graphs. <b>R2 is fit quality, not reliability.</b> A fitted-crossing interval is conditional on linear-model assumptions, not an individual bearing-lifetime guarantee. Flat/poor trends withhold forecasts. Meters show budget/indicator position, not failure risk. All warnings are project examples.')
add('05  Analyse sound after recording/upload','h')
add('Choose <b>Sound</b>, then simulation, WAV, microphone recording or external log. Click <b>Analyse sound</b>. Simulation processes a real generated sine/envelope and stays labelled SIMULATED; the whole-record average may be below the entered upper target.')
add('<b>WAV:</b> uncompressed PCM/float, up to20MB,300seconds,1-8channels,1-192kHz and10million selected samples. Channel0 is first. The included amplitude0.1 sine averages approximately <b>-23.01dBFS RMS</b>.')
add('<b>Microphone:</b> allow browser permission, Record, then <b>Stop</b>, then Analyse sound. HTTPS/localhost and a real device are needed. This is a <b>completed recording, not continuously streaming live telemetry</b>. Failure never substitutes simulated audio as a microphone result.')
add('<b>External log:</b> paste/upload <b>level_db,duration_sec</b>; durations must be positive. Choose dBFS or <b>User-declared dB SPL (unverified)</b>. Do not mix conventions/weightings. Calibration/instrument accuracy are not independently verified.')
box('<b>Privacy / hardware:</b> recordings are uploaded to the Streamlit server for analysis. Do not record sensitive audio on public/untrusted hosts. Browser gain, encoding and preprocessing may change amplitude. A virtual microphone software test is not physical acoustic calibration. Close the tab/revoke permission if needed to fully release microphone hardware.')
add('06  Units, ranges, alerts & troubleshooting','h')
add('<b>dBFS is not SPL/dBA/dBC.</b> RMS level=20log10(RMS/1). A full-amplitude sine is-3.01dBFS RMS; silence has no finite level, not0dB. Min/max/current are interval RMS levels. The average uses energy/duration weighting, not arithmetic dB averaging. Sample peak is not true peak.')
add('Set ordered display bounds and warning/high alerts. Raw defaults -90..0dBFS and -20/-6 alerts are illustrative, <b>not safe-exposure limits</b>. Numbers stay visible outside the graph range; the meter clips position only. Nonzero reference offset needs a documented note and remains unverified, not certified SPL.')
add('<b>Page/build fails:</b> check terminal/logs, Python/pins, full folder upload and correct Streamlit entry point. <b>Microphone denied:</b> check permission, hardware and HTTPS/direct app URL. <b>No RUL:</b> inspect real history, slope, fit gate and threshold. No A/C weighting, IEC time weighting, exposure compliance, guaranteed life or safety certification is supplied.')
add('Current verification: <b>docs/TEST_REPORT.md</b>. The archive/ folder contains the complete prior source only for preservation; it is not the active framework or current instructions.','small')
SimpleDocTemplate(str(DEST),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=58,bottomMargin=51,title='RaceGuard Streamlit | Two-page user guide',author='RaceGuard project').build(story,onFirstPage=footer,onLaterPages=footer)
print(DEST)
