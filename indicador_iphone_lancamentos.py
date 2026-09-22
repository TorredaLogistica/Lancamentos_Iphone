from pathlib import Path
import base64, io, mimetypes, unicodedata
import pandas as pd
import plotly.express as px
import streamlit as st
from itertools import count

st.set_page_config(page_title='Lançamentos iPhone', page_icon='📱', layout='wide', initial_sidebar_state='expanded')
RED='#E30613'; WINE='#960018'; GRAY='#5B5B5B'; LIGHT='#FFF4F5'; GRID='#ECECEC'; BLUE17='#626A73'
ROOT=Path(__file__).resolve().parent

st.markdown('''<style>
.block-container{padding:3.8rem 1rem 2rem;max-width:1650px}header[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer{visibility:hidden;height:0}
[data-testid="stSidebar"]{background:#fafafa;border-right:1px solid #eee}.hero{display:grid;grid-template-columns:150px 1fr 100px;align-items:center;gap:18px;margin:8px 0 18px}.hero img{max-height:64px;max-width:140px;object-fit:contain}.hero .apple{justify-self:end}.hero h1{text-align:center;font-size:clamp(22px,2.1vw,36px);margin:0;color:#252525}.kpi{min-height:104px;border:1px solid #444;border-radius:12px;background:linear-gradient(145deg,#fff 50%,#f1d9dc);box-shadow:0 2px 7px #0001,inset 0 0 12px #eadadd;padding:12px 7px;display:flex;flex-direction:column;justify-content:center;text-align:center;margin-bottom:8px}.kpi-num{font-size:clamp(26px,2.8vw,48px);line-height:1}.kpi-lbl{font-size:14px;color:#666;margin-top:10px}.section-title{font-weight:800;font-size:18px;color:#333;border-left:5px solid #E30613;padding-left:8px;margin-top:5px}
.stTabs{margin:14px 0 20px!important;overflow:visible!important}
.stTabs>div{overflow:visible!important}
.stTabs div[data-baseweb="tab-list"]{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:12px!important;width:100%!important;height:auto!important;overflow:visible!important;padding:8px 0 14px!important;border:0!important;background:transparent!important}
.stTabs div[data-baseweb="tab-list"]>button{display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;max-width:none!important;min-width:0!important;min-height:58px!important;height:auto!important;margin:0!important;padding:12px 14px!important;border:1px solid #D7D7D7!important;border-radius:12px!important;background:#FFFFFF!important;color:#333333!important;box-shadow:0 2px 8px rgba(0,0,0,.10)!important;transition:all .18s ease!important;overflow:visible!important;cursor:pointer!important}
.stTabs div[data-baseweb="tab-list"]>button:hover{border-color:#E30613!important;background:#FFF3F4!important;color:#B40010!important;transform:translateY(-1px)!important;box-shadow:0 5px 14px rgba(227,6,19,.18)!important}
.stTabs div[data-baseweb="tab-list"]>button[aria-selected="true"]{background:linear-gradient(135deg,#E30613 0%,#B40010 100%)!important;border-color:#E30613!important;color:#FFFFFF!important;box-shadow:0 6px 16px rgba(227,6,19,.30)!important}
.stTabs div[data-baseweb="tab-list"]>button p,.stTabs div[data-baseweb="tab-list"]>button span{margin:0!important;font-size:clamp(13px,1.05vw,16px)!important;line-height:1.25!important;white-space:normal!important;overflow:visible!important;text-overflow:clip!important;text-align:center!important;font-weight:750!important;color:inherit!important}
.stTabs div[data-baseweb="tab-list"] [data-baseweb="tab-highlight"],.stTabs div[data-baseweb="tab-list"] [data-baseweb="tab-border"]{display:none!important}
div[role="radiogroup"]{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:2px 0 10px}div[role="radiogroup"] label{border:1px solid #d3d3d3;border-radius:10px;padding:12px 10px;background:#fff;justify-content:center}div[role="radiogroup"] label:has(input:checked){border-color:#E30613;background:#FFF1F2;box-shadow:0 2px 7px #E3061322}div[role="radiogroup"] label p{font-weight:750;text-align:center}@media(max-width:700px){div[role="radiogroup"]{grid-template-columns:1fr}}
@media(max-width:900px){.stTabs div[data-baseweb="tab-list"]{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}.hero{grid-template-columns:90px 1fr 70px}.hero img{max-width:85px;max-height:48px}}
@media(max-width:650px){.block-container{padding:2.6rem .45rem 1rem}.hero{grid-template-columns:55px 1fr 45px;gap:5px}.hero img{max-width:52px;max-height:38px}.hero h1{font-size:19px}.kpi{min-height:80px}.kpi-num{font-size:26px}.kpi-lbl{font-size:12px}.stTabs div[data-baseweb="tab-list"]{grid-template-columns:1fr!important;gap:7px!important}.stTabs div[data-baseweb="tab-list"]>button{min-height:50px!important;padding:10px 8px!important}.stTabs div[data-baseweb="tab-list"]>button p,.stTabs div[data-baseweb="tab-list"]>button span{font-size:12px!important}}
</style>''', unsafe_allow_html=True)

