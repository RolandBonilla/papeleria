"""Patrón Singleton.

Una metaclase guarda la única instancia de cada clase que la use. La primera
llamada a ``Clase()`` crea el objeto; las siguientes devuelven el mismo.
El candado evita que dos hilos creen dos instancias a la vez.
"""
import threading


class SingletonMeta(type):
    _instances: dict[type, object] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            with SingletonMeta._lock:
                if cls not in SingletonMeta._instances:
                    SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]
