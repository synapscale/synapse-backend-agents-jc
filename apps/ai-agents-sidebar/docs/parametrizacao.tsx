"use client"

/**
 * Documentação de Parametrização dos Componentes
 *
 * Este arquivo contém a documentação detalhada sobre a parametrização dos componentes
 * do sistema, incluindo tipos, valores padrão, e exemplos de uso.
 */

/**
 * Componentes Atômicos
 *
 * Estes componentes são os blocos de construção básicos da interface.
 */

/**
 * IconButton
 *
 * Um botão com ícone que pode opcionalmente mostrar um rótulo.
 *
 * Props:
 * - icon: React.ReactNode (obrigatório) - O ícone a ser exibido
 * - label: string (obrigatório) - O texto do botão (pode ser visível ou apenas para acessibilidade)
 * - showLabel: boolean (opcional, padrão: true) - Se o rótulo deve ser visível
 * - asChild: boolean (opcional, padrão: false) - Se o componente deve renderizar seu filho como o elemento raiz
 * - ...props: ButtonProps - Todas as props do componente Button
 *
 * Exemplo de uso:
 * ```tsx
 * <IconButton
 *   icon={<Save />}
 *   label="Salvar"
 *   onClick={handleSave}
 *   variant="primary"
 * />
 * ```
 */

/**
 * Section
 *
 * Um componente de seção reutilizável com título, descrição e conteúdo.
 *
 * Props:
 * - title: React.ReactNode (opcional) - O título da seção
 * - description: React.ReactNode (opcional) - A descrição da seção
 * - titleClassName: string (opcional) - Classes adicionais para o título
 * - descriptionClassName: string (opcional) - Classes adicionais para a descrição
 * - contentClassName: string (opcional) - Classes adicionais para o conteúdo
 * - headerClassName: string (opcional) - Classes adicionais para o cabeçalho
 * - headerRight: React.ReactNode (opcional) - Conteúdo a ser exibido à direita do cabeçalho
 * - ...props: React.HTMLAttributes<HTMLElement> - Atributos HTML para o elemento section
 *
 * Exemplo de uso:
 * ```tsx
 * <Section
 *   title="Configurações"
 *   description="Gerencie suas preferências"
 *   headerRight={<Button>Salvar</Button>}
 * >
 *   <p>Conteúdo da seção</p>
 * </Section>
 * ```
 */

/**
 * BadgeList
 *
 * Um componente para exibir uma lista de badges com opções para adicionar e remover.
 *
 * Props:
 * - items: BadgeItem[] (obrigatório) - Array de itens a serem exibidos
 *   - BadgeItem: { id: string, label: string }
 * - onAdd: () => void (opcional) - Função chamada quando o botão de adicionar é clicado
 * - onRemove: (id: string) => void (opcional) - Função chamada quando um badge é removido
 * - addLabel: string (opcional, padrão: "Adicionar") - Texto do botão de adicionar
 * - className: string (opcional) - Classes adicionais para o componente
 * - badgeClassName: string (opcional) - Classes adicionais para os badges
 * - buttonClassName: string (opcional) - Classes adicionais para o botão de adicionar
 * - readOnly: boolean (opcional, padrão: false) - Se a lista é somente leitura
 *
 * Exemplo de uso:
 * ```tsx
 * <BadgeList
 *   items={[{ id: '1', label: 'Item 1' }, { id: '2', label: 'Item 2' }]}
 *   onAdd={handleAdd}
 *   onRemove={handleRemove}
 *   addLabel="Adicionar Item"
 * />
 * ```
 */

/**
 * Componentes de Formulário
 *
 * Estes componentes são usados para construir formulários.
 */

