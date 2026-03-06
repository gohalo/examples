from typing import List, Any


class Engine(object):
    def fetchraw(self, sql) -> None | List[Any]:
        raise RuntimeError("not available")

    def fetchall(self, sql) -> None | List[Any]:
        raise RuntimeError("not available")

    def fetchone(self, sql) -> None | Any:
        raise RuntimeError("not available")
