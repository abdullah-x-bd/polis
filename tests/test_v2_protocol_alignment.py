from polis.v2.protocol import load_protocol
from polis.v2.scenarios import HETEROGENEOUS_COMPOSITIONS


def test_heterogeneous_compositions_use_only_frozen_cheap_panel_models():
    protocol = load_protocol("configs/v2_protocol.json")
    cheap_ids = {item.id for item in protocol.cheap_models}
    composition_ids = {
        model
        for composition in HETEROGENEOUS_COMPOSITIONS
        for key, model in composition.items()
        if key.startswith("agent_")
    }
    assert composition_ids <= cheap_ids
    assert "deepseek/deepseek-v3.2" in composition_ids
    assert "deepseek/deepseek-v4-flash" not in composition_ids
