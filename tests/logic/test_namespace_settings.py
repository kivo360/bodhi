import os

from bodhi_server.settings import NamespaceSettings


def test_namespace_envs_correct():
    os.environ["BODHI_USERNAME"] = "beep"
    os.environ["BODHI_STAKEHOLDER"] = "boop"
    os.environ["BODHI_PROJECT"] = "blurp"

    ns_settings = NamespaceSettings()
    assert ns_settings.username == "beep"
    assert ns_settings.stakeholder == "boop"
    assert ns_settings.project == "blurp"

    assert isinstance(ns_settings.dict(), dict)
