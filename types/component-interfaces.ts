/**
 * Arquivo de definição de interfaces para componentes
 *
 * Este arquivo contém interfaces TypeScript que definem as propriedades
 * esperadas pelos diversos componentes da aplicação, facilitando a
 * manutenção, documentação e tipagem forte.
 */

import type { ReactNode, MouseEvent } from "react"
import type { NodeCategory } from "@/hooks/use-nodes"

/**
 * Interface base para componentes que podem receber classes CSS adicionais
 */
export interface BaseComponentProps {
  /** Classes CSS adicionais a serem aplicadas ao componente */
  className?: string
}

/**
 * Interface para componentes que podem ter filhos
 */
export interface WithChildrenProps {
  /** Elementos filhos do componente */
  children: ReactNode
}

/**
 * Interface para componentes que podem ser desabilitados
 */
export interface DisableableProps {
  /** Indica se o componente está desabilitado */
  disabled?: boolean
}

/**
 * Interface para componentes que podem ser selecionados
 */
export interface SelectableProps {
  /** Indica se o componente está selecionado */
  selected?: boolean
  /** Função chamada quando o estado de seleção muda */
  onSelectionChange?: (selected: boolean) => void
}

/**
 * Interface para componentes que podem ser arrastados
 */
export interface DraggableProps {
  /** Indica se o componente pode ser arrastado */
  draggable?: boolean
  /** Função chamada quando o arrasto começa */
  onDragStart?: (event: MouseEvent) => void
  /** Função chamada durante o arrasto */
  onDrag?: (event: MouseEvent) => void
  /** Função chamada quando o arrasto termina */
  onDragEnd?: (event: MouseEvent) => void
}

/**
 * Interface para componentes que podem receber soltura de elementos arrastados
 */
export interface DroppableProps {
  /** Indica se o componente pode receber elementos arrastados */
  droppable?: boolean
  /** Função chamada quando um elemento é solto sobre este componente */
  onDrop?: (event: MouseEvent) => void
  /** Função chamada quando um elemento arrastável entra na área deste componente */
  onDragEnter?: (event: MouseEvent) => void
  /** Função chamada quando um elemento arrastável sai da área deste componente */
  onDragLeave?: (event: MouseEvent) => void
  /** Função chamada quando um elemento arrastável está sobre este componente */
  onDragOver?: (event: MouseEvent) => void
}

/**
 * Interface para componentes de nó no canvas
 */
export interface NodeComponentProps extends BaseComponentProps, SelectableProps, DraggableProps {
  /** ID único do nó */
  id: string
  /** Nome exibido do nó */
  name: string
  /** Descrição do nó */
  description: string
  /** Categoria do nó, que determina sua aparência e comportamento */
  category: NodeCategory
  /** Posição do nó no canvas (coordenadas x e y) */
  position?: { x: number; y: number }
  /** Função chamada quando o nó é clicado */
  onClick?: (event: MouseEvent) => void
  /** Função chamada quando o nó é removido */
  onRemove?: (id: string) => void
  /** Configuração adicional do nó em formato JSON ou string */
  config?: string | Record<string, any>
  /** Indica se o nó é editável */
  editable?: boolean
}

/**
 * Interface para componentes de porta de nó (entradas e saídas)
 */
export interface NodePortProps extends BaseComponentProps {
  /** ID único da porta */
  id: string
  /** Nome exibido da porta */
  name: string
  /** Tipo da porta (entrada ou saída) */
  type: "input" | "output"
  /** Tipo de dados que a porta aceita ou fornece */
  dataType: string
  /** Indica se a porta é obrigatória */
  required?: boolean
  /** Indica se a porta aceita múltiplas conexões */
  multiple?: boolean
  /** Função chamada quando a porta é conectada */
  onConnect?: (portId: string, targetPortId: string) => void
  /** Função chamada quando a porta é desconectada */
  onDisconnect?: (portId: string, targetPortId: string) => void
  /** IDs das conexões associadas a esta porta */
  connections?: string[]
  /** Descrição da porta */
  description?: string
}

/**
 * Interface para componentes de conexão entre portas
 */
export interface ConnectionProps extends BaseComponentProps, SelectableProps {
  /** ID único da conexão */
  id: string
  /** ID do nó de origem */
  sourceNodeId: string
  /** ID da porta de origem */
  sourcePortId: string
  /** ID do nó de destino */
  targetNodeId: string
  /** ID da porta de destino */
  targetPortId: string
  /** Função chamada quando a conexão é removida */
  onRemove?: (id: string) => void
}

/**
 * Interface para componentes de categoria de nó na barra lateral
 */
export interface NodeCategoryProps extends BaseComponentProps {
  /** ID único da categoria */
  id: string
  /** Nome exibido da categoria */
  name: string
  /** Descrição da categoria */
  description: string
  /** Categoria do nó */
  category: NodeCategory
  /** Indica se é um nó criado pelo usuário */
  isUserNode?: boolean
  /** Função chamada quando o nó é editado */
  onEdit?: () => void
  /** Função chamada quando o nó é excluído */
  onDelete?: () => void
}

/**
 * Interface para componentes de formulário de nó
 */
export interface NodeFormProps extends BaseComponentProps {
  /** Indica se o formulário está aberto */
  open: boolean
  /** Função chamada quando o estado de abertura muda */
  onOpenChange: (open: boolean) => void
  /** Função chamada quando o formulário é enviado */
  onSubmit: (data: any) => void
  /** Dados iniciais para preencher o formulário */
  initialData?: {
    name: string
    description: string
    category: string
    config?: string
  }
  /** Categoria inicial selecionada */
  initialCategory?: string
  /** Indica se está editando um nó existente */
  isEditing?: boolean
  /** Lista de categorias de nó disponíveis */
  nodeCategories: Array<{
    id: string
    name: string
    description: string
    icon: string
  }>
}

/**
 * Interface para componentes de item do marketplace
 */
export interface MarketplaceItemProps extends BaseComponentProps {
  /** ID único do item */
  id: string
  /** Nome exibido do item */
  name: string
  /** Descrição do item */
  description: string
  /** Autor do item */
  author: string
  /** Avaliação do item (0-5) */
  rating: number
  /** Número de downloads do item */
  downloads: number
  /** Preço do item (0 para gratuito) */
  price: number
  /** URL da imagem do item */
  imageUrl?: string
  /** Tags associadas ao item */
  tags?: string[]
  /** Tipo do item (skill, node, etc.) */
  type: string
  /** Versão do item */
  version: string
  /** Data de publicação do item */
  publishedAt: string | Date
  /** Função chamada quando o item é clicado */
  onClick?: () => void
}

/**
 * Interface para componentes de coleção do marketplace
 */
export interface CollectionProps extends BaseComponentProps {
  /** ID único da coleção */
  id: string
  /** Nome exibido da coleção */
  name: string
  /** Descrição da coleção */
  description: string
  /** Número de itens na coleção */
  itemCount: number
  /** URL da imagem da coleção */
  imageUrl?: string
  /** Função chamada quando a coleção é clicada */
  onClick?: () => void
}
