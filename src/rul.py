"""Transparent maintenance-life planning / conditional trend extrapolation, NOT a CWRU RUL model."""
import numpy as np
from scipy.stats import t as student_t


def finite(value,name,low=None,high=None):
    try:v=float(value)
    except (ValueError,TypeError) as exc:raise ValueError(f'{name} must be numeric.') from exc
    if not np.isfinite(v) or (low is not None and v<low) or (high is not None and v>high):
        raise ValueError(f'{name} must be finite'+(f' and at least {low}' if low is not None else '')+(f' and at most {high}' if high is not None else '')+'.')
    return v


def alerts(remaining,warning,critical):
    if remaining is None:return 'Insufficient evidence'
    if remaining<=critical:return 'Critical — project threshold'
    if remaining<=warning:return 'Warning — project threshold'
    return 'Above configured alert thresholds'


def settings(data):
    unit=data.get('unit','hours')
    if unit not in ('hours','days','cycles'):raise ValueError('Choose hours, days or cycles; no automatic calendar conversion is made.')
    warning=finite(data.get('warning',10),'Warning threshold',0,1e12)
    critical=finite(data.get('critical',1),'Critical threshold',0,1e12)
    if critical>warning:raise ValueError('Critical remaining-life threshold must not exceed the warning threshold.')
    return unit,warning,critical


def life_budget(data):
    unit,warning,critical=settings(data)
    nominal=finite(data.get('nominal'),'Expected design/service life',1e-9,1e12)
    age=finite(data.get('age'),'Accumulated operating age',0,1e12)
    low=data.get('life_min');high=data.get('life_max')
    if (low in (None,'')) != (high in (None,'')):raise ValueError('Supply both lower and upper service-life assumptions, or leave both blank.')
    lo=hi=None
    if low not in (None,''):
        lo=finite(low,'Lower assumed total life',1e-9,1e12);hi=finite(high,'Upper assumed total life',1e-9,1e12)
        if not lo<=nominal<=hi:raise ValueError('Life assumptions must satisfy lower ≤ nominal ≤ upper.')
    remaining=max(0.,nominal-age)
    ages=np.linspace(0,max(nominal,age,hi or nominal),60)
    return dict(mode='budget',source='User-provided maintenance-life assumptions',unit=unit,remaining=remaining,remaining_min=max(0.,lo-age) if lo is not None else None,remaining_max=max(0.,hi-age) if hi is not None else None,current_age=age,expected_total=nominal,maximum_expected_life=hi,consumed_fraction=min(1.,age/nominal),health_label='Service-life budget consumed — NOT measured equipment health',status=alerts(remaining,warning,critical),warning=warning,critical=critical,reliability='No prediction confidence: arithmetic planning allowance, not a measured failure-time forecast.',range_label='User-supplied scenario range, NOT a statistical confidence interval',overdue=max(0.,age-nominal),trend={'age':ages.tolist(),'remaining':np.maximum(0,nominal-ages).tolist(),'label':'Assumed schedule, not observed degradation'},history=[],formulas=[f'Remaining allowance = max(0, {nominal:g} − {age:g}) = {remaining:g} {unit}',f'Consumed budget = min(1, {age:g}/{nominal:g}) = {min(1.,age/nominal):.6g}'],limitations=['Design/service life must come from a declared source; no universal maximum bearing life is supplied.','A healthy/faulty vibration class cannot determine remaining life.','Scenario range reflects entered assumptions only. Operating days are not automatically calendar days.'])


def _fit(x,y):
    xc=x-x.mean();sxx=float(xc@xc)
    if sxx<=0:raise ValueError('Operating-age history must span a positive interval.')
    b=float(xc@(y-y.mean())/sxx);a=float(y.mean()-b*x.mean());res=y-(y.mean()+b*xc);sse=float(res@res);sst=float(np.sum((y-y.mean())**2))
    r2=1-sse/sst if sst>1e-24 else 0.
    variance=sse/(len(x)-2)
    # Covariance of [indicator at mean age, slope], avoiding huge-age cancellation.
    cov=np.array([[variance/len(x),0.],[0.,variance/sxx]])
    return a,b,float(r2),cov,float(np.sqrt(sse/len(x)))


