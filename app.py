from pathlib import Path
import pandas as pd
import streamlit as st
from labcore.config import load_config
from labcore.observability import Recorder
from labcore.ui import header,evidence,sources_panel,ai_panel,docs_panel
from engine import simulate,live,public_arrivals

ROOT=Path(__file__).resolve().parent
config,meta=load_config(ROOT)
header("Incident Experiment Lab","Inject a failure. Account for every accepted event. Compare recovery.",meta)

@st.cache_resource
def recorder(): return Recorder(ROOT,"incident-experiment-lab")

tabs=st.tabs(["Experiment","Evidence","AI reviewer","Public sources","Guide"])
with tabs[0]:
    mode=st.radio("Execution mode",["Deterministic simulation","Live Apple Container"],horizontal=True)
    config["queueCapacity"]=st.slider("Queue capacity",5,200,config["queueCapacity"])
    config["drainPerTick"]=st.slider("Simulation drain per tick",1,10,config["drainPerTick"])
    use_public=st.checkbox("Use downloaded NAB values as the simulation arrival profile")
    st.caption("A public time series is rescaled into a workload; it is not evidence of the injected incident.")
    if st.button("Compare volatile and durable queues",type="primary"):
        try:
            arrivals=None
            if use_public:
                if mode!="Deterministic simulation": raise ValueError("Public arrival profiles currently apply to simulation only")
                source=st.session_state.get("source_result")
                if not source or source["id"] not in {"nab-taxi","nab-cpu"}: raise ValueError("Fetch a NAB source in Public sources first")
                arrivals=public_arrivals(source["local_path"],config["events"])
            with recorder().span("recovery_compare",mode=mode):
                runs=[simulate(config,d,arrivals) if mode=="Deterministic simulation" else live(ROOT,config,d) for d in [False,True]]
                report={"mode":mode,"runs":runs,"config_provenance":meta}
                recorder().save(report)
                st.session_state["report"]=report
        except Exception as e: st.error(str(e))
    if "report" in st.session_state:
        runs=st.session_state["report"]["runs"]
        st.dataframe([{k:r[k] for k in ["policy","accepted","rejected","delivered_unique","lost","duplicates","recovery_ratio"]} for r in runs],hide_index=True)
        frame=pd.concat([pd.DataFrame(r["timeline"]).assign(policy=r["policy"]) for r in runs])
        st.line_chart(frame.pivot(index="tick",columns="policy",values="queue_depth"))
        st.caption("Simulation: queue depth. Live HTTP mode: accepted minus delivered, which also includes records lost at crash.")
with tabs[1]: evidence(st.session_state.get("report"))
with tabs[2]: ai_panel(ROOT,st.session_state.get("report"))
with tabs[3]: sources_panel(ROOT)
with tabs[4]: docs_panel(ROOT)
