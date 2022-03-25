from bodhi_server import ModuleSettings


def test_password_exist():
    local_settings = ModuleSettings()
    assert local_settings.postgres.password


def test_username_is_starboy():
    local_settings = ModuleSettings()
    assert local_settings.postgres.user == "starboy"
