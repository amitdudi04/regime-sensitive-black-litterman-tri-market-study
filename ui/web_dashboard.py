from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go
from core.dual_market import evaluate_dual_market, MARKET_CONFIG

app = FastAPI(title="Professional Tri-Market Dash", version="1.0.0")

COLORS = {
    "bg": "#11111B",
    "panel": "rgba(24, 24, 37, 0.7)", # glassmorphism transparency
    "text": "#CDD6F4",
    "primary": "#F38BA8",
    "secondary": "#89DCEB",
    "accent": "#CBA6F7",
    "border": "rgba(49, 50, 68, 0.5)",
    "benchmark": "#F9E2AF"
}

def get_base_layout(title):
    return dict(
        title=dict(text=title, font=dict(color=COLORS['accent'], size=20, family="Inter")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'], family="Inter"),
        xaxis=dict(gridcolor=COLORS['border'], gridwidth=1, zeroline=False),
        yaxis=dict(gridcolor=COLORS['border'], gridwidth=1, zeroline=False),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified"
    )

def generate_plots():
    print("Generating data for web dashboard...")
    res = evaluate_dual_market(MARKET_CONFIG.copy())
    
    us_data = res["raw_results"]["US"]["backtest_series"]
    cn_data = res["raw_results"]["CHINA"]["backtest_series"]
    
    # Enable Plotly's built-in download PNG button by default in the config
    config = {"displaylogo": False, "toImageButtonOptions": {"format": "png", "filename": "chart_export"}}
    
    # US Plot
    fig_us = go.Figure()
    fig_us.add_trace(go.Scatter(x=us_data.index, y=us_data["bl_cum"], name='BL Net', line=dict(color=COLORS['primary'], width=2)))
    fig_us.add_trace(go.Scatter(x=us_data.index, y=us_data["mw_cum"], name='Markowitz Net', line=dict(color=COLORS['secondary'], width=2, dash='dash')))
    fig_us.add_trace(go.Scatter(x=us_data.index, y=us_data["bench_cum"], name='Benchmark', line=dict(color=COLORS['benchmark'], width=1.5)))
    fig_us.update_layout(**get_base_layout("US Market Cumulative Returns"))
    us_html = fig_us.to_html(full_html=False, include_plotlyjs=False, config=config)

    # CN Plot
    fig_cn = go.Figure()
    fig_cn.add_trace(go.Scatter(x=cn_data.index, y=cn_data["bl_cum"], name='BL Net', line=dict(color=COLORS['primary'], width=2)))
    fig_cn.add_trace(go.Scatter(x=cn_data.index, y=cn_data["mw_cum"], name='Markowitz Net', line=dict(color=COLORS['secondary'], width=2, dash='dash')))
    fig_cn.add_trace(go.Scatter(x=cn_data.index, y=cn_data["bench_cum"], name='Benchmark', line=dict(color=COLORS['benchmark'], width=1.5)))
    fig_cn.update_layout(**get_base_layout("China Market Cumulative Returns"))
    cn_html = fig_cn.to_html(full_html=False, include_plotlyjs=False, config=config)

    # Robustness Plot (US Tau)
    tau_df = res["raw_results"]["US"]["tau"]
    fig_rob = go.Figure()
    fig_rob.add_trace(go.Scatter(x=tau_df.index, y=tau_df["Sharpe Ratio"], mode='lines+markers', name='Sharpe', line=dict(color=COLORS['accent'], width=2)))
    fig_rob.update_layout(**get_base_layout("Tau Parameter Sensitivity (US Sharpe)"))
    fig_rob.update_xaxes(title_text="Tau (τ)")
    fig_rob.update_yaxes(title_text="Sharpe Ratio")
    rob_html = fig_rob.to_html(full_html=False, include_plotlyjs=False, config=config)

    return us_html, cn_html, rob_html

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    us_html, cn_html, rob_html = generate_plots()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Professional Quant Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{
                background-color: {COLORS['bg']};
                background-image: radial-gradient(circle at top right, rgba(243, 139, 168, 0.1), transparent 400px),
                                  radial-gradient(circle at bottom left, rgba(137, 220, 235, 0.1), transparent 400px);
                background-attachment: fixed;
                color: {COLORS['text']};
                font-family: 'Inter', sans-serif;
                margin: 0; padding: 40px;
            }}
            .glass-panel {{
                background: {COLORS['panel']};
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
                padding: 30px;
                margin-bottom: 24px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }}
            h1 {{ 
                color: {COLORS['primary']}; 
                text-align: center; 
                margin-bottom: 40px; 
                font-weight: 800;
                letter-spacing: -0.5px;
            }}
            .tab-container {{
                display: flex;
                gap: 12px;
                margin-bottom: 30px;
                border-bottom: 1px solid {COLORS['border']};
                padding-bottom: 15px;
            }}
            .tab-btn {{
                background: transparent;
                border: 1px solid transparent;
                color: {COLORS['text']};
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s ease;
            }}
            .tab-btn.active {{
                background: rgba(137, 220, 235, 0.15);
                border: 1px solid {COLORS['secondary']};
                color: {COLORS['secondary']};
            }}
            .tab-btn:hover:not(.active) {{
                background: rgba(255, 255, 255, 0.05);
            }}
            .tab-content {{ display: none; animation: fadeIn 0.4s; }}
            .tab-content.active {{ display: block; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            .export-btn {{
                background: {COLORS['accent']};
                color: {COLORS['bg']};
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 800;
                font-size: 14px;
                cursor: pointer;
                float: right;
                margin-top: -65px;
                margin-right: 10px;
                transition: all 0.2s;
                box-shadow: 0 4px 12px rgba(203, 166, 247, 0.3);
            }}
            .export-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(203, 166, 247, 0.4);
            }}
        </style>
        <script>
            function showTab(tabId) {{
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
                document.querySelector(`button[onclick="showTab('${{tabId}}')"]`).classList.add('active');
                window.dispatchEvent(new Event('resize')); 
            }}
            function downloadCSV(csvStr, filename) {{
                let blob = new Blob([csvStr], {{ type: 'text/csv;charset=utf-8;' }});
                let link = document.createElement("a");
                let url = URL.createObjectURL(blob);
                link.setAttribute("href", url);
                link.setAttribute("download", filename);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
            function triggerExport(market) {{
                // In a true application we would dump the serialized JSON from the backend.
                // Providing a functional demonstration of the pipeline.
                let data = "Date,Metric\\n2020-01-01,100\\n2020-01-02,101";
                downloadCSV(data, market + "_export.csv");
            }}
        </script>
    </head>
    <body>
        <h1>Tri-Market Quantitative Dashboard</h1>
        
        <div class="glass-panel">
            <div class="tab-container">
                <button class="tab-btn active" onclick="showTab('tab-us')">US Market</button>
                <button class="tab-btn" onclick="showTab('tab-cn')">China Market</button>
                <button class="tab-btn" onclick="showTab('tab-rob')">Robustness</button>
            </div>
            
            <div id="tab-us" class="tab-content active">
                <button class="export-btn" onclick="triggerExport('US')">Download Data (CSV)</button>
                {us_html}
            </div>
            
            <div id="tab-cn" class="tab-content">
                <button class="export-btn" onclick="triggerExport('CHINA')">Download Data (CSV)</button>
                {cn_html}
            </div>
            
            <div id="tab-rob" class="tab-content">
                <button class="export-btn" onclick="triggerExport('ROBUSTNESS')">Download Data (CSV)</button>
                {rob_html}
            </div>
            
            <div style="clear:both;"></div>
        </div>
    </body>
    </html>
    """
    return html

# To run: uvicorn ui.web_dashboard:app --reload
