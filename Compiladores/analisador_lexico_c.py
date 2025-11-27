#!/usr/bin/env python3
"""
analisador_lexico_c.py
Analisador léxico simples para C (Python 3.8+)

Uso:
    python analisador_lexico_c.py arquivo.c
"""

import re
import sys
from dataclasses import dataclass
from typing import Iterator, List

# Palavras reservadas do C
PALAVRAS_RESERVADAS = {
    "auto","break","case","char","const","continue","default","do","double",
    "else","enum","extern","float","for","goto","if","inline","int","long",
    "register","restrict","return","short","signed","sizeof","static","struct",
    "switch","typedef","union","unsigned","void","volatile","while","_Bool",
    "_Complex","_Imaginary"
}

# Estrutura de Token
@dataclass
class Token:
    tipo: str
    valor: str
    linha: int
    coluna: int

    def __repr__(self):
        return f"Token({self.tipo!r}, {self.valor!r}, linha={self.linha}, col={self.coluna})"

class ErroLexico(Exception):
    def __init__(self, mensagem, linha, coluna):
        super().__init__(f"[Linha {linha}, Coluna {coluna}] {mensagem}")
        self.linha = linha
        self.coluna = coluna

class AnalisadorLexico:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.pos = 0
        self.linha = 1
        self.coluna = 1

        # Expressões regulares dos tokens
        self.especificacao = [
            ("ESPACO", r"[ \t]+"),
            ("NOVA_LINHA", r"\n"),
            ("COMENTARIO_ML", r"/\*(?:.|\n)*?\*/"),
            ("COMENTARIO_SL", r"//[^\n]*"),
            ("PREPROCESSADOR", r"\#\s*[A-Za-z_][A-Za-z0-9_]*[^\n]*"),
            ("STRING", r'"(\\.|[^"\\])*"'),
            ("CHAR", r"'(\\.|[^'\\])'"),
            ("FLOAT", r"(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?[fFlL]?"),
            ("INTEIRO", r"\d+(?:[uUlL])*"),
            ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
            ("OPERADOR", r"(\+\+|--|==|!=|>=|<=|->|<<|>>|&&|\|\||\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<=|>>=)"),
            ("OP_SIMBOLO", r"[+\-*/%&|^~!<>=?:]"),
            ("PONTO_VIRGULA", r";"),
            ("VIRGULA", r","),
            ("PAR_ESQ", r"\("),
            ("PAR_DIR", r"\)"),
            ("CHAVE_ESQ", r"\{"),
            ("CHAVE_DIR", r"\}"),
            ("COLCH_ESQ", r"\["),
            ("COLCH_DIR", r"\]"),
            ("PONTO", r"\."),
            ("INVALIDO", r"."),
        ]

        partes = []
        for nome, regex in self.especificacao:
            partes.append(f"(?P<{nome}>{regex})")
        self.regex_mestre = re.compile("|".join(partes), re.MULTILINE)

    def analisar(self) -> Iterator[Token]:
        for m in self.regex_mestre.finditer(self.codigo):
            tipo = m.lastgroup
            texto = m.group(tipo)

            if tipo == "ESPACO":
                self._avancar(texto)
                continue

            elif tipo == "NOVA_LINHA":
                self._avancar(texto)
                continue

            elif tipo in ("COMENTARIO_ML", "COMENTARIO_SL"):
                self._avancar(texto)
                continue

            elif tipo == "PREPROCESSADOR":
                token = Token("PREPROCESSADOR", texto.strip(), self.linha, self.coluna)
                self._avancar(texto)
                yield token
                continue

            elif tipo == "STRING":
                token = Token("STRING", texto, self.linha, self.coluna)
                self._avancar(texto)
                yield token
                continue

            elif tipo == "CHAR":
                token = Token("CHAR", texto, self.linha, self.coluna)
                self._avancar(texto)
                yield token
                continue

            elif tipo == "FLOAT":
                token = Token("FLOAT", texto, self.linha, self.coluna)
                self._avancar(texto)
                yield token
                continue

            elif tipo == "INTEIRO":
                token = Token("INTEIRO", texto, self.linha, self.coluna)
                self._avancar(texto)
                yield token
                continue

            elif tipo == "ID":
                tipo_token = "PALAVRA_CHAVE" if texto in PALAVRAS_RESERVADAS else "ID"
                token = Token(tipo_token, texto, self.linha, self.coluna)
                self._avancar(texto)
                yield token
                continue

            elif tipo == "OPERADOR" or tipo == "OP_SIMBOLO":
                token = Token("OPERADOR", texto, self.linha, self.coluna)
                self._avancar(texto)
                yield token
                continue

            elif tipo in ("PONTO_VIRGULA", "VIRGULA", "PAR_ESQ", "PAR_DIR",
                          "CHAVE_ESQ", "CHAVE_DIR", "COLCH_ESQ", "COLCH_DIR", "PONTO"):
                token = Token(tipo, texto, self.linha, self.coluna)
                self._avancar(texto)
                yield token
                continue

            elif tipo == "INVALIDO":
                self._avancar(texto)
                raise ErroLexico(f"Caractere inválido: {texto!r}", self.linha, self.coluna)

    def _avancar(self, texto: str):
        linhas = texto.split("\n")
        if len(linhas) == 1:
            self.coluna += len(texto)
        else:
            self.linha += len(linhas) - 1
            self.coluna = len(linhas[-1]) + 1
        self.pos += len(texto)

def analisar_codigo(codigo: str) -> List[Token]:
    return list(AnalisadorLexico(codigo).analisar())

def main(argv):
    if len(argv) < 2:
        print("Uso: python analisador_lexico_c.py arquivo.c")
        return 0

    nome_arquivo = argv[1]
    codigo = open(nome_arquivo, "r", encoding="utf-8").read()

    try:
        tokens = analisar_codigo(codigo)
        for t in tokens:
            print(t)
    except ErroLexico as e:
        print("Erro Léxico:", e)

if __name__ == "__main__":
    main(sys.argv)
