"use client"

import { useCallback } from "react"
import { useCanvas } from "@/contexts/canvas-context"
import { useTheme } from "@/contexts/theme-context"
import type { NodeCategory } from "@/hooks/use-nodes"

/**
 * useNodeOperations Hook
 *
 * Custom hook that provides common operations for nodes on the canvas.
 *
 * @returns Object with node operation functions
 */
export function useNodeOperations() {
  const { removeCanvasNode, moveCanvasNode, updateCanvasNode, addConnection, removeConnection } = useCanvas()

  const { currentTheme } = useTheme()

  /**
   * Remove a node from the canvas
   * @param nodeId - ID of the node to remove
   */
  const removeNode = useCallback(
    (nodeId: string) => {
      removeCanvasNode(nodeId)
    },
    [removeCanvasNode],
  )

  /**
   * Move a node on the canvas
   * @param nodeId - ID of the node to move
   * @param position - New position for the node
   */
  const moveNode = useCallback(
    (nodeId: string, position: { x: number; y: number }) => {
      moveCanvasNode(nodeId, position)
    },
    [moveCanvasNode],
  )

  /**
   * Update a node's data
   * @param nodeId - ID of the node to update
   * @param data - New data for the node
   */
  const updateNode = useCallback(
    (nodeId: string, data: any) => {
      updateCanvasNode(nodeId, data)
    },
    [updateCanvasNode],
  )

  /**
   * Connect two nodes
   * @param sourceNodeId - ID of the source node
   * @param sourcePortId - ID of the source port
   * @param targetNodeId - ID of the target node
   * @param targetPortId - ID of the target port
   */
  const connectNodes = useCallback(
    (sourceNodeId: string, sourcePortId: string, targetNodeId: string, targetPortId: string) => {
      addConnection(sourceNodeId, sourcePortId, targetNodeId, targetPortId)
    },
    [addConnection],
  )

  /**
   * Disconnect two nodes
   * @param connectionId - ID of the connection to remove
   */
  const disconnectNodes = useCallback(
    (connectionId: string) => {
      removeConnection(connectionId)
    },
    [removeConnection],
  )

  /**
   * Get theme colors for a node category
   * @param category - Node category
   * @returns Theme colors for the category
   */
  const getNodeTheme = useCallback(
    (category: NodeCategory) => {
      return currentTheme.nodeColors[category] || currentTheme.nodeColors.core
    },
    [currentTheme],
  )

  return {
    removeNode,
    moveNode,
    updateNode,
    connectNodes,
    disconnectNodes,
    getNodeTheme,
  }
}

