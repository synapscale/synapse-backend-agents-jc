"use client"

import { create } from "zustand"
import { persist } from "zustand/middleware"

/**
 * Node categories supported by the application
 */
export type NodeCategory = "ai" | "app-action" | "data-transformation" | "flow" | "core" | "human" | "trigger"

/**
 * Node interface representing a node in the application
 */
export interface Node {
  id: string
  name: string
  description: string
  category: NodeCategory
  config?: string
  createdAt: string | Date
  updatedAt: string | Date
}

/**
 * Node state interface for Zustand store
 */
interface NodeState {
  nodes: Node[]
  addNode: (node: Omit<Node, "id" | "createdAt" | "updatedAt">) => string
  updateNode: (id: string, node: Partial<Omit<Node, "id" | "createdAt" | "updatedAt">>) => void
  deleteNode: (id: string) => void
  getNodeById: (id: string) => Node | undefined
}

/**
 * useNodes hook for managing nodes state
 *
 * Provides functions to add, update, delete, and retrieve nodes.
 * Uses Zustand for state management and persistence.
 */
export const useNodes = create<NodeState>()(
  persist(
    (set, get) => ({
      nodes: [],

      /**
       * Add a new node to the state
       * @param node - The node data to add (without id, createdAt, and updatedAt)
       * @returns The ID of the newly created node
       */
      addNode: (node) => {
        const id = crypto.randomUUID()
        const timestamp = new Date().toISOString()

        set((state) => ({
          nodes: [
            ...state.nodes,
            {
              ...node,
              id,
              createdAt: timestamp,
              updatedAt: timestamp,
            },
          ],
        }))

        return id
      },

      /**
       * Update an existing node in the state
       * @param id - The ID of the node to update
       * @param node - The partial node data to update
       */
      updateNode: (id, node) =>
        set((state) => ({
          nodes: state.nodes.map((n) =>
            n.id === id
              ? {
                  ...n,
                  ...node,
                  updatedAt: new Date().toISOString(),
                }
              : n,
          ),
        })),

      /**
       * Delete a node from the state
       * @param id - The ID of the node to delete
       */
      deleteNode: (id) =>
        set((state) => ({
          nodes: state.nodes.filter((n) => n.id !== id),
        })),

      /**
       * Get a node by its ID
       * @param id - The ID of the node to retrieve
       * @returns The node if found, undefined otherwise
       */
      getNodeById: (id) => get().nodes.find((node) => node.id === id),
    }),
    {
      name: "nodes-storage",
      serialize: (state) => JSON.stringify(state),
      deserialize: (str) => {
        const parsedState = JSON.parse(str)
        return parsedState
      },
    },
  ),
)
