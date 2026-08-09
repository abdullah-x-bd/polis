from polis.v1.actions import Action, ActionType
from polis.v1.agents import ScriptedAgent
from polis.v1.institutions import HardQuotaInstitution, NoCommonsInstitution
from polis.v1.loaders import load_resource_worlds
from polis.v1.resource_commons import ResourceCommonsEnvironment, oracle_welfare


def _agents(world, strategy="truthful"):
    return {
        spec.agent_id: ScriptedAgent(spec.agent_id, spec.agent_id, strategy=strategy, seed=i)
        for i, spec in enumerate(world.agents)
    }


class InvalidCommonsAgent:
    def act(self, observation):
        return Action(action=ActionType.REFUSE)


def test_v1_has_24_resource_worlds():
    worlds = load_resource_worlds("scenarios/resource_commons/v1.json")
    assert len(worlds) == 24
    assert {world.scarcity for world in worlds} == {"low", "medium", "high"}


def test_truthful_low_scarcity_completes_all_tasks():
    world = load_resource_worlds("scenarios/resource_commons/v1.json")[0]
    result = ResourceCommonsEnvironment(world, NoCommonsInstitution()).run(_agents(world), rounds=2)
    final = result.rounds[-1]
    assert all(row.completion == 1.0 for row in final.outcomes)
    assert final.overclaim_ratio == 0.0
    assert final.resource_waste == 0.0
    assert result.invalid_action_count == 0


def test_oracle_bounds_observed_welfare():
    world = load_resource_worlds("scenarios/resource_commons/v1.json")[-1]
    result = ResourceCommonsEnvironment(world, NoCommonsInstitution()).run(
        _agents(world, "max_requester"), rounds=2
    )
    assert result.rounds[-1].system_welfare <= oracle_welfare(world) + 1e-9


def test_hard_quota_caps_effective_requests():
    world = load_resource_worlds("scenarios/resource_commons/v1.json")[-1]
    result = ResourceCommonsEnvironment(world, HardQuotaInstitution(quota=25)).run(
        _agents(world, "max_requester"), rounds=1
    )
    assert all(row.effective_request <= 25 for row in result.rounds[0].outcomes)


def test_semantically_invalid_commons_action_becomes_zero_request():
    world = load_resource_worlds("scenarios/resource_commons/v1.json")[0]
    agents = _agents(world)
    first = world.agents[0].agent_id
    agents[first] = InvalidCommonsAgent()

    result = ResourceCommonsEnvironment(world, NoCommonsInstitution()).run(agents, rounds=1)
    outcome = next(row for row in result.rounds[0].outcomes if row.agent_id == first)

    assert outcome.requested == 0
    assert result.rounds[0].invalid_action_count == 1
    assert result.invalid_action_count == 1
