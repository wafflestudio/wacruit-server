from sqladmin import Admin
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.templating import pass_context


class HttpsAdmin(Admin):
    @staticmethod
    @pass_context
    def https_url_for(context: dict, name: str, **path_params) -> str:
        request: Request = context["request"]
        url = request.url_for(name, **path_params)
        return url.components.geturl().replace("http://", "https://")

    def init_templating_engine(self) -> Jinja2Templates:
        templates = super().init_templating_engine()
        templates.env.globals["url_for"] = self.https_url_for
        return templates