/**
 * FormField
 *
 * Um componente de campo de formulário reutilizável com label, descrição e mensagem de erro.
 *
 * Props:
 * - label: string (opcional) - O rótulo do campo
 * - htmlFor: string (opcional) - O ID do elemento de entrada associado
 * - description: string (opcional) - A descrição do campo
 * - error: string (opcional) - A mensagem de erro
 * - required: boolean (opcional) - Se o campo é obrigatório
 * - labelClassName: string (opcional) - Classes adicionais para o rótulo
 * - descriptionClassName: string (opcional) - Classes adicionais para a descrição
 * - errorClassName: string (opcional) - Classes adicionais para a mensagem de erro
 * - ...props: React.HTMLAttributes<HTMLDivElement> - Atributos HTML para o elemento div
 *
 * Exemplo de uso:
 * ```tsx
 * <FormField
 *   label="Nome"
 *   htmlFor="name"
 *   description="Digite seu nome completo"
 *   error={errors.name}
 *   required
 * >
 *   <Input id="name" value={name} onChange={handleChange} />
 * </FormField>
 * ```
 */

/**
 * InputField
 *
 * Um componente de campo de entrada com label e mensagem de erro.
 *
 * Props:
 * - id: string (obrigatório) - O ID do campo
 * - label: string (opcional) - O rótulo do campo
 * - value: string (obrigatório) - O valor do campo
 * - onChange: (value: string) => void (obrigatório) - Função chamada quando o valor muda
 * - description: string (opcional) - A descrição do campo
 * - error: string (opcional) - A mensagem de erro
 * - required: boolean (opcional) - Se o campo é obrigatório
 * - className: string (opcional) - Classes adicionais para o componente
 * - inputClassName: string (opcional) - Classes adicionais para o elemento de entrada
 * - ...props: React.InputHTMLAttributes<HTMLInputElement> - Atributos HTML para o elemento input
 *
 * Exemplo de uso:
 * ```tsx
 * <InputField
 *   id="email"
 *   label="Email"
 *   value={email}
 *   onChange={setEmail}
 *   type="email"
 *   required
 *   error={errors.email}
 * />
 * ```
 */

/**
 * SelectField
 *
 * Um componente de campo de seleção com label e mensagem de erro.
 *
 * Props:
 * - id: string (obrigatório) - O ID do campo
 * - label: string (opcional) - O rótulo do campo
 * - value: string (obrigatório) - O valor selecionado
 * - onChange: (value: string) => void (obrigatório) - Função chamada quando o valor muda
 * - options: SelectOption[] (obrigatório) - Array de opções
 *   - SelectOption: { value: string, label: string }
 * - placeholder: string (opcional, padrão: "Selecione uma opção") - Texto exibido quando nenhum valor está selecionado
 * - description: string (opcional) - A descrição do campo
 * - error: string (opcional) - A mensagem de erro
 * - required: boolean (opcional) - Se o campo é obrigatório
 * - className: string (opcional) - Classes adicionais para o componente
 * - triggerClassName: string (opcional) - Classes adicionais para o elemento de trigger
 *
 * Exemplo de uso:
 * ```tsx
 * <SelectField
 *   id="country"
 *   label="País"
 *   value={country}
 *   onChange={setCountry}
 *   options={[
 *     { value: 'br', label: 'Brasil' },
 *     { value: 'us', label: 'Estados Unidos' }
 *   ]}
 *   required
 * />
 * ```
 */

/**
 * Componentes Específicos da Aplicação
 *
 * Estes componentes são específicos para a aplicação de agentes.
 */

/**
 * AgentFormHeader
 *
 * Cabeçalho do formulário de agente com botões de navegação e ações.
 *
 * Props:
 * - isNewAgent: boolean (obrigatório) - Se é um novo agente ou edição
 * - isSubmitting: boolean (obrigatório) - Se o formulário está sendo enviado
 * - onSubmit: () => void (obrigatório) - Função chamada quando o botão de salvar é clicado
 * - onOpenTemplates: () => void (obrigatório) - Função chamada quando o botão de templates é clicado
 * - isValid: boolean (obrigatório) - Se o formulário é válido
 * - title: string (opcional) - Título personalizado para o cabeçalho
 *
 * Exemplo de uso:
 * ```tsx
 * <AgentFormHeader
 *   isNewAgent={true}
 *   isSubmitting={isSubmitting}
 *   onSubmit={handleSubmit}
 *   onOpenTemplates={openTemplates}
 *   isValid={isValid}
 * />
 * ```
 */

