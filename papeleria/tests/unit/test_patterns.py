from app.database.connection import DatabaseManager
from app.patterns.observer import Observer, Subject
from app.patterns.singleton import SingletonMeta


def test_database_manager_siempre_devuelve_la_misma_instancia():
    assert DatabaseManager() is DatabaseManager()


def test_singleton_meta_funciona_con_cualquier_clase():
    class Configuracion(metaclass=SingletonMeta):
        pass

    assert Configuracion() is Configuracion()


class Recorder(Observer):
    def __init__(self):
        self.events = []

    def update(self, event):
        self.events.append(event)


def test_subject_notifica_a_los_observadores():
    subject, observer = Subject(), Recorder()
    subject.attach(observer)
    subject.attach(observer)  # adjuntar dos veces no duplica
    subject.notify("evento")
    assert observer.events == ["evento"]


def test_observador_desadjuntado_ya_no_recibe_eventos():
    subject, observer = Subject(), Recorder()
    subject.attach(observer)
    subject.detach(observer)
    subject.notify("evento")
    assert observer.events == []
