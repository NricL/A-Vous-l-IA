from pathlib import PurePosixPath
import re

from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles


class ParcoursStaticFiles(StaticFiles):
    """Serve pages/assets, never source workbooks, mappings or review exports."""

    allowed_extensions = frozenset({
        ".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif",
        ".svg", ".ico", ".webp", ".woff", ".woff2", ".ttf",
    })

    async def get_response(self, path, scope):
        candidate = PurePosixPath(path.replace("\\", "/"))
        if any(part.startswith(".") and part not in (".", "..") for part in candidate.parts):
            raise HTTPException(status_code=404)
        if str(candidate) != "robots.txt" and candidate.suffix.lower() not in self.allowed_extensions:
            directory_route = re.fullmatch(r"action/[a-z0-9]{10,64}", str(candidate))
            if path not in ("", ".") and not directory_route:
                raise HTTPException(status_code=404)
        return await super().get_response(path, scope)