/**
 * PromptEditor
 *
 * Editor de prompt com ferramentas e botão de template.
 *
 * Props:
 * - value: string (obrigatório) - O valor do prompt
 * - onChange: (value: string) => void (obrigatório) - Função chamada quando o valor muda
 * - onToolClick: (toolId: string) => void (opcional) - Função chamada quando uma ferramenta é clicada
 * - onSelectTemplate: (content: string) => void (opcional) - Função chamada quando um template é selecionado
 * - tools: PromptTool[] (opcional) - Array de ferramentas de prompt
 *   - PromptTool: { id: string, name: string, icon: React.ReactNode }
 * - className: string (opcional) - Classes adicionais para o componente
 * - minHeight: string (opcional, padrão: "300px") - Altura mínima do editor
 * - showTemplateButton: boolean (opcional, padrão: true) - Se o botão de template deve ser exibido
 *
 * Exemplo de uso:
 * ```tsx
 * <PromptEditor
 *   value={prompt}
 *   onChange={setPrompt}
 *   onToolClick={handleToolClick}
 *   onSelectTemplate={handleSelectTemplate}
 * />
 * ```
 */

/**
 * Hooks Personalizados
 *
 * Estes hooks são usados para gerenciar estado e lógica.
 */

/**
 * useLocalStorage
 *
 * Hook para persistir e recuperar valores do localStorage.
 *
 * Parâmetros:
 * - key: string (obrigatório) - Chave para armazenar o valor
 * - initialValue: T (obrigatório) - Valor inicial caso não exista no localStorage
 *
 * Retorna:
 * - [T, (value: T | ((val: T) => T)) => void] - Um array com o valor armazenado e uma função para atualizá-lo
 *
 * Exemplo de uso:
 * ```tsx
 * const [theme, setTheme] = useLocalStorage('theme', 'light');
 * ```
 */

/**
 * useForm
 *
 * Hook para gerenciar formulários com validação.
 *
 * Parâmetros:
 * - options: FormOptions<T> (obrigatório) - Opções do formulário
 *   - initialValues: T (obrigatório) - Valores iniciais do formulário
 *   - onSubmit: (values: T) => void | Promise<void> (opcional) - Função chamada quando o formulário é enviado
 *   - validate: (values: T) => Partial<Record<keyof T, string>> (opcional) - Função para validar o formulário
 *
 * Retorna:
 * - Um objeto com os seguintes campos:
 *   - values: T - Valores atuais do formulário
 *   - errors: Partial<Record<keyof T, string>> - Erros de validação
 *   - touched: Partial<Record<keyof T, boolean>> - Campos que foram tocados
 *   - isSubmitting: boolean - Se o formulário está sendo enviado
 *   - isValid: boolean - Se o formulário é válido
 *   - handleChange: (field: keyof T, value: any) => void - Função para atualizar um campo
 *   - handleSubmit: (e?: React.FormEvent) => Promise<void> - Função para enviar o formulário
 *   - reset: (newValues?: T) => void - Função para resetar o formulário
 *   - setValues: React.Dispatch<React.SetStateAction<T>> - Função para atualizar todos os valores
 *
 * Exemplo de uso:
 * ```tsx
 * const form = useForm({
 *   initialValues: { name: '', email: '' },
 *   onSubmit: async (values) => {
 *     await api.saveUser(values);
 *   },
 *   validate: (values) => {
 *     const errors = {};
 *     if (!values.name) errors.name = 'Nome é obrigatório';
 *     if (!values.email) errors.email = 'Email é obrigatório';
 *     return errors;
 *   }
 * });
 * ```
 */

/**
 * useDisclosure
 *
 * Hook para gerenciar estados de abertura/fechamento.
 *
 * Parâmetros:
 * - initialState: boolean (opcional, padrão: false) - Estado inicial
 *
 * Retorna:
 * - Um objeto com os seguintes campos:
 *   - isOpen: boolean - Se está aberto
 *   - open: () => void - Função para abrir
 *   - close: () => void - Função para fechar
 *   - toggle: () => void - Função para alternar
 *
 * Exemplo de uso:
 * ```tsx
 * const { isOpen, open, close, toggle } = useDisclosure();
 * ```
 */
