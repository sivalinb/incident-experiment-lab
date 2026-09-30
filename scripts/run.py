from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from labcore.config import load_config
from labcore.observability import Recorder
config,meta=load_config(ROOT)
parser=argparse.ArgumentParser()
parser.add_argument('--live',action='store_true')
recorder=Recorder(ROOT,ROOT.name)
with recorder.span('cli_run'):
    from engine import simulate,live
    args=parser.parse_args()
    report={'mode':'live HTTP queue / Apple Container' if args.live else 'deterministic simulation','runs':[live(ROOT,config,d) if args.live else simulate(config,d) for d in [False,True]]}
report['config_provenance']=meta
recorder.save(report)
(ROOT/'artifacts/cli-latest.json').write_text(json.dumps(report,indent=2,allow_nan=False))
print(json.dumps(report,indent=2,allow_nan=False))
if report.get('passed') is False: raise SystemExit(1)