def norm(s): return unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower().strip()
def fmt(v,d=0): return f'{v:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.') if pd.notna(v) else '0'
def mm(v): return 'R$ '+fmt(float(v)/1_000_000,3)+' MM'
def file_uri(path):
    mime=mimetypes.guess_type(path.name)[0] or 'image/png'
    return f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode()
def find_logo(token):
    for p in ROOT.iterdir():
        if p.is_file() and token in norm(p.stem) and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}: return p
    return None
def hero(title):
    lc,la=find_logo('logo_claro'),find_logo('logo_apple')
    left=f'<img src="{file_uri(lc)}" alt="Claro">' if lc else '<b style="color:#E30613;font-size:28px">CLARO</b>'
    right=f'<img class="apple" src="{file_uri(la)}" alt="Apple">' if la else '<b class="apple">Apple</b>'
    st.markdown(f'<div class="hero"><div>{left}</div><h1>{title}</h1>{right}</div>',unsafe_allow_html=True)
def kpi(label,val): st.markdown(f'<div class="kpi"><div class="kpi-num">{val}</div><div class="kpi-lbl">{label}</div></div>',unsafe_allow_html=True)
def _short(v,limit=22):
    t=str(v)
    return t if len(t)<=limit else t[:limit-1]+'…'
def style(fig,h=390,legend=False,ncats=8):
    height=max(h,390 + max(0,ncats-8)*8)
    fig.update_layout(height=height,margin=dict(l=32,r=32,t=92 if legend else 60,b=115),paper_bgcolor='white',plot_bgcolor='white',font=dict(family='Arial',color='#333',size=14),showlegend=legend,legend=dict(orientation='h',y=1.22,x=0,title=None,font=dict(size=13)),hoverlabel=dict(bgcolor='white',font_size=13),uniformtext_minsize=11,uniformtext_mode='show',bargap=.18,bargroupgap=.05)
    fig.update_xaxes(title=None,showgrid=False,automargin=True,tickangle=-28,tickfont=dict(size=13),constrain='domain')
    fig.update_yaxes(title=None,visible=False,gridcolor=GRID,rangemode='tozero',automargin=True,range=[0,None])
    return fig
