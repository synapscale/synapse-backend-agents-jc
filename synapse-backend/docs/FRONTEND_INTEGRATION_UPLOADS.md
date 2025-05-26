# Documentação de Integração Frontend - Serviço de Uploads

## Visão Geral

Este documento descreve como integrar o frontend com o serviço de uploads do backend SynapScale, implementado na Fase 3. O serviço oferece funcionalidades seguras para upload, listagem e gerenciamento de arquivos com autenticação, autorização, validação de conteúdo e proteção contra abusos.

## Endpoints Disponíveis

### 1. Upload de Arquivo

**Endpoint:** `POST /uploads/`

**Autenticação:** Bearer Token JWT com escopo `uploads:write`

**Formato:** Multipart Form Data

**Parâmetros:**
- `file`: Arquivo a ser enviado (obrigatório)
- `description`: Descrição do arquivo (opcional)
- `tags`: Tags separadas por vírgula (opcional)

**Exemplo de Requisição:**
```javascript
// Usando fetch com FormData
const formData = new FormData();
formData.append('file', fileObject);
formData.append('description', 'Descrição do arquivo');
formData.append('tags', 'tag1,tag2,tag3');

const response = await fetch('https://api.synapse.com/uploads/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
```

**Resposta de Sucesso (200 OK):**
```json
{
  "file_id": "f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3",
  "filename": "documento.pdf",
  "url": "https://storage.synapse.com/uploads/f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3/documento.pdf",
  "content_type": "application/pdf",
  "size": 1024567,
  "category": "document",
  "description": "Descrição do arquivo",
  "tags": ["tag1", "tag2", "tag3"],
  "created_at": "2025-05-26T16:30:00Z",
  "user_id": "user123"
}
```

**Possíveis Erros:**
- `400 Bad Request`: Arquivo vazio ou tipo não permitido
- `401 Unauthorized`: Token ausente ou inválido
- `403 Forbidden`: Sem permissão de escrita
- `413 Payload Too Large`: Arquivo excede o tamanho máximo
- `429 Too Many Requests`: Limite de requisições excedido

### 2. Listar Arquivos

**Endpoint:** `GET /uploads/`

**Autenticação:** Bearer Token JWT com escopo `uploads:read`

**Parâmetros de Query:**
- `category`: Filtrar por categoria (opcional)
- `tags`: Filtrar por tags (opcional)
- `page`: Número da página (opcional, padrão: 1)
- `limit`: Itens por página (opcional, padrão: 20)

**Exemplo de Requisição:**
```javascript
const response = await fetch('https://api.synapse.com/uploads/?category=document&tags=importante&page=1&limit=10', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const files = await response.json();
```

**Resposta de Sucesso (200 OK):**
```json
[
  {
    "file_id": "f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3",
    "filename": "documento.pdf",
    "url": "https://storage.synapse.com/uploads/f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3/documento.pdf",
    "content_type": "application/pdf",
    "size": 1024567,
    "category": "document",
    "description": "Descrição do arquivo",
    "tags": ["tag1", "tag2", "tag3"],
    "created_at": "2025-05-26T16:30:00Z"
  },
  // ... outros arquivos
]
```

### 3. Obter Arquivo por ID

**Endpoint:** `GET /uploads/{file_id}`

**Autenticação:** Bearer Token JWT com escopo `uploads:read`

