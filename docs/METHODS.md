# Numerical methods and interpretation

The framework changed; numerical kernels and trained model artifact are preserved from the audited project. The full previous package, including detailed data/model audit and historical technical reports, is in archive/previous_v4_source.zip. It is archival, not a runtime dependency.

## Vibration
- Classification domain: declared compatible48kHz CWRU drive-end acceleration in g;4,096-sample nonoverlapping windows, each demeaned identically to training. Tail samples excluded from complete model windows are disclosed. Whole-input statistics and window scopes differ explicitly.
- Twelve features, FFT and all-window sufficient-statistic/formula ledgers use actual data. Sample-rate/time-column agreement, finite data and numerical bounds are checked. No silent resampling, row removal/interpolation or calibration assumption.
- The Random Forest/artifact/evaluation are unchanged. Historical same-rig/small-subset performance is not independent-bearing/industrial validation. Window agreement is a vote-consistency measure, not calibrated fault/failure probability. Provisional review labels are not severity, location certainty or safe-operation decisions.
- Signal-only/synthetic outputs report completed analysis with intentional nonclassification. They are not mapped to arbitrary real fault classes or remaining life. Supplied geometry changes explanatory frequency markers only.
- An older demo_reference.py contains historical preprocessing helpers, including an interpolation helper. Those helpers are not used by the active measured-data path. src/services.py calls strict processing.py validation and only the explicit synthetic generator from that module.

## RUL
- Budget: remaining=max(0,nominal−age); optional endpoints=max(0,entered lower/upper total−age). Maximum life means supplied scenario only; absent input is unavailable. Operating hours/days/cycles are not automatically converted to calendar age.
- Trend: at least6 and at most2,000 paired nonnegative finite age/indicator values, unique increasing ages, same asset/regime and higher indicator=worse. A healthy reference and justified higher maintenance limit are supplied by the user. CWRU recordings do not form an asset-lifetime sequence.
- Centered OLS indicator=c+b(age−mean age). Crossing age=mean age+(limit−c)/b. Remaining=max(0,crossing−latest age). Nonpositive slope/insufficient configurable R² gate/numerical crossing bounds withhold forecasts. Reached threshold yields0, not a certified bearing failure diagnosis.
- Approximate95% fitted-crossing interval uses centered coefficient covariance, Student-t and the delta method; only supported positive-slope/numerically finite bounds are issued. It is conditional on linear-model residual assumptions and entered threshold, not a95% individual lifetime/survival interval. Threshold uncertainty/process drift/future individual variability are excluded. No real maximum life is inferred.
- R², residual RMSE and last-two-point indicator holdout RMSE describe fit/prediction in entered indicator units, not life accuracy/reliability percentages. Prefix history refits chronological prefixes, not independent failures. Plot projection is bounded to5 observed spans; a numeric crossing may lie beyond the plotted horizon.
- Meters show consumed budget or (latest indicator−reference)/(limit−reference), clipped0..1. Those are positions, not failure probability. Alerts are configured examples, not service standards.

## Sound
- RMS=sqrt(sum(x²)/N); raw level=20log10(RMS/1)dBFS. Here RMS=1defines0dBFS, so a full-amplitude sine has−3.0103dBFS RMS, amplitude0.1sine≈−23.0103dBFS. PCM integers use explicit full-scale normalization; float WAV keeps supplied native amplitude within bounds, not silent renormalization. Zero-based channel is explicit.
- Whole-record average derives from total sample energy/count. Log average=10log10(sum(duration×10^(level/10))/sum duration), using stable peak-referenced arithmetic. Arithmetic averaging of dB is not used.
- Current/min/max are disjoint≈0.25second interval RMS/log levels, with a shorter final block. Silence has no finite level (null/−infinity), not0dB. A record including a silent interval has no finite minimum. Sample peak is max|x|, not intersample true peak. Near-full-scale count flags possible digital clipping, not certified analog clipping.
- Display meter=clip((displayed level−low)/(high−low),0,1); graph has fixed entered dB range. This is linear on a dB display, not physical intensity/pressure. Numerical overrange remains visible. Silence creates chart gaps.
- Optional offset requires documented user reference/conditions, applies only to digital sources, retains raw values and is labelled unverified/not certified SPL. External SPL logs remain user-declared/unverified. No dBA/dBC, A/C frequency weighting, IEC Fast/Slow, exposure compliance or certified accuracy.
- Native Streamlit **completed microphone recording** is uploaded to the server. There is no continuous streaming feature. Browser gain/codec/resampling/device preprocessing may affect amplitude; physical acoustic calibration is unknown. Simulation is actual generated audio and explicitly labelled, never a fake microphone fallback.

Reproducible format examples and strict validation remain in the supplied data/sample_data and tests. The UI exports JSON with formulas, units, sources, limitations and display settings; CSV preserves raw/displayed interval levels. Default inputs/alerts are illustrative values to replace, not standards or safe limits.