_chart_ids=count(1)
def chart(title,fig):
    st.markdown(f'<div class="section-title">{title}</div>',unsafe_allow_html=True)
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False,'responsive':True},key=f'plotly_{next(_chart_ids)}')
def bar(df,x,y,color=RED,text=None,percent=False,money=False):
    plot=df.sort_values(y,ascending=False).copy(); order=plot[x].astype(str).tolist()
    plot['_eixo']=plot[x].map(_short)
    plot['_texto']=plot[y].map(lambda v:('R$ '+fmt(float(v)/1_000_000,2)+' MM') if money else ((fmt(v,1)+'%') if percent else fmt(v))) if text is None else plot[text]
    fig=px.bar(plot,x='_eixo',y=y,text='_texto',color_discrete_sequence=[color],category_orders={'_eixo':[_short(v) for v in order]},custom_data=[x,'_texto'])
    fig.update_traces(textposition='outside',cliponaxis=False,textfont_size=12,hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>')
    if percent: fig.update_yaxes(range=[0,118])
    return style(fig,ncats=plot['_eixo'].nunique())
def groupbar(df,x,y,series,order_by_total=True,percent=False,money=False):
    plot=df.copy(); order=plot.groupby(x)[y].sum().sort_values(ascending=False).index.astype(str).tolist() if order_by_total else plot[x].astype(str).drop_duplicates().tolist()
    plot['_eixo']=plot[x].map(_short)
    plot['_texto']=plot[y].map(lambda v:('R$ '+fmt(float(v)/1_000_000,2)+' MM') if money else ((fmt(v,1)+'%') if percent else fmt(v)))
    cmap={'Lançamento iPhone 18':RED,'Lançamento iPhone 17':BLUE17,'Agente Autorizado':RED,'Loja Propria':WINE,'Status Expedição':RED,'Status Faturamento':WINE,'Atrasado':RED,'Prazo OK':'#FFC857'}
    fig=px.bar(plot,x='_eixo',y=y,color=series,barmode='group',text='_texto',color_discrete_map=cmap,category_orders={'_eixo':[_short(v) for v in order],series:(['Lançamento iPhone 18','Lançamento iPhone 17'] if series=='Lançamento' else plot[series].astype(str).drop_duplicates().tolist())},custom_data=[x,'_texto'])
    fig.update_traces(textposition='outside',cliponaxis=False,textfont_size=12,hovertemplate='<b>%{customdata[0]}</b><br>%{fullData.name}: %{customdata[1]}<extra></extra>')
    if money:
        # Alterna a posição vertical dos textos das duas séries para reduzir sobreposição.
        for idx,tr in enumerate(fig.data):
            tr.textposition='outside'
            tr.textfont=dict(size=11)
            tr.texttemplate='%{text}'
            tr.offsetgroup=str(idx)
        fig.update_layout(bargap=.28,bargroupgap=.10)
    if percent: fig.update_yaxes(range=[0,118])
    fig.update_layout(margin=dict(l=40,r=40,t=115,b=120),legend=dict(orientation='h',y=1.18,x=0,traceorder='normal',font=dict(size=13)))
    return style(fig,455,True,plot['_eixo'].nunique())
@st.cache_data(show_spinner=False)
def load_book(path, launch):
    b=pd.ExcelFile(path,engine='openpyxl'); out={s:pd.read_excel(b,sheet_name=s) for s in b.sheet_names}
    for d in out.values(): d['Lançamento']=launch
    return out

def find_book(number):
    candidates=[]
    for p in ROOT.glob('*.xlsx'):
        n=norm(p.stem).replace(' ','')
        if f'iphone{number}' in n and not p.name.startswith('~$'): candidates.append(p)
    return sorted(candidates,key=lambda p:(len(p.name),p.name))[0] if candidates else None

p18=find_book('18');p17=find_book('17')
if not p18: st.error('Base do iPhone 18 não encontrada. Use um nome contendo “iPhone 18”.');st.stop()
books={'Lançamento iPhone 18':load_book(str(p18),'Lançamento iPhone 18')}
if p17: books['Lançamento iPhone 17']=load_book(str(p17),'Lançamento iPhone 17')
options=['Lançamento iPhone 18']+(['Lançamento iPhone 17','Comparativo entre os lançamentos'] if p17 else [])
# Seletor principal sempre visível na página, sem depender da barra lateral recolhida.
st.markdown('### Selecione o lançamento')
selected=st.radio(
    'Escolha a análise',
    options,
    index=0,
    horizontal=True,
    label_visibility='collapsed',
    key='seletor_lancamento'
)
if not p17:
    st.info('A base do iPhone 17 não foi identificada. Confirme se o arquivo .xlsx contém “iPhone 17” no nome e está na mesma pasta do .py.')
st.markdown('---')

def get(sheet):
    if selected=='Comparativo entre os lançamentos': return pd.concat([books[k][sheet] for k in ['Lançamento iPhone 18','Lançamento iPhone 17']],ignore_index=True)
    return books[selected][sheet].copy()
def title_text(base): return f'{base} - '+('Comparativo iPhone 18 x iPhone 17' if selected.startswith('Comparativo') else selected.replace('Lançamento ','').replace('iPhone','iPhone '))
def cards(values):
    cs=st.columns(len(values))
    for c,(l,v) in zip(cs,values):
        with c:kpi(l,v)
def comp_kpis(df, items):
    launches=['Lançamento iPhone 18','Lançamento iPhone 17']; cs=st.columns(len(items))
    for c,(label,func) in zip(cs,items):
        with c:
            v18=func(df[df.Lançamento==launches[0]]);v17=func(df[df.Lançamento==launches[1]])
            kpi(label,f'{fmt(v18)} | {fmt(v17)}');st.caption('iPhone 18 | iPhone 17')

tabs=st.tabs(['Recebimentos','Faturamento e Expedição','AAs e LPs','E-Commerce'])
with tabs[0]:
    d=get('Base_Recebimento'); hero(title_text('Recebimentos dos Agendamentos'))
    comp=selected.startswith('Comparativo')
    if comp:
        comp_kpis(d,[('Qtde de NFs',lambda x:x['Nº da NF'].nunique()),('Qtde de Aparelhos',lambda x:pd.to_numeric(x['Quantidade'],errors='coerce').sum())])
        cs=st.columns(2)
        for c,(lab,fn,is_money) in zip(cs,[('Valor Total das NFs',lambda x:pd.to_numeric(x['Valor'],errors='coerce').sum(),True),('CDs atendidos',lambda x:x['CD_Corrigido'].nunique(),False)]):
            with c:
                a=fn(d[d.Lançamento=='Lançamento iPhone 18']);b=fn(d[d.Lançamento=='Lançamento iPhone 17']);kpi(lab,(f'{mm(a)} | {mm(b)}' if is_money else f'{fmt(a)} | {fmt(b)}'));st.caption('iPhone 18 | iPhone 17')
    else: cards([('Qtde de NFs',fmt(d['Nº da NF'].nunique())),('Qtde de Aparelhos',fmt(pd.to_numeric(d['Quantidade'],errors='coerce').sum())),('Valor Total das NFs',mm(pd.to_numeric(d['Valor'],errors='coerce').sum()))])
    keys=lambda col:[col,'Lançamento'] if comp else [col]
    g=d.groupby(keys('CD_Corrigido'))['Quantidade'].sum().reset_index(name='Aparelhos')
    n=d.groupby(keys('CD_Corrigido'))['Nº da NF'].nunique().reset_index(name='NFs')
    v=d.groupby(keys('CD_Corrigido'))['Valor'].sum().reset_index(name='Valor')
    stat=d.assign(StatusPrazo=d['St. entrega'].map(lambda z:'Atrasado' if 'atras' in norm(z) else 'Prazo OK')).groupby(keys('CD_Corrigido')+['StatusPrazo'])['Quantidade'].sum().reset_index(name='Aparelhos')
    if comp: stat['Serie']=stat['Lançamento']
    else: stat['Serie']=stat['StatusPrazo']
    a,b=st.columns(2)
    with a:chart('Qtde de Aparelhos',groupbar(g,'CD_Corrigido','Aparelhos','Lançamento') if comp else bar(g,'CD_Corrigido','Aparelhos'))
    with b:chart('Qtde de NFs',groupbar(n,'CD_Corrigido','NFs','Lançamento') if comp else bar(n,'CD_Corrigido','NFs'))
    a,b=st.columns(2)
    with a:chart('Valor Total das NFs',groupbar(v,'CD_Corrigido','Valor','Lançamento',money=True) if comp else bar(v,'CD_Corrigido','Valor',money=True))
    with b:chart('Execução dos Horários dos Agendamentos',groupbar(stat,'CD_Corrigido','Aparelhos','Serie'))
with tabs[1]:
    d=get('Consulta Massiva');hero(title_text('Faturamento e Expedição'))
    funcs=[('Qtde de NFs',lambda x:x['N° NF'].notna().sum()),('SLA D+0',lambda x:pd.to_numeric(x['Dias Fat + Exp'],errors='coerce').eq(0).sum()),('SLA D+1',lambda x:pd.to_numeric(x['Dias Fat + Exp'],errors='coerce').eq(1).sum()),('SLA D+2',lambda x:pd.to_numeric(x['Dias Fat + Exp'],errors='coerce').eq(2).sum()),('SLA D+3',lambda x:pd.to_numeric(x['Dias Fat + Exp'],errors='coerce').eq(3).sum()),('Não finalizado',lambda x:pd.to_numeric(x['Dias Fat + Exp'],errors='coerce').isna().sum())]
    if selected.startswith('Comparativo'): comp_kpis(d,funcs)
    else: cards([(l,fmt(f(d))) for l,f in funcs])
    dims=[('Qtde de OVs por CDs','CD Origem'),('Qtde de OVs por Região','Região Destino'),('Qtde de OVs por Transportadoras','Transportadora')]
    a,b=st.columns(2)
    containers=[a,b]
    for i,(lab,col) in enumerate(dims):
        g=d.dropna(subset=[col]).groupby(([col,'Lançamento'] if selected.startswith('Comparativo') else [col]))['Pedido'].nunique().reset_index(name='OVs')
        target=containers[i%2]
        with target: chart(lab,groupbar(g,col,'OVs','Lançamento') if selected.startswith('Comparativo') else bar(g,col,'OVs'))
    status=[]
    for col in ['Status Expedição','Status Faturamento']:
        z=d.assign(ok=d[col].map(lambda v:1 if norm(v)=='no prazo' else 0)).groupby((['CD Origem','Lançamento'] if selected.startswith('Comparativo') else ['CD Origem']))['ok'].mean().mul(100).reset_index(name='Percentual');z['Indicador']=col;status.append(z)
    z=pd.concat(status,ignore_index=True)
    if selected.startswith('Comparativo'):
        z=z.groupby(['CD Origem','Lançamento'],as_index=False)['Percentual'].mean();series='Lançamento'
    else: series='Indicador'
    chart('Status dos Faturamentos no Prazo',groupbar(z,'CD Origem','Percentual',series,percent=True))
with tabs[2]:
    d=get('Concluidas');hero(title_text('Faturamento AAs e LPs'))
    if selected.startswith('Comparativo'):
        comp_kpis(d,[('Qtde de NFs',lambda x:x['Documento SD'].nunique()),('Qtde de Aparelhos',lambda x:pd.to_numeric(x['Quantidade da ordem'],errors='coerce').sum()),('Qtde de PDVs',lambda x:x['Cód.Client'].nunique()),('Qtde de Clientes',lambda x:x['Cliente'].nunique())])
    else:
        ss=d.groupby('Segmento').agg(NFs=('Documento SD','nunique'),Aparelhos=('Quantidade da ordem','sum'),PDVs=('Cód.Client','nunique'),Cidades=('GrpClients','nunique'))
        cards([('Qtde de NFs',fmt(d['Documento SD'].nunique())),('Qtde de Aparelhos',fmt(d['Quantidade da ordem'].sum())),('Qtde de PDVs',fmt(d['Cód.Client'].nunique())),('Qtde de Clientes',fmt(d['Cliente'].nunique()))])
        for seg,short in [('Agente Autorizado','AA'),('Loja Propria','LP')]: cards([(f'Qtde de NFs - {short}',fmt(ss.loc[seg,'NFs'])),(f'Aparelhos {short}',fmt(ss.loc[seg,'Aparelhos'])),(f'Qtde de {short}',fmt(ss.loc[seg,'PDVs'])),(f'Qtde de Cidades - {short}',fmt(ss.loc[seg,'Cidades']))])
    series='Lançamento' if selected.startswith('Comparativo') else 'Segmento'
    groups=[('Qtde de Aparelhos por CD','Região','Quantidade da ordem'),('Qtde de PDVs','Região','Cód.Client')]
    a,b=st.columns(2)
    for box,(lab,col,val) in zip([a,b],groups):
        keys=[col,series];g=d.groupby(keys)[val].sum().reset_index(name='Valor') if val=='Quantidade da ordem' else d.groupby(keys)[val].nunique().reset_index(name='Valor')
        with box:chart(lab,groupbar(g,col,'Valor',series))
    d['_data']=pd.to_datetime(d['Data do documento'],errors='coerce').dt.strftime('%d/%m');g=d.groupby(['_data',series])['Quantidade da ordem'].sum().reset_index(name='Aparelhos')
    # Total de aparelhos por CD, sem quebra entre Agente Autorizado e Loja Própria.
    if selected.startswith('Comparativo'):
        aparelhos_cd=d.groupby(['Região','Lançamento'])['Quantidade da ordem'].sum().reset_index(name='Aparelhos')
    else:
        aparelhos_cd=d.groupby('Região')['Quantidade da ordem'].sum().reset_index(name='Aparelhos')
    a,b=st.columns(2)
    with a:chart('Qtde de Aparelhos por Data',groupbar(g,'_data','Aparelhos',series,False))
    with b:chart('Qtde de Aparelhos por CD',groupbar(aparelhos_cd,'Região','Aparelhos','Lançamento') if selected.startswith('Comparativo') else bar(aparelhos_cd,'Região','Aparelhos'))
with tabs[3]:
    d=get('Base Ecommerce');hero(title_text('Faturamentos E-Commerce'))
    funcs=[('Qtde de Pedidos',lambda x:x['Nº do pedido'].nunique()),('Qtde de Aparelhos',lambda x:pd.to_numeric(x['Quantidade da ordem'],errors='coerce').sum()),('Qtde de UFs',lambda x:x['Região'].nunique())]
    if selected.startswith('Comparativo'):comp_kpis(d,funcs)
    else:cards([(l,fmt(f(d))) for l,f in funcs])
    series='Lançamento' if selected.startswith('Comparativo') else None
    a,b=st.columns(2)
    g=d.groupby((['Região',series] if series else ['Região']))['Quantidade da ordem'].sum().reset_index(name='Aparelhos')
    with a:chart('Qtde de Aparelhos por UF',groupbar(g,'Região','Aparelhos',series) if series else bar(g,'Região','Aparelhos'))
    h=d.groupby((['Descrição',series] if series else ['Descrição']))['Nº do pedido'].nunique().reset_index(name='Pedidos')
    with b:chart('Status das Entregas',groupbar(h,'Descrição','Pedidos',series) if series else bar(h,'Descrição','Pedidos',WINE))
    d['_data']=pd.to_datetime(d['Data do documento'],errors='coerce').dt.strftime('%d/%m');q=d.groupby((['_data',series] if series else ['_data']))['Quantidade da ordem'].sum().reset_index(name='Aparelhos')
    # SLA do E-Commerce: coluna R da guia Base Ecommerce (Nº nota fiscal).
    sla_col='Nº nota fiscal' if 'Nº nota fiscal' in d.columns else d.columns[17]
    d['_sla']=pd.to_numeric(d[sla_col],errors='coerce')
    d_sla=d.dropna(subset=['_sla']).copy()
    d_sla['_sla']=d_sla['_sla'].astype(int).astype(str)
    sla_keys=['_sla',series] if series else ['_sla']
    sla=d_sla.groupby(sla_keys)['Nº do pedido'].nunique().reset_index(name='Pedidos')
    sla['_ordem']=pd.to_numeric(sla['_sla'],errors='coerce')
    sla=sla.sort_values('_ordem').drop(columns='_ordem')
    a,b=st.columns(2)
    with a:chart('Qtde de Aparelhos por Data do Pedido',groupbar(q,'_data','Aparelhos',series,False) if series else bar(q,'_data','Aparelhos'))
    with b:chart('SLA',groupbar(sla,'_sla','Pedidos',series,False) if series else bar(sla,'_sla','Pedidos'))
