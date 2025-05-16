"use client"

import type React from "react"

import { useState, useRef, useEffect, useCallback } from "react"
import { X, ChevronUp, ChevronDown } from "lucide-react"
import { useNodeOperations } from "@/hooks"
import { useTheme } from "@/contexts/theme-context"
import type { CanvasNode as CanvasNodeType } from "@/contexts/canvas-context"
import { NodePort } from "./node-port"

interface CanvasNodeProps {
  node: CanvasNodeType
  isSelected?: boolean
  onClick?: (event: React.MouseEvent) => void
}

/**
 * CanvasNode Component
 *
 * Represents a node on the canvas that can be dragged, selected, and connected.
 *
 * @param node - The node data
 * @param isSelected - Whether the node is currently selected
 * @param onClick - Function to call when the node is clicked
 */
export function CanvasNode({ node, isSelected = false, onClick }: CanvasNodeProps) {
  // State for whether the node content is expanded or collapsed
  const [isExpanded, setIsExpanded] = useState(true)

  // State for whether the node is being dragged
  const [isDragging, setIsDragging] = useState(false)

  // Reference to the node DOM element
  const nodeRef = useRef<HTMLDivElement>(null)

  // Reference to the initial mouse position during drag
  const dragStartRef = useRef<{ x: number; y: number } | null>(null)

  // Node operations from custom hook
  const { removeNode, moveNode, getNodeTheme } = useNodeOperations()

  // Current theme
  const { currentTheme } = useTheme()

  // Get theme colors for the node category
  const nodeTheme = getNodeTheme(node.data.category)

  /**
   * Handle the start of node dragging
   */
  const handleDragStart = useCallback((e: React.MouseEvent) => {
    // Prevent default browser drag behavior
    e.preventDefault()
    e.stopPropagation()

    // Mark the node as being dragged
    setIsDragging(true)

    // Store the initial mouse position
    dragStartRef.current = { x: e.clientX, y: e.clientY }

    // Add event listeners for drag movement and end
    document.addEventListener("mousemove", handleDragMove)
    document.addEventListener("mouseup", handleDragEnd)
  }, [])

  /**
   * Handle node movement during drag
   */
  const handleDragMove = useCallback(
    (e: MouseEvent) => {
      // If not dragging or no initial position, do nothing
      if (!isDragging || !dragStartRef.current) return

      // Calculate the mouse displacement since drag start
      const dx = e.clientX - dragStartRef.current.x
      const dy = e.clientY - dragStartRef.current.y

      // Update the node position in the global state
      moveNode(node.id, {
        x: node.position.x + dx,
        y: node.position.y + dy,
      })

      // Update the initial position for the next movement
      dragStartRef.current = { x: e.clientX, y: e.clientY }
    },
    [isDragging, moveNode, node],
  )

  /**
   * Handle the end of node dragging
   */
  const handleDragEnd = useCallback(() => {
    // Mark the node as no longer being dragged
    setIsDragging(false)

    // Clear the initial drag position
    dragStartRef.current = null

    // Remove the event listeners
    document.removeEventListener("mousemove", handleDragMove)
    document.removeEventListener("mouseup", handleDragEnd)
  }, [handleDragMove])

  /**
   * Handle node removal
   */
  const handleRemove = useCallback(
    (e: React.MouseEvent) => {
      // Prevent the event from propagating to the node's onClick
      e.stopPropagation()

      // Remove the node from the canvas
      removeNode(node.id)
    },
    [removeNode, node.id],
  )

  /**
   * Handle toggling node expansion/collapse
   */
  const handleToggleExpand = useCallback((e: React.MouseEvent) => {
    // Prevent the event from propagating to the node's onClick
    e.stopPropagation()

    // Toggle the expansion state
    setIsExpanded((prev) => !prev)
  }, [])

  // Clean up event listeners when component unmounts
  useEffect(() => {
    return () => {
      document.removeEventListener("mousemove", handleDragMove)
      document.removeEventListener("mouseup", handleDragEnd)
    }
  }, [handleDragMove, handleDragEnd])

  // Get the node's input and output ports
  const inputPorts = node.ports?.inputs || []
  const outputPorts = node.ports?.outputs || []

  // Dynamic styles based on theme and node state
  const nodeStyle = {
    left: `${node.position.x}px`,
    top: `${node.position.y}px`,
    borderRadius: currentTheme.nodeStyle.borderRadius,
    boxShadow: isSelected ? "0 0 0 2px #3b82f6" : currentTheme.nodeStyle.shadowSize,
  }

  return (
    <div
      ref={nodeRef}
      className={`absolute ${nodeTheme.background} ${nodeTheme.border} border ${
        isSelected ? "z-10" : "z-0"
      } w-64 select-none`}
      style={nodeStyle}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`Node: ${node.data.name}`}
      aria-selected={isSelected}
    >
      {/* Node header */}
      <div
        className={`${nodeTheme.headerBg} ${nodeTheme.text} p-2 cursor-move flex justify-between items-center`}
        onMouseDown={handleDragStart}
        role="region"
        aria-label="Node header"
      >
        <div className="font-medium truncate" title={node.data.name}>
          {node.data.name}
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={handleToggleExpand}
            className="p-1 hover:bg-black/10 rounded"
            aria-label={isExpanded ? "Colapsar nó" : "Expandir nó"}
          >
            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          <button onClick={handleRemove} className="p-1 hover:bg-black/10 rounded" aria-label="Remover nó">
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Node content (visible only if expanded) */}
      {isExpanded && (
        <div className="p-2">
          {/* Node description */}
          <div className={`${nodeTheme.text} text-xs mb-3`} title={node.data.description}>
            {node.data.description}
          </div>

          {/* Input ports */}
          {inputPorts.length > 0 && (
            <div className="mb-2">
              <div className={`${nodeTheme.text} text-xs font-medium mb-1`}>Entradas</div>
              <div className="space-y-1">
                {inputPorts.map((port) => (
                  <NodePort
                    key={port.id}
                    nodeId={node.id}
                    port={{
                      id: port.id,
                      type: "input",
                      connections: port.connections,
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Output ports */}
          {outputPorts.length > 0 && (
            <div>
              <div className={`${nodeTheme.text} text-xs font-medium mb-1`}>Saídas</div>
              <div className="space-y-1">
                {outputPorts.map((port) => (
                  <NodePort
                    key={port.id}
                    nodeId={node.id}
                    port={{
                      id: port.id,
                      type: "output",
                      connections: port.connections,
                    }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