**Exemplo de Requisição:**
```javascript
const fileId = "f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3";
const response = await fetch(`https://api.synapse.com/uploads/${fileId}`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const file = await response.json();
```

**Resposta de Sucesso (200 OK):**
```json
{
  "file_id": "f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3",
  "filename": "documento.pdf",
  "url": "https://storage.synapse.com/uploads/f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3/documento.pdf",
  "content_type": "application/pdf",
  "size": 1024567,
  "category": "document",
  "description": "Descrição do arquivo",
  "tags": ["tag1", "tag2", "tag3"],
  "created_at": "2025-05-26T16:30:00Z",
  "user_id": "user123"
}
```

### 4. Excluir Arquivo

**Endpoint:** `DELETE /uploads/{file_id}`

**Autenticação:** Bearer Token JWT com escopo `uploads:write`

**Exemplo de Requisição:**
```javascript
const fileId = "f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3";
const response = await fetch(`https://api.synapse.com/uploads/${fileId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const result = await response.json();
```

**Resposta de Sucesso (200 OK):**
```json
{
  "message": "Arquivo excluído com sucesso",
  "file_id": "f8a7b6c5-d4e3-2f1g-0h9i-j8k7l6m5n4o3"
}
```

## Tipos de Arquivos Permitidos

O serviço aceita os seguintes tipos de arquivos:

### Imagens
- JPEG/JPG (`image/jpeg`)
- PNG (`image/png`)
- GIF (`image/gif`)
- WebP (`image/webp`)
- SVG (`image/svg+xml`)

### Documentos
- PDF (`application/pdf`)
- Word (`application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- Texto (`text/plain`)
- Markdown (`text/markdown`)

### Áudio
- MP3 (`audio/mpeg`)
- WAV (`audio/wav`)
- OGG (`audio/ogg`)

### Vídeo
- MP4 (`video/mp4`)
- WebM (`video/webm`)

### Arquivos Compactados
- ZIP (`application/zip`)
- TAR (`application/x-tar`)
- GZIP (`application/gzip`)

## Limites e Restrições

- **Tamanho máximo de arquivo:** 5MB
- **Rate limiting:** 30 requisições por minuto por usuário
- **Formatos de arquivo:** Apenas os tipos listados acima são permitidos
- **Nomes de arquivo:** Caracteres especiais são automaticamente sanitizados

## Componente de Upload para React

Abaixo está um exemplo de componente React para integração com o serviço de uploads:

```jsx
import React, { useState } from 'react';
import axios from 'axios';

const FileUploader = ({ token, onUploadSuccess, onUploadError }) => {
  const [file, setFile] = useState(null);
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      onUploadError('Selecione um arquivo para upload');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    if (description) {
      formData.append('description', description);
    }
    
    if (tags) {
      formData.append('tags', tags);
    }
    
    setLoading(true);
    setProgress(0);
    
    try {
      const response = await axios.post('https://api.synapse.com/uploads/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        }
      });
      
      setLoading(false);
      onUploadSuccess(response.data);
      
      // Limpar formulário
      setFile(null);
      setDescription('');
      setTags('');
      setProgress(0);
      
    } catch (error) {
      setLoading(false);
      
      let errorMessage = 'Erro ao fazer upload do arquivo';
      
      if (error.response) {
        // Erros do servidor
        switch (error.response.status) {
          case 400:
            errorMessage = error.response.data.detail || 'Arquivo inválido';
            break;
          case 401:
            errorMessage = 'Autenticação necessária';
            break;
          case 403:
            errorMessage = 'Sem permissão para upload';
            break;
          case 413:
            errorMessage = 'Arquivo muito grande';
            break;
          case 429:
            errorMessage = 'Muitas requisições. Tente novamente mais tarde.';
            break;
          default:
            errorMessage = `Erro ${error.response.status}: ${error.response.data.detail || 'Erro desconhecido'}`;
        }
      }
      
      onUploadError(errorMessage);
    }
  };

  return (
    <div className="file-uploader">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="file">Arquivo:</label>
          <input 
            type="file" 
            id="file" 
            onChange={handleFileChange} 
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">Descrição:</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="tags">Tags (separadas por vírgula):</label>
          <input
            type="text"
            id="tags"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            disabled={loading}
          />
        </div>
        
        {loading && (
          <div className="progress-bar">
            <div 
              className="progress" 
              style={{ width: `${progress}%` }}
            ></div>
            <span>{progress}%</span>
          </div>
        )}
        
        <button type="submit" disabled={loading || !file}>
          {loading ? 'Enviando...' : 'Enviar Arquivo'}
        </button>
      </form>
    </div>
  );
};

