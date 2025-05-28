"""
Módulos mock para dependências externas não disponíveis.

Este módulo fornece implementações simuladas de bibliotecas externas
que podem não estar disponíveis no ambiente de execução, permitindo
que os testes sejam executados sem falhas de importação.
"""

import sys
from unittest.mock import MagicMock

# Criar módulos mock para xai
xai_mock = MagicMock()
xai_mock.__version__ = "0.1.0"
xai_mock.GrokClient = MagicMock()
sys.modules["xai"] = xai_mock

# Criar módulos mock para deepseek
deepseek_mock = MagicMock()
deepseek_mock.__version__ = "0.1.0"
deepseek_mock.DeepSeekClient = MagicMock()
sys.modules["deepseek"] = deepseek_mock
