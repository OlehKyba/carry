import jinja2

from carry.config import settings


_template_loader = jinja2.FileSystemLoader(searchpath=settings.templates_dir)
_env = jinja2.Environment(
    loader=_template_loader,
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=True,
)


def render_template(template_name: str, data: dict | None = None) -> str:
    if data is None:
        data = {}

    template = _env.get_template(template_name)
    rendered = template.render(**data).replace('<br/>', '\n')
    # rendered = rendered.replace("<br>", "\n")
    # rendered = re.sub(" +", " ", rendered).replace(" .", ".").replace(" ,", ",")
    # rendered = "\n".join(line.strip() for line in rendered.split("\n"))
    # rendered = rendered.replace("{FOURPACES}", "    ")
    return rendered
