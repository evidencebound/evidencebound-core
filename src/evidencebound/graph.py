"""Deterministic dependency graph with exact blast-radius traversal."""
from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable

from .models import Checkpoint


class GraphError(ValueError):
    pass


class DependencyGraph:
    def __init__(self, checkpoints: Iterable[Checkpoint] = ()) -> None:
        self._nodes: dict[str, Checkpoint] = {}
        for checkpoint in checkpoints:
            if checkpoint.checkpoint_id in self._nodes:
                raise GraphError(f"duplicate checkpoint id: {checkpoint.checkpoint_id}")
            self._nodes[checkpoint.checkpoint_id] = checkpoint
        self._validate_dependencies()
        self._validate_acyclic()

    @property
    def checkpoint_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def _validate_dependencies(self) -> None:
        for checkpoint in self._nodes.values():
            for dependency in checkpoint.depends_on:
                if dependency not in self._nodes:
                    raise GraphError(
                        f"checkpoint {checkpoint.checkpoint_id} depends on missing {dependency}"
                    )

    def _children(self) -> dict[str, set[str]]:
        children: dict[str, set[str]] = defaultdict(set)
        for checkpoint in self._nodes.values():
            for dependency in checkpoint.depends_on:
                children[dependency].add(checkpoint.checkpoint_id)
        return children

    def _validate_acyclic(self) -> None:
        self.topological_order()

    def topological_order(self) -> tuple[str, ...]:
        indegree = {node: 0 for node in self._nodes}
        children = self._children()
        for checkpoint in self._nodes.values():
            indegree[checkpoint.checkpoint_id] = len(checkpoint.depends_on)
        ready = deque(sorted(node for node, degree in indegree.items() if degree == 0))
        result: list[str] = []
        while ready:
            node = ready.popleft()
            result.append(node)
            for child in sorted(children.get(node, ())):
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
            if len(ready) > 1:
                ready = deque(sorted(ready))
        if len(result) != len(self._nodes):
            raise GraphError("dependency graph contains a cycle")
        return tuple(result)

    def descendants(self, checkpoint_id: str) -> tuple[str, ...]:
        if checkpoint_id not in self._nodes:
            raise GraphError(f"unknown checkpoint: {checkpoint_id}")
        children = self._children()
        seen: set[str] = set()
        queue = deque(sorted(children.get(checkpoint_id, ())))
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            queue.extend(sorted(children.get(current, ())))
        order = self.topological_order()
        return tuple(node for node in order if node in seen)

    def ancestors(self, checkpoint_id: str) -> tuple[str, ...]:
        if checkpoint_id not in self._nodes:
            raise GraphError(f"unknown checkpoint: {checkpoint_id}")
        seen: set[str] = set()
        queue = deque(sorted(self._nodes[checkpoint_id].depends_on))
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            queue.extend(sorted(self._nodes[current].depends_on))
        order = self.topological_order()
        return tuple(node for node in order if node in seen)

    def blast_radius(self, checkpoint_ids: Iterable[str]) -> tuple[str, ...]:
        roots = set(checkpoint_ids)
        for root in roots:
            if root not in self._nodes:
                raise GraphError(f"unknown checkpoint: {root}")
        affected = set(roots)
        for root in roots:
            affected.update(self.descendants(root))
        order = self.topological_order()
        return tuple(node for node in order if node in affected)

    def get(self, checkpoint_id: str) -> Checkpoint:
        try:
            return self._nodes[checkpoint_id]
        except KeyError as exc:
            raise GraphError(f"unknown checkpoint: {checkpoint_id}") from exc
