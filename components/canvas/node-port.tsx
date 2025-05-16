"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { cn } from "@/lib/utils"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useCanvas } from "@/contexts/canvas-context"

interface NodePortProps {
  nodeId: string
  port: {
    id: string
    type: "input" | "output"
    connections: string[]
    name?: string
    dataType?: string
  }
  isRequired?: boolean
  isCompatible?: boolean
  isAtMaxConnections?: boolean
  maxConnections?: number | null
  disabled?: boolean
  className?: string
}

/**
 * NodePort Component
 *
 * Represents an input or output port on a node that can be connected to other ports.
 *
 * @param nodeId - ID of the node this port belongs to
 * @param port - Port data including ID, type, and connections
 * @param isRequired - Whether this port is required to have a connection
 * @param isCompatible - Whether this port is compatible with the currently dragged port
 * @param isAtMaxConnections - Whether this port has reached its maximum number of connections
 * @param maxConnections - Maximum number of connections this port can have
 * @param disabled - Whether this port is disabled
 * @param className - Additional CSS classes
 */
export function NodePort({
  nodeId,
  port,
  isRequired = false,
  isCompatible = false,
  isAtMaxConnections = false,
  maxConnections = null,
  disabled = false,
  className,
}: NodePortProps) {
  const { addConnection, setSelectedConnection } = useCanvas()
  const [isHovered, setIsHovered] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  // Track the source node and port when starting a connection
  const [connectionSource, setConnectionSource] = useState<{ nodeId: string; portId: string } | null>(null)

  // Determine if the port is connected
  const isConnected = port.connections.length > 0

  // Check if the port has reached its connection limit
  const hasReachedConnectionLimit = maxConnections !== null && port.connections.length >= maxConnections

  /**
   * Get color based on data type
   */
  const getDataTypeColor = useCallback((dataType = "any") => {
    switch (dataType) {
      case "string":
        return "bg-green-500"
      case "number":
        return "bg-blue-500"
      case "boolean":
        return "bg-yellow-500"
      case "object":
        return "bg-purple-500"
      case "array":
        return "bg-indigo-500"
      case "any":
        return "bg-gray-400"
      default:
        return "bg-gray-500"
    }
  }, [])

  /**
   * Handle drag start (for output ports)
   */
  const handleDragStart = useCallback(
    (e: React.DragEvent) => {
      if (disabled || port.type !== "output" || hasReachedConnectionLimit) {
        e.preventDefault()
        return
      }

      // Set drag data
      e.dataTransfer.setData(
        "application/json",
        JSON.stringify({
          nodeId,
          portId: port.id,
          portType: port.type,
          dataType: port.dataType,
        }),
      )

      setIsDragging(true)
      setConnectionSource({ nodeId, portId: port.id })
    },
    [disabled, port, hasReachedConnectionLimit, nodeId],
  )

  /**
   * Handle drag end
   */
  const handleDragEnd = useCallback(() => {
    setIsDragging(false)
    setConnectionSource(null)
  }, [])

  /**
   * Handle drag over (for input ports)
   */
  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      if (port.type === "input" && !disabled && !hasReachedConnectionLimit) {
        e.preventDefault()
        e.stopPropagation()
      }
    },
    [port.type, disabled, hasReachedConnectionLimit],
  )

  /**
   * Handle drop (for input ports)
   */
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      if (port.type !== "input" || disabled || hasReachedConnectionLimit) return

      e.preventDefault()
      e.stopPropagation()

      try {
        const data = JSON.parse(e.dataTransfer.getData("application/json"))

        if (data.portType === "output" && data.nodeId !== nodeId) {
          // Check type compatibility
          if (data.dataType === port.dataType || data.dataType === "any" || port.dataType === "any") {
            addConnection(data.nodeId, data.portId, nodeId, port.id)
          }
        }
      } catch (error) {
        console.error("Error processing drop:", error)
      }
    },
    [port, disabled, hasReachedConnectionLimit, nodeId, addConnection],
  )

  /**
   * Handle click on port
   */
  const handleClick = useCallback(() => {
    if (disabled) return

    // If there's only one connection, select/deselect it
    if (port.connections.length === 1) {
      setSelectedConnection(port.connections[0])
    }
  }, [disabled, port.connections, setSelectedConnection])

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className={cn(
              "w-6 h-6 rounded-full flex items-center justify-center",
              !disabled && "cursor-pointer",
              disabled && "opacity-60 cursor-not-allowed",
              port.type === "input" ? "ml-0" : "mr-0",
              isHovered || isDragging ? "bg-muted/50" : "",
              isCompatible && "ring-2 ring-green-400",
              className,
            )}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            draggable={port.type === "output" && !disabled && !hasReachedConnectionLimit}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={handleClick}
            data-node-id={nodeId}
            data-port-id={port.id}
            data-port-type={port.type}
            data-port-datatype={port.dataType}
            aria-label={`${port.name || port.id} (${port.dataType || "any"}) ${port.type} port`}
            role="button"
            tabIndex={0}
          >
            <div
              className={cn(
                "w-3 h-3 rounded-full border-2 border-background",
                getDataTypeColor(port.dataType),
                isConnected ? "ring-2 ring-white/50" : "",
                isRequired && !isConnected && "ring-2 ring-red-400",
                hasReachedConnectionLimit && "opacity-50",
              )}
              aria-hidden="true"
            />
          </div>
        </TooltipTrigger>
        <TooltipContent side={port.type === "input" ? "left" : "right"}>
          <div>
            <p className="font-medium">{port.name || port.id}</p>
            <p className="text-xs text-muted-foreground">Tipo: {port.dataType || "any"}</p>
            {isConnected && <p className="text-xs text-muted-foreground">Conexões: {port.connections.length}</p>}
            {maxConnections !== null && (
              <p className="text-xs text-muted-foreground">
                {port.connections.length}/{maxConnections} conexões
              </p>
            )}
            {isRequired && !isConnected && <p className="text-xs text-red-400">Obrigatório</p>}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
