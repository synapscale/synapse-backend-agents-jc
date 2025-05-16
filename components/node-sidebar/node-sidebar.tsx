"use client"

import type React from "react"

import { useState, useCallback, useMemo } from "react"
import { Search, Plus, ChevronRight } from "lucide-react"
import * as LucideIcons from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { NodeCategory } from "./node-category"
import { NodeForm } from "./node-form"
import { type Node, useNodes } from "@/hooks/use-nodes"
import { toast } from "@/components/ui/use-toast"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { NODE_CATEGORIES, getNodesByCategory } from "@/types/node-types"

/**
 * NodeSidebar Component
 *
 * Sidebar for browsing, searching, and managing nodes.
 * Provides tabs for browsing node categories, templates, and user-created nodes.
 */
export function NodeSidebar() {
  // State for search query
  const [searchQuery, setSearchQuery] = useState("")

  // State for selected category
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  // State for node form
  const [nodeFormOpen, setNodeFormOpen] = useState(false)

  // State for active tab
  const [activeTab, setActiveTab] = useState("browse")

  // State for node being edited
  const [editingNode, setEditingNode] = useState<Node | null>(null)

  // State for node to be deleted
  const [nodeToDelete, setNodeToDelete] = useState<Node | null>(null)

  // State for delete dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  // Hook for accessing and manipulating nodes
  const { nodes, addNode, updateNode, deleteNode } = useNodes()

  /**
   * Filter nodes based on search query and selected category
   */
  const filteredNodes = useMemo(() => {
    // If no category is selected, return empty array
    if (!selectedCategory) return []

    // Get nodes of the selected category
    const categoryNodes = getNodesByCategory(selectedCategory as any)

    // Filter nodes based on search query
    return categoryNodes.filter((node) => {
      const matchesSearch =
        searchQuery === "" ||
        node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.description.toLowerCase().includes(searchQuery.toLowerCase())

      return matchesSearch
    })
  }, [searchQuery, selectedCategory])

  /**
   * Filter user nodes based on search query
   */
  const userNodes = useMemo(() => {
    return nodes.filter((node) => {
      const matchesSearch =
        searchQuery === "" ||
        node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.description.toLowerCase().includes(searchQuery.toLowerCase())

      return matchesSearch
    })
  }, [nodes, searchQuery])

  /**
   * Handle creating a new node
   */
  const handleCreateNode = useCallback(
    (data) => {
      // Add the new node
      addNode({
        name: data.name,
        description: data.description,
        category: data.category,
        config: data.config,
      })

      // Show success notification
      toast({
        title: "Node criado",
        description: `O node "${data.name}" foi criado com sucesso.`,
      })

      // Switch to "My Nodes" tab after creating a new node
      setActiveTab("my-nodes")
    },
    [addNode],
  )

  /**
   * Handle editing an existing node
   */
  const handleEditNode = useCallback(
    (data) => {
      if (editingNode) {
        // Update the existing node
        updateNode(editingNode.id, {
          name: data.name,
          description: data.description,
          category: data.category,
          config: data.config,
        })

        // Show success notification
        toast({
          title: "Node atualizado",
          description: `O node "${data.name}" foi atualizado com sucesso.`,
        })

        // Clear the editing node
        setEditingNode(null)
      }
    },
    [editingNode, updateNode],
  )

  /**
   * Open the edit modal for a node
   */
  const handleOpenEditModal = useCallback((node: Node) => {
    setEditingNode(node)
    setNodeFormOpen(true)
  }, [])

  /**
   * Confirm deletion of a node
   */
  const handleConfirmDelete = useCallback(() => {
    if (nodeToDelete) {
      // Delete the node
      deleteNode(nodeToDelete.id)

      // Show success notification
      toast({
        title: "Node excluído",
        description: `O node "${nodeToDelete.name}" foi excluído com sucesso.`,
      })

      // Clear the node to be deleted and close the dialog
      setNodeToDelete(null)
      setDeleteDialogOpen(false)
    }
  }, [nodeToDelete, deleteNode])

  /**
   * Open the delete confirmation dialog
   */
  const handleOpenDeleteDialog = useCallback((node: Node) => {
    setNodeToDelete(node)
    setDeleteDialogOpen(true)
  }, [])

  /**
   * Close the modal and clear the editing node
   */
  const handleCloseModal = useCallback((open: boolean) => {
    setNodeFormOpen(open)
    if (!open) {
      setEditingNode(null)
    }
  }, [])

  /**
   * Get the Lucide icon component by name
   */
  const getIconComponent = useCallback((iconName: string) => {
    const Icon = LucideIcons[iconName as keyof typeof LucideIcons] || LucideIcons.Box
    return <Icon className="h-5 w-5 mr-2" aria-hidden="true" />
  }, [])

  /**
   * Handle category selection
   */
  const handleCategorySelect = useCallback(
    (categoryId: string) => {
      setSelectedCategory(categoryId === selectedCategory ? null : categoryId)
    },
    [selectedCategory],
  )

  /**
   * Handle search input change
   */
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }, [])

  /**
   * Render category buttons
   */
  const categoryButtons = useMemo(
    () =>
      Object.values(NODE_CATEGORIES).map((category) => (
        <Button
          key={category.id}
          variant={category.id === selectedCategory ? "secondary" : "ghost"}
          className="w-full justify-start"
          onClick={() => handleCategorySelect(category.id)}
          aria-pressed={category.id === selectedCategory}
          aria-label={`Categoria ${category.name}`}
        >
          {getIconComponent(category.icon)}
          <span>{category.name}</span>
          <ChevronRight className="ml-auto h-4 w-4" aria-hidden="true" />
        </Button>
      )),
    [selectedCategory, getIconComponent, handleCategorySelect],
  )

  return (
    <div className="h-full w-full flex flex-col">
      <Tabs defaultValue="browse" value={activeTab} onValueChange={setActiveTab}>
        {/* Header with tabs and search */}
        <div className="px-4 py-3">
          <TabsList className="w-full">
            <TabsTrigger value="browse" className="flex-1">
              Navegar
            </TabsTrigger>
            <TabsTrigger value="templates" className="flex-1">
              Templates
            </TabsTrigger>
            <TabsTrigger value="my-nodes" className="flex-1">
              Meus Nodes
            </TabsTrigger>
          </TabsList>
          <div className="mt-3 relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="Buscar nodes..."
              className="pl-8"
              value={searchQuery}
              onChange={handleSearchChange}
              aria-label="Buscar nodes"
            />
          </div>
        </div>

        {/* Sidebar content */}
        <div className="overflow-auto flex-1">
          {/* Browse tab */}
          <TabsContent value="browse" className="mt-0 h-full">
            <div className="py-2">
              <div className="px-4 py-2 text-sm font-medium">Categorias</div>
              <div className="space-y-1 px-2">{categoryButtons}</div>
            </div>

            {/* List of nodes in the selected category */}
            {selectedCategory && (
              <div className="py-2">
                <div className="px-4 py-2 text-sm font-medium">{NODE_CATEGORIES[selectedCategory]?.name}</div>
                <div className="space-y-2 px-2">
                  {filteredNodes.map((node) => (
                    <NodeCategory
                      key={node.id}
                      id={node.id}
                      name={node.name}
                      description={node.description}
                      category={node.category}
                    />
                  ))}

                  {filteredNodes.length === 0 && (
                    <div className="text-center p-4 text-muted-foreground">Nenhum node encontrado nesta categoria.</div>
                  )}
                </div>
              </div>
            )}
          </TabsContent>

          {/* Templates tab */}
          <TabsContent value="templates" className="mt-0 h-full">
            <div className="py-2">
              <div className="px-4 py-2 flex justify-between items-center">
                <span className="text-sm font-medium">Templates</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2"
                  onClick={() => setNodeFormOpen(true)}
                  aria-label="Criar novo template"
                >
                  <Plus className="h-4 w-4 mr-1" aria-hidden="true" />
                  Novo
                </Button>
              </div>
              <div className="grid gap-2 p-2">
                {/* Templates will be added here */}
                <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
                  <p>Você ainda não criou nenhum template.</p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => setNodeFormOpen(true)}
                    aria-label="Criar primeiro template"
                  >
                    <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
                    Criar Primeiro Template
                  </Button>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* My Nodes tab */}
          <TabsContent value="my-nodes" className="mt-0 h-full">
            <div className="py-2">
              <div className="px-4 py-2 flex justify-between items-center">
                <span className="text-sm font-medium">Meus Nodes</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2"
                  onClick={() => setNodeFormOpen(true)}
                  aria-label="Criar novo node"
                >
                  <Plus className="h-4 w-4 mr-1" aria-hidden="true" />
                  Criar
                </Button>
              </div>
              {userNodes.length > 0 ? (
                <div className="grid gap-2 p-2">
                  {userNodes.map((node) => (
                    <NodeCategory
                      key={node.id}
                      id={node.id}
                      name={node.name}
                      description={node.description}
                      category={node.category}
                      isUserNode={true}
                      onEdit={() => handleOpenEditModal(node)}
                      onDelete={() => handleOpenDeleteDialog(node)}
                    />
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
                  <p>Você ainda não criou nenhum node personalizado.</p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => setNodeFormOpen(true)}
                    aria-label="Criar primeiro node"
                  >
                    <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
                    Criar Primeiro Node
                  </Button>
                </div>
              )}
            </div>
          </TabsContent>
        </div>
      </Tabs>

      {/* Node creation/editing form */}
      <NodeForm
        open={nodeFormOpen}
        onOpenChange={handleCloseModal}
        onSubmit={editingNode ? handleEditNode : handleCreateNode}
        initialData={
          editingNode
            ? {
                name: editingNode.name,
                description: editingNode.description,
                category: editingNode.category,
                config: editingNode.config || "",
              }
            : undefined
        }
        initialCategory={selectedCategory || undefined}
        isEditing={!!editingNode}
        nodeCategories={Object.values(NODE_CATEGORIES)}
      />

      {/* Delete confirmation dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir Node</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja excluir o node "{nodeToDelete?.name}"? Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmDelete} className="bg-destructive text-destructive-foreground">
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
