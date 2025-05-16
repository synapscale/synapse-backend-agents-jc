"use client"

import { createContext, useContext, useState, useEffect, useCallback, useRef, useMemo, type ReactNode } from "react"
import { type Node, useNodes } from "@/hooks/use-nodes"
import { getNodeTypeById, type NodeTypeDefinition } from "@/types/node-types"

/**
 * Canvas Node representation
 */
export type CanvasNode = {
  id: string
  type: string
  position: { x: number; y: number }
  data: Node
  ports?: {
    inputs: Array<{ id: string; connections: string[] }>
    outputs: Array<{ id: string; connections: string[] }>
  }
}

/**
 * Connection between nodes
 */
export type Connection = {
  id: string
  sourceNodeId: string
  sourcePortId: string
  targetNodeId: string
  targetPortId: string
  selected?: boolean
}

/**
 * Types of actions that can be performed on the canvas
 */
type ActionType = "ADD_NODE" | "REMOVE_NODE" | "MOVE_NODE" | "UPDATE_NODE" | "ADD_CONNECTION" | "REMOVE_CONNECTION"

/**
 * History action for undo/redo functionality
 */
interface HistoryAction {
  type: ActionType
  payload: any
  undo: () => void
  redo: () => void
}

/**
 * Canvas context type definition
 */
type CanvasContextType = {
  canvasNodes: CanvasNode[]
  connections: Connection[]
  addCanvasNode: (node: Node, position: { x: number; y: number }) => void
  updateCanvasNode: (id: string, data: Partial<Node>) => void
  removeCanvasNode: (id: string) => void
  moveCanvasNode: (id: string, position: { x: number; y: number }) => void
  selectedNode: string | null
  setSelectedNode: (id: string | null) => void
  selectedConnection: string | null
  setSelectedConnection: (id: string | null) => void
  addConnection: (sourceNodeId: string, sourcePortId: string, targetNodeId: string, targetPortId: string) => void
  removeConnection: (connectionId: string) => void
  getNodeConnections: (nodeId: string) => Connection[]
  undo: () => void
  redo: () => void
  canUndo: boolean
  canRedo: boolean
  getNodeType: (nodeId: string) => NodeTypeDefinition | undefined
}

// Create the canvas context
const CanvasContext = createContext<CanvasContextType | undefined>(undefined)

/**
 * CanvasProvider Component
 *
 * Provides canvas context to the application, managing canvas state and operations.
 *
 * @param children - React children to be wrapped by the provider
 */
