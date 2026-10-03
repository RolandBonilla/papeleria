"""Tipo Money: guarda dinero como centavos enteros y lo devuelve como Decimal.

SQLite no tiene un tipo decimal exacto; con enteros se evitan errores de redondeo.
"""
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import Integer
from sqlalchemy.types import TypeDecorator


class Money(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return int((Decimal(value) * 100).to_integral_value(ROUND_HALF_UP))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Decimal(value).scaleb(-2)