export default FileUploader;
```

## Componente de Listagem de Arquivos

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const FileList = ({ token, category, onFileSelect, onDeleteSuccess }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchFiles = async (pageNum = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      let url = `https://api.synapse.com/uploads/?page=${pageNum}&limit=10`;
      
      if (category) {
        url += `&category=${category}`;
      }
      
      const response = await axios.get(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (pageNum === 1) {
        setFiles(response.data);
      } else {
        setFiles(prev => [...prev, ...response.data]);
      }
      
      setHasMore(response.data.length === 10);
      setPage(pageNum);
      
    } catch (error) {
      setError('Erro ao carregar arquivos');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles(1);
  }, [token, category]);

  const handleLoadMore = () => {
    fetchFiles(page + 1);
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm('Tem certeza que deseja excluir este arquivo?')) {
      return;
    }
    
    try {
      await axios.delete(`https://api.synapse.com/uploads/${fileId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setFiles(files.filter(file => file.file_id !== fileId));
      
      if (onDeleteSuccess) {
        onDeleteSuccess(fileId);
      }
      
    } catch (error) {
      alert('Erro ao excluir arquivo');
      console.error(error);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="file-list">
      {files.length === 0 && !loading ? (
        <p>Nenhum arquivo encontrado</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Tipo</th>
              <th>Tamanho</th>
              <th>Data</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {files.map(file => (
              <tr key={file.file_id}>
                <td>
                  <a 
                    href={file.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                  >
                    {file.filename}
                  </a>
                </td>
                <td>{file.category}</td>
                <td>{formatFileSize(file.size)}</td>
                <td>{formatDate(file.created_at)}</td>
                <td>
                  <button 
                    onClick={() => onFileSelect(file)}
                    className="btn-view"
                  >
                    Ver
                  </button>
                  <button 
                    onClick={() => handleDelete(file.file_id)}
                    className="btn-delete"
                  >
                    Excluir
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      
      {loading && <div className="loading">Carregando...</div>}
      
      {hasMore && !loading && (
        <button 
          onClick={handleLoadMore}
          className="btn-load-more"
        >
          Carregar Mais
        </button>
      )}
    </div>
  );
};

export default FileList;
```

## Tratamento de Erros

O serviço de uploads retorna códigos de erro HTTP padronizados com mensagens descritivas. Implemente tratamento de erros adequado no frontend para melhorar a experiência do usuário:

- **400 Bad Request**: Validação de arquivo falhou (vazio, formato inválido)
- **401 Unauthorized**: Token ausente ou inválido
- **403 Forbidden**: Sem permissão para a operação
- **404 Not Found**: Arquivo não encontrado
- **413 Payload Too Large**: Arquivo excede o tamanho máximo
- **429 Too Many Requests**: Limite de requisições excedido

Para o erro 429, o serviço inclui o cabeçalho `Retry-After` indicando o tempo em segundos para aguardar antes de tentar novamente.

## Considerações de Segurança

1. **Tokens JWT**: Armazene tokens de forma segura (HttpOnly cookies ou localStorage com precauções)
2. **Validação no Frontend**: Implemente validação prévia de tipos e tamanhos de arquivo
3. **Sanitização**: Evite enviar nomes de arquivo com caracteres especiais ou caminhos
4. **CORS**: O backend está configurado para aceitar apenas origens permitidas
5. **Rate Limiting**: Implemente backoff exponencial para lidar com erros 429

## Próximos Passos

1. Integre os componentes de upload e listagem em sua aplicação
2. Implemente tratamento de erros adequado
3. Adicione feedback visual para operações de upload e exclusão
4. Teste a integração em diferentes navegadores e dispositivos
