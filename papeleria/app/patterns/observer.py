"""Patrón Observer.

``Subject`` mantiene una lista de observadores y les avisa cuando ocurre un
evento. Cada ``Observer`` decide qué hacer. En este proyecto el evento es
"el stock de un producto cambió" y el observador genera o cierra alertas.
"""
from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    @abstractmethod
    def update(self, event: Any) -> None:
        """Recibe el evento notificado por el Subject."""


class Subject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: Any) -> None:
        for observer in list(self._observers):
            observer.update(event)
