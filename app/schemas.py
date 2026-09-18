"""Validacao estrutural nao equivale a verificacao matematica de cronogramas."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnaliseConsulta(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    tema: Literal['recarga', 'tarifa', 'margem', 'estrategia', 'dados', 'fora_do_dominio']
    resumo: str = Field(min_length=5, max_length=600)
    modo_citado: Literal['economico', 'equilibrado', 'operacional', 'nao_informado']
    dados_faltantes: list[str] = Field(max_length=12)
    alertas: list[str] = Field(max_length=12)
    proximo_passo: str = Field(min_length=5, max_length=700)
    natureza: Literal['analise_consultiva_nao_validada']
    requer_decisao_humana: Literal[True]

    @field_validator('resumo', 'proximo_passo')
    @classmethod
    def texto_util(cls, value):
        if len(value.strip()) < 5:
            raise ValueError('Texto deve conter informacao util.')
        return value.strip()

    @field_validator('dados_faltantes', 'alertas')
    @classmethod
    def itens_validos(cls, values):
        if any(not item.strip() or len(item) > 400 for item in values):
            raise ValueError('Itens devem ser textos nao vazios de ate 400 caracteres.')
        return [item.strip() for item in values]