export function CanvasProvider({ children }: { children: ReactNode }) {
  const [canvasNodes, setCanvasNodes] = useState<CanvasNode[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [selectedConnection, setSelectedConnection] = useState<string | null>(null)
  const { updateNode } = useNodes()

  // History state for undo/redo
  const [history, setHistory] = useState<HistoryAction[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const isPerformingAction = useRef(false)

  // Check if we can undo/redo
  const canUndo = historyIndex >= 0
  const canRedo = historyIndex < history.length - 1

  // Load nodes from localStorage on mount
  useEffect(() => {
    try {
      const savedNodes = localStorage.getItem("canvas-nodes")
      if (savedNodes) {
        setCanvasNodes(JSON.parse(savedNodes))
      }

      const savedConnections = localStorage.getItem("canvas-connections")
      if (savedConnections) {
        setConnections(JSON.parse(savedConnections))
      }
    } catch (error) {
      console.error("Error loading canvas data:", error)
    }
  }, [])

  // Save nodes to localStorage when they change
  useEffect(() => {
    if (!isPerformingAction.current) {
      try {
        localStorage.setItem("canvas-nodes", JSON.stringify(canvasNodes))
        localStorage.setItem("canvas-connections", JSON.stringify(connections))
      } catch (error) {
        console.error("Error saving canvas data:", error)
      }
    }
  }, [canvasNodes, connections])

  /**
   * Add an action to the history
   */
  const addToHistory = useCallback(
    (action: HistoryAction) => {
      setHistory((prev) => {
        // If we're in the middle of the history, remove all future actions
        const newHistory = prev.slice(0, historyIndex + 1)
        return [...newHistory, action]
      })
      setHistoryIndex((prev) => prev + 1)
    },
    [historyIndex],
  )

  /**
   * Undo the last action
   */
  const undo = useCallback(() => {
    if (historyIndex >= 0) {
      isPerformingAction.current = true
      const action = history[historyIndex]
      action.undo()
      setHistoryIndex((prev) => prev - 1)
      isPerformingAction.current = false
    }
  }, [history, historyIndex])

  /**
   * Redo the last undone action
   */
  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      isPerformingAction.current = true
      const action = history[historyIndex + 1]
      action.redo()
      setHistoryIndex((prev) => prev + 1)
      isPerformingAction.current = false
    }
  }, [history, historyIndex])

  /**
   * Add a node to the canvas
   */
  const addCanvasNode = useCallback(
    (node: Node, position: { x: number; y: number }) => {
      const nodeType = getNodeTypeById(node.category)

      const newCanvasNode: CanvasNode = {
        id: `canvas-${node.id}-${Date.now()}`,
        type: node.category,
        position,
        data: node,
        ports: nodeType
          ? {
              inputs: nodeType.inputs.map((input) => ({ id: input.id, connections: [] })),
              outputs: nodeType.outputs.map((output) => ({ id: output.id, connections: [] })),
            }
          : undefined,
      }

      setCanvasNodes((prev) => [...prev, newCanvasNode])

      // Add to history
      addToHistory({
        type: "ADD_NODE",
        payload: { node: newCanvasNode },
        undo: () => {
          setCanvasNodes((prev) => prev.filter((n) => n.id !== newCanvasNode.id))
          // Remove associated connections
          setConnections((prev) =>
            prev.filter((conn) => conn.sourceNodeId !== newCanvasNode.id && conn.targetNodeId !== newCanvasNode.id),
          )
          if (selectedNode === newCanvasNode.id) {
            setSelectedNode(null)
          }
        },
        redo: () => {
          setCanvasNodes((prev) => [...prev, newCanvasNode])
        },
      })
    },
    [addToHistory, selectedNode],
  )

  /**
   * Update a node on the canvas
   */
  const updateCanvasNode = useCallback(
    (id: string, data: Partial<Node>) => {
      let oldData: Partial<Node> = {}
      let nodeToUpdate: CanvasNode | undefined

      setCanvasNodes((prev) => {
        return prev.map((node) => {
          if (node.id === id) {
            nodeToUpdate = node
            oldData = { ...node.data }
            const updatedData = { ...node.data, ...data }

            // Also update in the global node storage
            if (node.data.id) {
              updateNode(node.data.id, data)
            }

            return { ...node, data: updatedData }
          }
          return node
        })
      })

      if (nodeToUpdate) {
        // Add to history
        addToHistory({
          type: "UPDATE_NODE",
          payload: { id, newData: data, oldData },
          undo: () => {
            setCanvasNodes((prev) =>
              prev.map((node) => (node.id === id ? { ...node, data: { ...node.data, ...oldData } } : node)),
            )
            if (nodeToUpdate?.data.id) {
              updateNode(nodeToUpdate.data.id, oldData)
            }
          },
          redo: () => {
            setCanvasNodes((prev) =>
              prev.map((node) => (node.id === id ? { ...node, data: { ...node.data, ...data } } : node)),
            )
            if (nodeToUpdate?.data.id) {
              updateNode(nodeToUpdate.data.id, data)
            }
          },
        })
      }
    },
    [addToHistory, updateNode],
  )

  /**
   * Move a node on the canvas
   */
  const moveCanvasNode = useCallback(
    (id: string, position: { x: number; y: number }) => {
      let oldPosition = { x: 0, y: 0 }

      setCanvasNodes((prev) => {
        return prev.map((node) => {
          if (node.id === id) {
            oldPosition = { ...node.position }
            return { ...node, position }
          }
          return node
        })
      })

      // Add to history
      addToHistory({
        type: "MOVE_NODE",
        payload: { id, newPosition: position, oldPosition },
        undo: () => {
          setCanvasNodes((prev) => prev.map((node) => (node.id === id ? { ...node, position: oldPosition } : node)))
        },
        redo: () => {
          setCanvasNodes((prev) => prev.map((node) => (node.id === id ? { ...node, position } : node)))
        },
      })
    },
    [addToHistory],
  )

  /**
   * Remove a node from the canvas
   */
  const removeCanvasNode = useCallback(
    (id: string) => {
      let removedNode: CanvasNode | undefined
      let affectedConnections: Connection[] = []

      // Find connections associated with this node
      affectedConnections = connections.filter((conn) => conn.sourceNodeId === id || conn.targetNodeId === id)

      setCanvasNodes((prev) => {
        removedNode = prev.find((node) => node.id === id)
        return prev.filter((node) => node.id !== id)
      })

      // Remove associated connections
      if (affectedConnections.length > 0) {
        setConnections((prev) => prev.filter((conn) => conn.sourceNodeId !== id && conn.targetNodeId !== id))
      }

      if (selectedNode === id) {
        setSelectedNode(null)
      }

      if (removedNode) {
        // Add to history
        addToHistory({
          type: "REMOVE_NODE",
          payload: { node: removedNode, connections: affectedConnections },
          undo: () => {
            setCanvasNodes((prev) => [...prev, removedNode!])
            if (affectedConnections.length > 0) {
              setConnections((prev) => [...prev, ...affectedConnections])
            }
          },
          redo: () => {
            setCanvasNodes((prev) => prev.filter((node) => node.id !== id))
            if (affectedConnections.length > 0) {
              setConnections((prev) => prev.filter((conn) => conn.sourceNodeId !== id && conn.targetNodeId !== id))
            }
            if (selectedNode === id) {
              setSelectedNode(null)
            }
          },
        })
      }
    },
    [addToHistory, selectedNode, connections],
  )

  /**
   * Add a connection between nodes
   */
  const addConnection = useCallback(
    (sourceNodeId: string, sourcePortId: string, targetNodeId: string, targetPortId: string) => {
      // Check if the connection already exists
      const connectionExists = connections.some(
        (conn) =>
          conn.sourceNodeId === sourceNodeId &&
          conn.sourcePortId === sourcePortId &&
          conn.targetNodeId === targetNodeId &&
          conn.targetPortId === targetPortId,
      )

      if (connectionExists) return

      const newConnection: Connection = {
        id: `conn-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        sourceNodeId,
        sourcePortId,
        targetNodeId,
        targetPortId,
      }

      setConnections((prev) => [...prev, newConnection])

      // Update the ports of the nodes
      setCanvasNodes((prev) =>
        prev.map((node) => {
          if (node.id === sourceNodeId && node.ports) {
            return {
              ...node,
              ports: {
                ...node.ports,
                outputs: node.ports.outputs.map((output) =>
                  output.id === sourcePortId
                    ? { ...output, connections: [...output.connections, newConnection.id] }
                    : output,
                ),
              },
            }
          }
          if (node.id === targetNodeId && node.ports) {
            return {
              ...node,
              ports: {
                ...node.ports,
                inputs: node.ports.inputs.map((input) =>
                  input.id === targetPortId
                    ? { ...input, connections: [...input.connections, newConnection.id] }
                    : input,
                ),
              },
            }
          }
          return node
        }),
      )

      // Add to history
      addToHistory({
        type: "ADD_CONNECTION",
        payload: { connection: newConnection },
        undo: () => {
          setConnections((prev) => prev.filter((conn) => conn.id !== newConnection.id))

          // Update the ports of the nodes
          setCanvasNodes((prev) =>
            prev.map((node) => {
              if (node.id === sourceNodeId && node.ports) {
                return {
                  ...node,
                  ports: {
                    ...node.ports,
                    outputs: node.ports.outputs.map((output) =>
                      output.id === sourcePortId
                        ? { ...output, connections: output.connections.filter((id) => id !== newConnection.id) }
                        : output,
                    ),
                  },
                }
              }
              if (node.id === targetNodeId && node.ports) {
                return {
                  ...node,
                  ports: {
                    ...node.ports,
                    inputs: node.ports.inputs.map((input) =>
                      input.id === targetPortId
                        ? { ...input, connections: input.connections.filter((id) => id !== newConnection.id) }
                        : input,
                    ),
                  },
                }
              }
              return node
            }),
          )

          if (selectedConnection === newConnection.id) {
            setSelectedConnection(null)
          }
        },
        redo: () => {
          setConnections((prev) => [...prev, newConnection])

          // Update the ports of the nodes
          setCanvasNodes((prev) =>
            prev.map((node) => {
              if (node.id === sourceNodeId && node.ports) {
                return {
                  ...node,
                  ports: {
                    ...node.ports,
                    outputs: node.ports.outputs.map((output) =>
                      output.id === sourcePortId
                        ? { ...output, connections: [...output.connections, newConnection.id] }
                        : output,
                    ),
                  },
                }
              }
              if (node.id === targetNodeId && node.ports) {
                return {
                  ...node,
                  ports: {
                    ...node.ports,
                    inputs: node.ports.inputs.map((input) =>
                      input.id === targetPortId
                        ? { ...input, connections: [...input.connections, newConnection.id] }
                        : input,
                    ),
                  },
                }
              }
              return node
            }),
          )
        },
      })
    },
    [connections, addToHistory, selectedConnection],
  )

  /**
   * Remove a connection
   */
  const removeConnection = useCallback(
    (connectionId: string) => {
      const connectionToRemove = connections.find((conn) => conn.id === connectionId)

      if (!connectionToRemove) return

      setConnections((prev) => prev.filter((conn) => conn.id !== connectionId))

      // Update the ports of the nodes
      setCanvasNodes((prev) =>
        prev.map((node) => {
          if (node.id === connectionToRemove.sourceNodeId && node.ports) {
            return {
              ...node,
              ports: {
                ...node.ports,
                outputs: node.ports.outputs.map((output) =>
                  output.id === connectionToRemove.sourcePortId
                    ? { ...output, connections: output.connections.filter((id) => id !== connectionId) }
                    : output,
                ),
              },
            }
          }
          if (node.id === connectionToRemove.targetNodeId && node.ports) {
            return {
              ...node,
              ports: {
                ...node.ports,
                inputs: node.ports.inputs.map((input) =>
                  input.id === connectionToRemove.targetPortId
                    ? { ...input, connections: input.connections.filter((id) => id !== connectionId) }
                    : input,
                ),
              },
            }
          }
          return node
        }),
      )

      if (selectedConnection === connectionId) {
        setSelectedConnection(null)
      }

      // Add to history
      addToHistory({
        type: "REMOVE_CONNECTION",
        payload: { connection: connectionToRemove },
        undo: () => {
          setConnections((prev) => [...prev, connectionToRemove])

          // Update the ports of the nodes
          setCanvasNodes((prev) =>
            prev.map((node) => {
              if (node.id === connectionToRemove.sourceNodeId && node.ports) {
                return {
                  ...node,
                  ports: {
                    ...node.ports,
                    outputs: node.ports.outputs.map((output) =>
                      output.id === connectionToRemove.sourcePortId
                        ? { ...output, connections: [...output.connections, connectionId] }
                        : output,
                    ),
                  },
                }
              }
              if (node.id === connectionToRemove.targetNodeId && node.ports) {
                return {
                  ...node,
                  ports: {
                    ...node.ports,
                    inputs: node.ports.inputs.map((input) =>
                      input.id === connectionToRemove.targetPortId
                        ? { ...input, connections: [...input.connections, connectionId] }
                        : input,
                    ),
                  },
                }
              }
              return node
            }),
          )
        },
        redo: () => {
          setConnections((prev) => prev.filter((conn) => conn.id !== connectionId))

          // Update the ports of the nodes
          setCanvasNodes((prev) =>
            prev.map((node) => {
              if (node.id === connectionToRemove.sourceNodeId && node.ports) {
                return {
                  ...node,
                  ports: {
                    ...node.ports,
                    outputs: node.ports.outputs.map((output) =>
                      output.id === connectionToRemove.sourcePortId
                        ? { ...output, connections: output.connections.filter((id) => id !== connectionId) }
                        : output,
                    ),
                  },
                }
              }
              if (node.id === connectionToRemove.targetNodeId && node.ports) {
                return {
                  ...node,
                  ports: {
                    ...node.ports,
                    inputs: node.ports.inputs.map((input) =>
                      input.id === connectionToRemove.targetPortId
                        ? { ...input, connections: input.connections.filter((id) => id !== connectionId) }
                        : input,
                    ),
                  },
                }
              }
              return node
            }),
          )

          if (selectedConnection === connectionId) {
            setSelectedConnection(null)
          }
        },
      })
    },
    [connections, addToHistory, selectedConnection],
  )

  /**
   * Get connections for a node
   */
  const getNodeConnections = useCallback(
    (nodeId: string) => {
      return connections.filter((conn) => conn.sourceNodeId === nodeId || conn.targetNodeId === nodeId)
    },
    [connections],
  )

  /**
   * Get the type definition for a node
   */
  const getNodeType = useCallback(
    (nodeId: string) => {
      const node = canvasNodes.find((n) => n.id === nodeId)
      if (!node) return undefined

      return getNodeTypeById(node.type)
    },
    [canvasNodes],
  )

  // Add keyboard shortcuts for undo/redo
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+Z for undo
      if ((e.ctrlKey || e.metaKey) && e.key === "z" && !e.shiftKey) {
        e.preventDefault()
        undo()
      }

      // Ctrl+Y or Ctrl+Shift+Z for redo
      if ((e.ctrlKey || e.metaKey) && (e.key === "y" || (e.key === "z" && e.shiftKey))) {
        e.preventDefault()
        redo()
      }

      // Delete to remove selected node or connection
      if (e.key === "Delete" || e.key === "Backspace") {
        if (selectedNode) {
          e.preventDefault()
          removeCanvasNode(selectedNode)
        } else if (selectedConnection) {
          e.preventDefault()
          removeConnection(selectedConnection)
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [undo, redo, selectedNode, selectedConnection, removeCanvasNode, removeConnection])

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(
    () => ({
      canvasNodes,
      connections,
      addCanvasNode,
      updateCanvasNode,
      removeCanvasNode,
      moveCanvasNode,
      selectedNode,
      setSelectedNode,
      selectedConnection,
      setSelectedConnection,
      addConnection,
      removeConnection,
      getNodeConnections,
      undo,
      redo,
      canUndo,
      canRedo,
      getNodeType,
    }),
    [
      canvasNodes,
      connections,
      addCanvasNode,
      updateCanvasNode,
      removeCanvasNode,
      moveCanvasNode,
      selectedNode,
      setSelectedNode,
      selectedConnection,
      setSelectedConnection,
      addConnection,
      removeConnection,
      getNodeConnections,
      undo,
      redo,
      canUndo,
      canRedo,
      getNodeType,
    ],
  )

  return <CanvasContext.Provider value={contextValue}>{children}</CanvasContext.Provider>
}

/**
 * useCanvas Hook
 *
 * Custom hook to access the canvas context.
 *
 * @returns The canvas context value
 * @throws Error if used outside of a CanvasProvider
 */
export function useCanvas() {
  const context = useContext(CanvasContext)

  if (context === undefined) {
    throw new Error("useCanvas must be used within a CanvasProvider")
  }

  return context
}
