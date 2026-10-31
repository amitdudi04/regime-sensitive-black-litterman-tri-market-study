"""Publication rendering from auditable plot payloads, without estimation or resampling."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

from scripts.phase3_final_results import MARKETS, MODELS, main_wealth, asi_events, payload_hash

COLORS={"Black-Litterman":"#0072B2","Markowitz":"#D55E00","Equal-weight":"#009E73"}
LABELS={"Black-Litterman":"Black–Litterman","Markowitz":"Markowitz","Equal-weight":"Rebalanced 1/N"}
STYLES={"Black-Litterman":"-","Markowitz":"-","Equal-weight":"--"}


def figure_payloads(e,tables):
    p={}
    p["01_cumulative_wealth"]={"kind":"wealth","title":"Net cumulative wealth at 10 bps",
        "source":["results/generated/phase2/phase2_daily_returns.csv"],"phase":"Phase 2",
        "caption":"Compounded daily net simple returns; 100% target cap. NAV 1 immediately before the first OOS return is anchored at the first plotted date. Panel windows differ; BL and 1/N nearly overlap.",
        "panels":[{"market":m,"start":tables[1].set_index("Market").loc[m,"OOS Start"],
            "end":tables[1].set_index("Market").loc[m,"OOS End"],
            "series":[{"model":model,**main_wealth(e["daily"],m,model)} for model in MODELS]} for m in MARKETS]}
    events=asi_events(e["decisions"])
    rows=[]
    for m in MARKETS:
        for model in MODELS[:2]:
            group=events[events.Market.eq(m)&events.Model.eq(model)&events["Target Weight Cap"].eq(1)]
            rows.append({"market":m,"model":model,"value":float(group["ASI Event"].mean()),"annotation":f'{group["ASI Event"].mean():.4f}'})
    p["02_allocation_stability"]={"kind":"bars","title":"Target-allocation stability","ylabel":"Mean successive target L1 distance",
        "source":["results/generated/phase2/phase2_trading_decisions.csv"],"phase":"Phase 2","rows":rows,"models":list(MODELS[:2]),
        "caption":"ASI derived from actual consecutive 100%-cap rebalance target vectors; first undefined difference excluded. Values agree with Table 2 at displayed precision. Each market uses its own Table 1 OOS window; target ASI is not traded turnover."}
    p["03_trading_turnover"]={"kind":"bars","title":"Drift-adjusted trading turnover","ylabel":"Mean rebalance L1 turnover (%)",
        "source":["results/phase2_results/phase2_strategy_summary.csv"],"phase":"Phase 2","models":list(MODELS),"percent":True,
        "rows":[{"market":r.Market,"model":r.Model,"value":float(r["Mean Rebalance L1 Turnover"]),"annotation":f'{100*r["Mean Rebalance L1 Turnover"]:.2f}%'} for _,r in tables[2].iterrows()],
        "caption":"100%-cap primary strategies, common 63-session schedule within each market. L1 target minus drifted pretrade holdings. Initial cash deployment (L1=1) excluded from this mean and reported separately in Table 2. Market-specific windows are given in Table 1."}
    cap_panels=[]
    for m in MARKETS:
        block=tables[3][tables[3].Market.eq(m)]
        cap_panels.append({"market":m,"series":[{"model":model,"x":["100%","40%"],
            "y":[float(block[block.Model.eq(model)&block["Target Weight Cap"].eq(cap)]["Sharpe Ratio"].iloc[0]) for cap in (1,.4)]} for model in MODELS[:2]]})
    p["04_matched_concentration"]={"kind":"scenario","title":"Matched concentration bounds: net Sharpe at 10 bps","ylabel":"Zero-RF annualized Sharpe",
        "source":["results/phase2_results/phase2_concentration_sensitivity.csv"],"phase":"Phase 2","panels":cap_panels,
        "caption":"BL and Markowitz use the same maximum target bound at each point. The 40% constraint is imposed at rebalance, not continuously on drifting holdings. BL's constraint is inactive. Unequal market samples are listed in Table 1; each line is a same-market matched comparison."}
    cost_panels=[]
    for m in MARKETS:
        block=tables[4][tables[4].Market.eq(m)&tables[4]["Target Weight Cap"].eq(1)]
        cost_panels.append({"market":m,"series":[{"model":model,"x":[0,5,10,20],
            "y":[float(block[block.Model.eq(model)&block["Cost (bps per L1)"].eq(bps)]["Net Terminal Wealth"].iloc[0]) for bps in (0,5,10,20)]} for model in MODELS]})
    p["05_transaction_costs"]={"kind":"scenario","title":"Transaction costs and compounded terminal wealth","ylabel":"Terminal wealth (initial NAV = 1)",
        "source":["results/phase2_results/phase2_transaction_cost_sensitivity.csv"],"phase":"Phase 2","panels":cost_panels,"xlabel":"Cost (bps per unit L1 turnover)",
        "caption":"100%-cap principal strategies, all four predefined cost rates. Same gross path and trading decisions across rates. Terminal wealth is distinct from arithmetic annual return in Table 4. Each panel uses its own Table 1 OOS span and y scale; no cross-market common-horizon ranking is implied."}
    forest=[]
    for m in MARKETS:
        for cap,comparator in ((1.,"Markowitz"),(1.,"Equal-weight"),(.4,"Markowitz")):
            r=tables[5][tables[5].Market.eq(m)&tables[5]["Target Weight Cap"].eq(cap)&tables[5]["Strategy B"].eq(comparator)].iloc[0]
            forest.append({"label":f'{m} · BL − {"1/N" if comparator=="Equal-weight" else "MV"} · cap {cap:.0%}',
                "model":comparator,"value":float(r["Sharpe Difference A minus B"]),"lower":float(r["95% CI Lower"]),"upper":float(r["95% CI Upper"]),
                "annotation":f'p = {r["Two-sided P-value"]:.4f}'})
    p["06_statistical_uncertainty"]={"kind":"forest","title":"Paired Sharpe differences and 95% uncertainty","source":["results/phase2_results/phase2_statistical_comparisons.csv"],
        "phase":"Phase 2","rows":forest,"caption":"Net 10 bps. Paired 20-session circular blocks, 2,000 iterations, seed 42; percentile 95% intervals, approximate empirical-mean-centered two-sided p-values, unadjusted. Windows/paired counts are those in Tables 1/5. All intervals include zero. Duplicate inactive-cap BL/1N rows are omitted; they remain in Table 5."}
    factor=tables[7][tables[7].Term.ne("Alpha")]
    p["08_us_factor_exposures"]={"kind":"factors","title":"US four-factor exposures — Phase 1 supplementary",
        "source":["docs/phase1/factor_regression_us.csv"],"phase":"Phase 1","terms":["MKT","SMB","HML","MOM"],
        "rows":[{"term":r.Term,"model":r.Model,"value":float(r.Coefficient),"annotation":f'{r.Coefficient:.4f}'} for _,r in factor.iterrows()],
        "caption":"OLS betas for Phase 1 US net strategies, 2011-01-04–2024-12-31 (3,521 sessions). HAC/Newey–West t statistics and p-values with maxlags 5 are in Table 7. Not a refit of Phase 2 capped/1N paths and not evidence of China/India factor exposure."}
    tau=tables[8].sort_values("Tau")
    p["09_us_tau_sensitivity"]={"kind":"tau","title":"US fixed-tau sensitivity — Phase 1 supplementary",
        "source":["docs/phase1/tau_sensitivity.csv"],"phase":"Phase 1","x":tau.Tau.tolist(),"y":tau["Sharpe Ratio"].tolist(),
        "annotations":[f'{v:.6f}' for v in tau["Sharpe Ratio"]],
        "caption":"Five verified fixed-tau US runs, 2011-01-04–2024-12-31 (3,521 sessions), net 10 bps. Omega independent of tau. Each point is the source value; no refit/tuning in Phase 3. These are not the adaptive-main-strategy return series."}
    return p


def render_figures(payloads, out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.titlesize":10,
        "axes.labelsize":9,"axes.spines.top":False,"axes.spines.right":False,"svg.fonttype":"none",
        "figure.facecolor":"white","savefig.facecolor":"white","axes.grid":True,"grid.alpha":.18,
        "axes.axisbelow":True,"svg.hashsalt":"phase3-final"})
    records={}
    for name,p in payloads.items():
        annotations=[]
        kind=p["kind"]
        if kind in ("wealth","scenario"):
            fig,axes=plt.subplots(1,3,figsize=(10.6,3.5))
            for ax,panel in zip(axes,p["panels"]):
                for series in panel["series"]:
                    model=series["model"]
                    if kind=="wealth":
                        x=pd.to_datetime(series["dates"]); y=series["wealth"]
                    else: x=series["x"]; y=series["y"]
                    ax.plot(x,y,label=LABELS[model],color=COLORS[model],linestyle=STYLES[model],linewidth=1.55,
                            marker="o" if kind=="scenario" else None,markersize=4)
                ax.set_title(panel["market"]+(f'\n{panel["start"]} – {panel["end"]}' if kind=="wealth" else ""))
                if kind=="wealth":
                    ax.tick_params(axis="x",labelrotation=35,labelsize=8)
                    ax.set_ylabel("Wealth (initial NAV = 1)")
                else:
                    ax.set_xticks(series["x"])
                    ax.set_xlabel(p.get("xlabel","Maximum rebalance target weight"))
                    ax.set_ylabel(p["ylabel"])
            handles,labels=axes[0].get_legend_handles_labels()
            fig.legend(handles,labels,loc="lower center",ncol=3,frameon=False,bbox_to_anchor=(.5,0))
            fig.suptitle(p["title"],fontsize=12,y=.99)
            fig.tight_layout(rect=(0,.13,1,.91))
        elif kind in ("bars","factors"):
            fig,ax=plt.subplots(figsize=(7.3,3.8))
            groups=list(MARKETS) if kind=="bars" else p["terms"]
            models=p.get("models",list(MODELS[:2])); width=.75/len(models)
            for k,model in enumerate(models):
                rows=[next(r for r in p["rows"] if r["model"]==model and r["market" if kind=="bars" else "term"]==group) for group in groups]
                positions=np.arange(len(groups))+(k-(len(models)-1)/2)*width
                ax.bar(positions,[r["value"] for r in rows],width=width*.92,label=LABELS[model],color=COLORS[model])
                for x,r in zip(positions,rows):
                    ax.annotate(r["annotation"],(x,r["value"]),xytext=(0,5 if r["value"]>=0 else -11),
                        textcoords="offset points",ha="center",fontsize=8)
                    annotations.append(r["annotation"])
            ax.set_xticks(np.arange(len(groups)),groups)
            ax.set_ylabel(p.get("ylabel","OLS factor beta (dimensionless)"))
            if p.get("percent"): ax.yaxis.set_major_formatter(PercentFormatter(1))
            if kind=="factors": ax.axhline(0,color="#555555",linewidth=.7)
            ax.margins(y=.25)
            ax.set_title(p["title"],pad=12)
            ax.legend(frameon=False,loc="upper center",bbox_to_anchor=(.5,-.1),ncol=3)
            fig.tight_layout()
        elif kind=="forest":
            fig,ax=plt.subplots(figsize=(9,5.3))
            for i,r in enumerate(p["rows"]):
                ax.hlines(i,r["lower"],r["upper"],color=COLORS[r["model"]],linewidth=1.6)
                ax.plot(r["value"],i,"o",color=COLORS[r["model"]],markersize=4)
                ax.annotate(r["annotation"],xy=(1.02,i),xycoords=("axes fraction","data"),fontsize=8,va="center")
                annotations.append(r["annotation"])
            ax.set_yticks(np.arange(len(p["rows"])),[r["label"] for r in p["rows"]])
            ax.invert_yaxis(); ax.axvline(0,color="#555555",linestyle="--",linewidth=.9)
            ax.set_xlabel("Annualized Sharpe difference (BL minus comparator)"); ax.set_title(p["title"],pad=12)
            fig.tight_layout(rect=(0,0,.89,1))
        else:
            fig,ax=plt.subplots(figsize=(7.3,3.8))
            ax.plot(p["x"],p["y"],"o-",color=COLORS["Black-Litterman"],linewidth=1.5)
            for x,y,label in zip(p["x"],p["y"],p["annotations"]):
                ax.annotate(label,(x,y),xytext=(0,8),textcoords="offset points",ha="center",fontsize=8)
                annotations.append(label)
            ax.set_xticks(p["x"]); ax.set_xlabel("Fixed tau"); ax.set_ylabel("US net annualized Sharpe (RF = 0)")
            ax.set_title(p["title"],pad=12); ax.margins(x=.08,y=.22); fig.tight_layout()
        paths=[]
        for suffix in ("png","svg"):
            path=out/f"{name}.{suffix}"
            fig.savefig(path,dpi=300,bbox_inches="tight",metadata={"Date":None} if suffix=="svg" else {})
            paths.append(path.name)
        plt.close(fig)
        records[name]={"files":paths,"payload_sha256":payload_hash(p),"source_files":p["source"],
                       "phase":p["phase"],"caption":p["caption"],"annotations":annotations}
    return records


def verify_figure_annotations(path, annotations):
    tree=ET.parse(path)
    text=" ".join("".join(n.itertext()) for n in tree.getroot().iter() if n.tag.endswith("text"))
    for label in annotations:
        if label not in text: raise ValueError(f"Figure annotation does not match generated table/payload: {label}")


def expected_annotations(payload):
    if payload.get("kind") in ("bars","factors"):
        models=payload.get("models",list(MODELS[:2]))
        groups=list(MARKETS) if payload["kind"]=="bars" else payload["terms"]
        key="market" if payload["kind"]=="bars" else "term"
        return [next(r["annotation"] for r in payload["rows"] if r["model"]==model and r[key]==group) for model in models for group in groups]
    if payload.get("kind")=="forest": return [r["annotation"] for r in payload["rows"]]
    return payload.get("annotations",[])
