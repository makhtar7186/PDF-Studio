import streamlit as st


def setup_page() -> None:
    st.set_page_config(
        page_title="PDF Studio",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_css() -> None:
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
*,*::before,*::after{box-sizing:border-box}
#MainMenu,footer,header{visibility:hidden}
.stDeployButton{display:none}
:root{
  --bg:#09090f;--surface:#111118;--surface2:#17171f;--border:#252533;
  --accent:#6c63ff;--accent2:#ff6584;--accent3:#43e97b;--accent4:#f7b731;
  --text:#e4e4f0;--muted:#6a6a90;--radius:14px;
}
html,body,.stApp{background:var(--bg)!important;font-family:'DM Sans',sans-serif;color:var(--text)}
.main .block-container{max-width:1140px;padding:1.5rem 2rem 5rem}
.hero{text-align:center;padding:2.5rem 1rem 1.5rem;position:relative}
.hero::before{content:'';position:absolute;top:-40px;left:50%;transform:translateX(-50%);width:700px;height:260px;background:radial-gradient(ellipse,rgba(108,99,255,.16) 0%,rgba(255,101,132,.07) 55%,transparent 70%);pointer-events:none}
.hero h1{font-family:'Syne',sans-serif;font-size:clamp(2.2rem,5vw,3.4rem);font-weight:800;letter-spacing:-.03em;margin:0 0 .4rem;background:linear-gradient(135deg,#fff 25%,#6c63ff 65%,#ff6584);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero p{color:var(--muted);font-size:1rem;font-weight:300;margin:0}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem 1.75rem;margin-bottom:1.1rem;transition:border-color .2s}
.card:hover{border-color:rgba(108,99,255,.35)}
.card-title{font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;margin-bottom:.3rem;color:var(--text);display:flex;align-items:center;gap:.45rem}
.card-sub{color:var(--muted);font-size:.82rem;margin-bottom:1rem}
.stat-row{display:flex;gap:.6rem;flex-wrap:wrap;margin:.6rem 0}
.stat-chip{background:var(--surface2);border:1px solid var(--border);border-radius:7px;padding:.3rem .75rem;font-size:.78rem;color:var(--muted)}
.stat-chip span{color:var(--text);font-weight:500}
.file-item{display:flex;align-items:center;gap:.65rem;background:var(--surface2);border:1px solid var(--border);border-radius:9px;padding:.6rem .9rem;margin:.35rem 0;font-size:.85rem}
.file-icon{width:30px;height:30px;background:linear-gradient(135deg,var(--accent),var(--accent2));border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;color:#fff;flex-shrink:0}
.file-name{flex:1;color:var(--text)}
.file-size{color:var(--muted);font-size:.75rem}
.result-banner{background:linear-gradient(135deg,rgba(67,233,123,.1) 0%,rgba(108,99,255,.07) 100%);border:1px solid rgba(67,233,123,.3);border-radius:var(--radius);padding:1.2rem 1.6rem;margin:1rem 0;text-align:center}
.result-banner .big-num{font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;color:var(--accent3);display:block}
.result-banner .label{color:var(--muted);font-size:.85rem}
.progress-wrap{background:var(--surface2);border-radius:99px;height:5px;overflow:hidden;margin:.4rem 0}
.progress-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .4s}
.section-label{font-family:'Syne',sans-serif;font-weight:700;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:.9rem 0 .4rem}
.stFileUploader>div{background:var(--surface2)!important;border:2px dashed var(--border)!important;border-radius:var(--radius)!important}
.stFileUploader>div:hover{border-color:var(--accent)!important}
[data-testid="stFileUploadDropzone"]{background:transparent!important}
.stFileUploader label,.stFileUploader p,.stFileUploader span,.stFileUploader small{color:var(--muted)!important}
.stButton>button{background:linear-gradient(135deg,var(--accent) 0%,#8b82ff 100%)!important;color:#fff!important;border:none!important;border-radius:9px!important;font-family:'Syne',sans-serif!important;font-weight:600!important;font-size:.88rem!important;padding:.6rem 1.6rem!important;box-shadow:0 4px 18px rgba(108,99,255,.28)!important;transition:all .2s!important;width:100%!important}
.stButton>button:hover{box-shadow:0 6px 24px rgba(108,99,255,.48)!important;transform:translateY(-1px)!important}
.stDownloadButton>button{background:linear-gradient(135deg,var(--accent3) 0%,#30c96a 100%)!important;color:#060f0a!important;border:none!important;border-radius:9px!important;font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:.88rem!important;padding:.6rem 1.6rem!important;box-shadow:0 4px 18px rgba(67,233,123,.28)!important;width:100%!important}
.stSelectbox>div>div{background:var(--surface2)!important;border-color:var(--border)!important;color:var(--text)!important;border-radius:9px!important}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:11px!important;padding:3px!important;gap:3px!important;border:1px solid var(--border)!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:'Syne',sans-serif!important;font-weight:600!important;border-radius:8px!important;border:none!important;font-size:.82rem!important}
.stTabs [aria-selected="true"]{background:var(--accent)!important;color:#fff!important}
.stTabs [data-baseweb="tab-panel"]{padding-top:1.4rem!important}
label,.stMarkdown p{color:var(--text)!important}
.stCheckbox span{color:var(--text)!important}
.stNumberInput input,.stTextInput input,.stTextArea textarea{background:var(--surface2)!important;border-color:var(--border)!important;color:var(--text)!important;border-radius:8px!important}
hr{border-color:var(--border)!important}
.stAlert{border-radius:9px!important}
.stMultiSelect [data-baseweb="tag"]{background:var(--accent)!important}
.stMultiSelect>div>div{background:var(--surface2)!important;border-color:var(--border)!important;border-radius:9px!important}
div[data-testid="stSlider"]>div>div>div{background:linear-gradient(90deg,var(--accent),var(--accent2))!important}
.viewer-wrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;margin-top:1.2rem}
.viewer-header{display:flex;align-items:center;justify-content:space-between;padding:.75rem 1.2rem;border-bottom:1px solid var(--border);background:var(--surface2)}
.viewer-title{font-family:'Syne',sans-serif;font-weight:700;font-size:.9rem;color:var(--text);display:flex;align-items:center;gap:.4rem}
.viewer-info{font-size:.78rem;color:var(--muted)}
.viewer-body{padding:1rem;display:flex;gap:1rem}
.thumb-panel{width:110px;flex-shrink:0;display:flex;flex-direction:column;gap:.4rem;max-height:520px;overflow-y:auto;padding-right:.3rem}
.thumb-panel::-webkit-scrollbar{width:4px}
.thumb-panel::-webkit-scrollbar-track{background:var(--surface2)}
.thumb-panel::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
.thumb-item{cursor:pointer;border-radius:6px;overflow:hidden;border:2px solid transparent;transition:border-color .15s;position:relative}
.thumb-item:hover{border-color:rgba(108,99,255,.5)}
.thumb-item.active{border-color:var(--accent)!important}
.thumb-item img{width:100%;display:block;border-radius:4px}
.thumb-num{position:absolute;bottom:2px;right:4px;font-size:.6rem;color:rgba(255,255,255,.7);font-family:'Syne',sans-serif;font-weight:700;background:rgba(0,0,0,.5);padding:1px 4px;border-radius:3px}
.main-view{flex:1;display:flex;align-items:center;justify-content:center;background:var(--bg);border-radius:10px;padding:1rem;min-height:400px}
.main-view img{max-width:100%;max-height:500px;border-radius:6px;box-shadow:0 8px 32px rgba(0,0,0,.5)}
.viewer-footer{display:flex;align-items:center;justify-content:center;gap:1rem;padding:.75rem 1.2rem;border-top:1px solid var(--border);background:var(--surface2)}
.page-badge{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:.25rem .75rem;font-family:'Syne',sans-serif;font-weight:700;font-size:.82rem;color:var(--text)}
.page-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:.6rem;margin-top:.8rem}
.page-grid-item{background:var(--surface2);border:1px solid var(--border);border-radius:8px;overflow:hidden;transition:border-color .15s}
.page-grid-item:hover{border-color:rgba(108,99,255,.4)}
.page-grid-item img{width:100%;display:block}
.page-grid-num{text-align:center;padding:.25rem;font-family:'Syne',sans-serif;font-size:.7rem;color:var(--muted)}
.meta-row{display:flex;align-items:baseline;gap:.5rem;padding:.4rem 0;border-bottom:1px solid var(--border)}
.meta-row:last-child{border-bottom:none}
.meta-key{font-size:.78rem;color:var(--muted);width:85px;flex-shrink:0}
.meta-val{font-size:.85rem;color:var(--text);word-break:break-all}
</style>
""", unsafe_allow_html=True)
