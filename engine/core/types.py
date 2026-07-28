"""Tipos de datos compartidos del engine.

Define el CONTRATO de salida que todo mercado debe respetar: ``MarketResult``.
Este molde garantiza que todos los plugins (córners, goles, tarjetas, BTTS...)
devuelvan la misma forma de resultado, para que la API y el frontend los
consuman de manera uniforme.

Son solo contenedores de datos: sin lógica de negocio ni modelos de base de
datos.
"""

from dataclasses import dataclass, field


@dataclass
class MarketResult:
    """Resultado estándar de cualquier mercado del engine.

    Atributos:
        market:        Código del mercado que lo produjo (p. ej. "corners").
        indice:        Índice de apuesta 0-100 (calidad/volumen esperado).
        valores:       Números intermedios y finales del cálculo (dict), para
                       transparencia y para que el frontend muestre detalles.
        explicacion:   Texto legible en español que justifica el índice.
        advertencias:  Lista de avisos (p. ej. datos históricos insuficientes).
        confiable:     False si alguna advertencia compromete la fiabilidad.
    """

    market: str
    indice: float
    valores: dict = field(default_factory=dict)
    explicacion: str = ""
    advertencias: list = field(default_factory=list)
    confiable: bool = True

    def resumen(self) -> str:
        """Devuelve un resumen de una línea, útil para logs/consola."""
        estado = "confiable" if self.confiable else "POCO CONFIABLE"
        return f"[{self.market}] índice={self.indice:.0f}/100 ({estado})"
