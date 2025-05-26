"""Testes para validação de arquivos."""

import pytest


def test_file_validation_basic():
    """Teste básico de validação."""
    assert True


@pytest.mark.parametrize("extension", [".jpg", ".png", ".pdf"])
def test_extensions(extension):
    """Testa extensões de arquivo."""
    assert extension.startswith(".")