def trend_rul(data,ages,indicator,source='User-provided degradation history'):
    unit,warning,critical=settings(data)
    x=np.asarray(ages,dtype=float);y=np.asarray(indicator,dtype=float)
    if x.ndim!=1 or y.ndim!=1 or len(x)!=len(y) or not 6<=len(x)<=2000:raise ValueError('Trend requires 6–2000 paired operating-age / health-indicator observations.')
    if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Trend contains missing, infinite or nonnumeric data. No records were discarded.')
    if np.any(x<0) or np.any(y<0) or np.any(x>1e12) or np.any(y>1e9):raise ValueError('Trend ages/indicators must be nonnegative and within supported numeric bounds.')
    if np.any(np.diff(x)<=0):raise ValueError('Operating ages must be strictly increasing and unique, in acquisition order.')
    baseline=finite(data.get('baseline',0),'Healthy reference indicator',0,1e9)
    limit=finite(data.get('limit',1),'Failure/maintenance indicator limit',0,1e9)
    gate=finite(data.get('min_r2',.5),'Minimum R² display gate',0,1)
    if limit<=baseline:raise ValueError('Failure/maintenance indicator limit must exceed the healthy reference; higher indicator means worse condition.')
    a,b,r2,cov,rmse=_fit(x,y);current=float(x[-1]);confidence=float(student_t.ppf(.975,len(x)-2));se_b=float(np.sqrt(max(0.,cov[1,1])));slope_low=b-confidence*se_b
    projected=None;remaining=None;lower=None;upper=None
    crossed=bool(y[-1]>=limit)
    acceptable=b>0 and r2>=gate
    if crossed:
        remaining=0.;lower=0.;upper=0.;projected=current
    elif acceptable:
        projected=float(x.mean()+(limit-y.mean())/b)
        if not np.isfinite(projected) or abs(projected)>1e15:
            projected=None;acceptable=False
        else:remaining=max(0.,projected-current)
        if acceptable and slope_low>0 and abs(b)>1e-150:
            # Delta-method CI of the FITTED LINE's threshold crossing, not individual failure time.
            g=np.array([-1/b,-(limit-y.mean())/(b*b)])
            with np.errstate(over='ignore',invalid='ignore'):
                variance_cross=float(g@cov@g)
                sd=float(np.sqrt(max(0.,variance_cross))) if np.isfinite(variance_cross) else float('inf')
                delta=confidence*sd
            if np.isfinite(delta) and max(abs(projected-delta),abs(projected+delta))<=1e15:
                lower=max(0.,projected-delta-current);upper=max(0.,projected+delta-current)
    hist=[]
    for n in range(6,len(x)+1):
        aa,bb,rr,_,_=_fit(x[:n],y[:n]);v=0. if y[n-1]>=limit else max(0.,x[:n].mean()+(limit-y[:n].mean())/bb-x[n-1]) if bb>0 and rr>=gate else None
        if v is not None and (not np.isfinite(v) or abs(v)>1e15):v=None
        hist.append({'age':float(x[n-1]),'remaining':float(v) if v is not None else None})
    aa,bb,_,_,_=_fit(x[:-2],y[:-2]);holdout=float(np.sqrt(np.mean((y[-2:]-(y[:-2].mean()+bb*(x[-2:]-x[:-2].mean())))**2)))
    horizon=current if projected is None else max(current,min(projected,current+5*(x[-1]-x[0])))
    line_x=np.linspace(float(x[0]),horizon,100);fitted=y.mean()+b*(line_x-x.mean())
    limitations=['Conditional straight-line extrapolation of a supplied higher-is-worse indicator, NOT an ML failure-time model or survival probability.','Crossing ages outside ±1e15 chosen units exceed supported numeric bounds; no estimate is issued.', 'The indicator, healthy reference and maintenance/failure threshold must be justified for this component and operating regime.','95% range is an approximate delta-method interval for the fitted-line crossing under independent, homoscedastic, approximately normal residual assumptions. It excludes future process drift, threshold uncertainty and individual failure-time variability.','R² and last-two-point indicator backtest RMSE describe fit/prediction in indicator units, NOT reliability percentages.']
    if remaining is not None and remaining>(x[-1]-x[0]):limitations.append('The estimated remaining horizon exceeds the observed time span: extrapolation is especially fragile.')
    if acceptable and lower is None and slope_low>0:limitations.append('Crossing range withheld: coefficient scale or crossing bounds exceed supported numerical precision/range.')
    if acceptable and slope_low<=0:limitations.append('The slope interval includes zero: finite upper crossing bound is unsupported; range is intentionally unavailable.')
    if not acceptable and not crossed:limitations.append(f'No numeric RUL is issued: slope must be positive and R² must meet the configurable display gate ({gate:g}); this gate is a project screening rule, not engineering validation.')
    return dict(mode='trend',source=source,unit=unit,remaining=remaining,remaining_min=lower,remaining_max=upper,current_age=current,expected_total=projected,maximum_expected_life=None,consumed_fraction=float(np.clip((y[-1]-baseline)/(limit-baseline),0,1)),health_label='Indicator position between entered reference and limit — NOT failure probability',status='Threshold already reached — inspect' if crossed else alerts(remaining,warning,critical),warning=warning,critical=critical,reliability='Conditional extrapolation only; no validated equipment-life confidence or survival probability.',range_label='Approximate 95% fitted-line crossing interval (conditional; NOT individual failure time)' if lower is not None and not crossed else 'Range unavailable or threshold already reached; see assumptions',fit={'intercept':a,'centered_intercept':float(y.mean()),'age_center':float(x.mean()),'slope':b,'r2':r2,'slope_ci95':[float(b-confidence*se_b),float(b+confidence*se_b)],'rmse':rmse,'last_two_holdout_rmse':holdout,'n':len(x),'min_r2_gate':gate},trend={'age':x.tolist(),'indicator':y.tolist(),'line_age':line_x.tolist(),'line_indicator':fitted.tolist(),'limit':limit,'baseline':baseline},history=hist,formulas=[f'Indicator(age) = c + b×(age−mean_age) = {y.mean():.9g} + {b:.9g}×(age−{x.mean():.9g})',f'Threshold age = mean_age + (limit−c)/b = {x.mean():.9g} + ({limit:g}−{y.mean():.9g})/{b:.9g}' if b>0 else 'Threshold crossing is undefined for nonpositive slope.',f'Remaining = max(0, threshold age − {current:g}); measured limit already reached → 0',f'R² = 1 − SSE/SST = {r2:.9g}; screening gate = {gate:g}', 'Crossing CI: gradient g=[−1/b, −(limit−c)/b²]; SE=sqrt(gᵀ Cov(c,b) g), centered c=indicator at mean age; crossing ± t(0.975,n−2)×SE.'],limitations=limitations)
