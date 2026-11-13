"""Canonical app.py, compatibility entry point and evidence-only RaceGuard visuals."""
from pathlib import Path
import json,re,base64

def svg_text(html):return base64.b64decode(re.search(r"base64,([^\"]+)",html).group(1)).decode()
from streamlit.testing.v1 import AppTest
from src.services import ROOT,vibration
from src.presentation import hero,kpis,bearing,BRAND

def button(at,label):return next(x for x in at.button if x.label==label)

def test_canonical_main_contains_real_interface_not_just_wrapper():
 source=(ROOT/'app.py').read_text();assert 'def vibration_page()' in source and 'def rul_page()' in source and 'def sound_page()' in source
 assert "ROOT/'assets/raceguard.css'" in source;assert 'runpy.run_path' not in source
 wrapper=(ROOT/'streamlit_app.py').read_text();assert "with_name('app.py')" in wrapper
 assert 'app.py' in (ROOT/'RUN_MAC_LINUX.sh').read_text();assert 'app.py' in (ROOT/'RUN_WINDOWS.bat').read_text();assert 'app.py' in (ROOT/'Dockerfile').read_text()

def test_canonical_main_all_pages_and_actual_model():
 at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run();assert not at.exception
 button(at,'Run vibration analysis').click().run();assert not at.exception;assert at.session_state['v_result']['data']['predicted_class']=='Normal'
 for page,action in [('RUL','Calculate RUL / allowance'),('Sound','Analyse sound')]:
  at.sidebar.radio[0].set_value(page).run();button(at,action).click().run();assert not at.exception
 at.sidebar.radio[0].set_value('Evidence & guide').run();assert not at.exception

def test_alias_uses_same_result_and_main_visual_helpers():
 a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run();b=AppTest.from_file(str(ROOT/'streamlit_app.py'),default_timeout=30).run()
 for at in [a,b]:button(at,'Run vibration analysis').click().run();assert not at.exception
 assert a.session_state['v_result']['data']==b.session_state['v_result']['data']

def test_kpis_before_run_do_not_fabricate_health():
 html=kpis();assert 'Not assessed' in html and '100%' not in html;assert 'No current processed waveform' in html
 assert 'software readiness' in html

def test_synthetic_visual_never_highlights_a_fault():
 d=vibration({'source':'synthetic','sample':'outer_race_fault'});html=bearing(d)
 assert '#f6b764' not in svg_text(html);assert 'classification was intentionally not run' in html
 assert 'Signal analysis complete' in html;assert 'not a measured defect location' in html

def test_class_map_and_duplicate_svg_ids_scoped():
 d=vibration({'source':'sample','sample':'outer_race_fault'})
 a=bearing(d,'v');b=bearing(d,'history');assert 'id="rg-steel-v"' in svg_text(a) and 'url(#rg-steel-v)' in svg_text(a)
 assert 'id="rg-steel-history"' in svg_text(b);assert '#f6b764' in svg_text(a);assert 'not spatial localization' in a

def test_user_content_escaped_in_visuals():
 d=vibration({'source':'synthetic'});d['predicted_class']='<script>alert(1)</script>'
 assert '<script>' not in bearing(d);assert '&lt;script&gt;' in bearing(d);assert '<script>' not in kpis(d)
 assert '<script>' not in hero('Vibration','<script>')

def test_styles_are_bundled_and_not_remote_dependencies():
 css=(ROOT/'assets/raceguard.css').read_text();assert '#53dfca' in css and '#091119' in css
 assert '@media(max-width:600px)' in css;assert 'url(http' not in css
 assert '<iframe' not in (ROOT/'app.py').read_text();assert 'CONDITION INTELLIGENCE' in BRAND
