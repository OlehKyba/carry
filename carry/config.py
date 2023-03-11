from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="CARRY",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True,
)
