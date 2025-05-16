"use client"

import type React from "react"

import { useState, useRef, useEffect, useCallback } from "react"
import { useCanvas } from "@/contexts/canvas-context"
import { useTheme } from "@/contexts/theme-context"
import { CanvasNode } from "@/components/canvas/canvas-node"
import { ConnectionLine } from "@/components/canvas/connection-line"
import { NodeDetailsPanel } from "@/components/canvas/node-details-panel"
import { CanvasToolbar } from "@/components/canvas/canvas-toolbar"
import { cn } from "@/lib/utils"

/**
 * CanvasArea Component
 *
 * Main area where nodes are displayed and can be connected.
 * Handles drag and drop of nodes from the sidebar.
 */
export function CanvasArea() {
  const {
    canvasNodes,
    connections,
    addCanvasNode,
    selectedNode,
    setSelectedNode,
    selectedConnection,
    setSelectedConnection,
  } = useCanvas()

  const { currentTheme } = useTheme()
  const canvasRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const [isDraggingOver, setIsDraggingOver] = useState(false)
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 })

  // Update canvas size when window is resized
  useEffect(() => {
    const updateCanvasSize = () => {
      if (canvasRef.current) {
        setCanvasSize({
          width: canvasRef.current.clientWidth,
          height: canvasRef.current.clientHeight,
        })
      }
    }

    updateCanvasSize()

    const resizeObserver = new ResizeObserver(updateCanvasSize)
    if (canvasRef.current) {
      resizeObserver.observe(canvasRef.current)
    }

    return () => {
      resizeObserver.disconnect()
    }
  }, [])

  /**
   * Handle drag over event
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDraggingOver(true)
  }, [])

  /**
   * Handle drag leave event
   */
  const handleDragLeave = useCallback(() => {
    setIsDraggingOver(false)
  }, [])

  /**
   * Handle drop event
   */
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDraggingOver(false)

      try {
        const data = JSON.parse(e.dataTransfer.getData("application/json"))

        if (data.type === "node" && data.id) {
          // Calculate position relative to canvas
          const canvasRect = canvasRef.current?.getBoundingClientRect()
          if (canvasRect) {
            const x = e.clientX - canvasRect.left
            const y = e.clientY - canvasRect.top

            // Get node from global storage
            const nodeData = JSON.parse(localStorage.getItem("nodes-storage") || "{}")
            const nodes = nodeData.state?.nodes || []
            const node = nodes.find((n: any) => n.id === data.id)

            if (node) {
              addCanvasNode(node, { x, y })
            }
          }
        }
      } catch (error) {
        console.error("Error processing drop:", error)
      }
    },
    [addCanvasNode],
  )

  /**
   * Handle canvas click event
   */
  const handleCanvasClick = useCallback(() => {
    setSelectedNode(null)
    setSelectedConnection(null)
  }, [setSelectedNode, setSelectedConnection])

  return (
    <div className="flex-1 h-full">
      <div className="flex h-full">
        <div
          id="canvas-area"
          ref={canvasRef}
          className={cn(
            "flex-1 h-full overflow-auto relative",
            currentTheme.canvasBg,
            isDraggingOver ? "bg-opacity-70" : "",
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleCanvasClick}
          aria-label="Canvas Area"
          role="region"
        >
          <CanvasToolbar />

          {/* SVG for rendering connections */}
          <svg
            ref={svgRef}
            className="absolute inset-0 pointer-events-none z-0"
            width={canvasSize.width}
            height={canvasSize.height}
            aria-hidden="true"
          >
            {connections.map((connection) => (
              <ConnectionLine
                key={connection.id}
                connection={connection}
                isSelected={selectedConnection === connection.id}
              />
            ))}
          </svg>

          <div className="absolute inset-0 p-4">
            {canvasNodes.map((node) => (
              <CanvasNode
                key={node.id}
                node={node}
                isSelected={selectedNode === node.id}
                onClick={() => setSelectedNode(node.id === selectedNode ? null : node.id)}
              />
            ))}

            {canvasNodes.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <h2 className="text-xl font-semibold mb-2">Canvas Vazio</h2>
                  <p className="text-muted-foreground">
                    Arraste e solte nodes da sidebar para começar a construir seu fluxo.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {selectedNode && <NodeDetailsPanel nodeId={selectedNode} />}
      </div>
    </div>
  )
}
