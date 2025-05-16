"use client"

import type React from "react"

import { useEffect, useState, useCallback } from "react"
import { useCanvas } from "@/contexts/canvas-context"
import type { Connection } from "@/contexts/canvas-context"

interface ConnectionLineProps {
  connection: Connection
  isSelected?: boolean
}

/**
 * ConnectionLine Component
 *
 * Renders a bezier curve between two ports on the canvas.
 *
 * @param connection - The connection data
 * @param isSelected - Whether the connection is selected
 */
export function ConnectionLine({ connection, isSelected = false }: ConnectionLineProps) {
  const { canvasNodes, setSelectedConnection } = useCanvas()
  const [path, setPath] = useState<string>("")
  const [sourcePos, setSourcePos] = useState<{ x: number; y: number } | null>(null)
  const [targetPos, setTargetPos] = useState<{ x: number; y: number } | null>(null)

  /**
   * Calculate the positions of the source and target ports
   */
  const calculatePositions = useCallback(() => {
    // Find the source and target nodes
    const sourceNode = canvasNodes.find((node) => node.id === connection.sourceNodeId)
    const targetNode = canvasNodes.find((node) => node.id === connection.targetNodeId)

    if (!sourceNode || !targetNode) return

    // Find the source and target port elements
    const sourcePortElement = document.querySelector(
      `[data-node-id="${connection.sourceNodeId}"][data-port-id="${connection.sourcePortId}"]`,
    ) as HTMLElement

    const targetPortElement = document.querySelector(
      `[data-node-id="${connection.targetNodeId}"][data-port-id="${connection.targetPortId}"]`,
    ) as HTMLElement

    if (!sourcePortElement || !targetPortElement) return

    // Get the positions of the ports
    const sourceRect = sourcePortElement.getBoundingClientRect()
    const targetRect = targetPortElement.getBoundingClientRect()

    // Get the canvas element
    const canvasElement = document.getElementById("canvas-area")
    if (!canvasElement) return

    const canvasRect = canvasElement.getBoundingClientRect()

    // Calculate the positions relative to the canvas
    const sourceX = sourceRect.left + sourceRect.width / 2 - canvasRect.left + canvasElement.scrollLeft
    const sourceY = sourceRect.top + sourceRect.height / 2 - canvasRect.top + canvasElement.scrollTop
    const targetX = targetRect.left + targetRect.width / 2 - canvasRect.left + canvasElement.scrollLeft
    const targetY = targetRect.top + targetRect.height / 2 - canvasRect.top + canvasElement.scrollTop

    setSourcePos({ x: sourceX, y: sourceY })
    setTargetPos({ x: targetX, y: targetY })

    // Calculate the control points for the bezier curve
    const dx = Math.abs(targetX - sourceX)
    const controlPointOffset = Math.min(dx * 0.5, 150)

    // Create the path for the bezier curve
    const path = `M ${sourceX} ${sourceY} C ${sourceX + controlPointOffset} ${sourceY}, ${
      targetX - controlPointOffset
    } ${targetY}, ${targetX} ${targetY}`

    setPath(path)
  }, [canvasNodes, connection])

  // Calculate positions when component mounts or when nodes or connection change
  useEffect(() => {
    calculatePositions()

    // Recalculate positions when window is resized
    window.addEventListener("resize", calculatePositions)

    // Recalculate positions when canvas is scrolled
    const canvasElement = document.getElementById("canvas-area")
    if (canvasElement) {
      canvasElement.addEventListener("scroll", calculatePositions)
    }

    return () => {
      window.removeEventListener("resize", calculatePositions)
      if (canvasElement) {
        canvasElement.removeEventListener("scroll", calculatePositions)
      }
    }
  }, [calculatePositions])

  // If we don't have positions yet, don't render anything
  if (!sourcePos || !targetPos) return null

  /**
   * Handle click on the connection
   */
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    setSelectedConnection(connection.id)
  }

  return (
    <g onClick={handleClick}>
      <path
        d={path}
        fill="none"
        stroke={isSelected ? "#3b82f6" : "#64748b"}
        strokeWidth={isSelected ? 3 : 2}
        strokeDasharray={isSelected ? "5,5" : "none"}
        className="transition-colors duration-200"
      />
      {/* Source point */}
      <circle
        cx={sourcePos.x}
        cy={sourcePos.y}
        r={4}
        fill={isSelected ? "#3b82f6" : "#64748b"}
        className="transition-colors duration-200"
      />
      {/* Target point */}
      <circle
        cx={targetPos.x}
        cy={targetPos.y}
        r={4}
        fill={isSelected ? "#3b82f6" : "#64748b"}
        className="transition-colors duration-200"
      />
    </g>
  )
}
