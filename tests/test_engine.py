from pathlib import Path
import pytest
from labcore.config import load_config
from engine import simulate,Experiment,public_arrivals

@pytest.fixture
def config(): return load_config(Path(__file__).resolve().parents[1])[0]

@pytest.mark.parametrize('capacity',[5,20,100])
def test_durable_delivery_accounting(config,capacity):
    result=simulate(dict(config,queueCapacity=capacity),True)
    assert result['lost']==0
    assert result['accepted']+result['rejected']==config['events']
    assert result['delivered_unique']==result['accepted']

def test_volatile_crash_loses_only_accepted_events(config):
    result=simulate(config,False)
    assert result['lost']>0
    assert result['lost']+result['delivered_unique']==result['accepted']
    assert set(result['lost_ids']).isdisjoint(result['delivery_ids'])

def test_simulation_repeatable(config):
    assert simulate(config)==simulate(config)

def test_invalid_fault_order_rejected(config):
    with pytest.raises(ValueError): Experiment.model_validate(dict(config,crashAt=50))

def test_arrival_curve_capacity(config):
    result=simulate(dict(config,queueCapacity=5),True,[5]*config['events'])
    assert result['rejected']>0
    assert result['lost']==0

def test_public_curve_is_rescaled_and_bounded(tmp_path):
    path=tmp_path/'data.csv'
    path.write_text('timestamp,value\na,1\nb,5\nc,9\n')
    assert public_arrivals(path,3)==[1,3,5]
