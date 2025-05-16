"use client"

import type React from "react"

import { useState, useCallback } from "react"

interface DragDropOptions {
  onDragStart?: (data: any, event: React.DragEvent) => void
  onDragEnd?: () => void
  onDrop?: (data: any, event: React.DragEvent) => void
  acceptTypes?: string[]
  dataType?: string
}

export function useDragDrop({
  onDragStart,
  onDragEnd,
  onDrop,
  acceptTypes = [],
  dataType = "application/json",
}: DragDropOptions = {}) {
  const [isDragging, setIsDragging] = useState(false)
  const [isOver, setIsOver] = useState(false)

  const handleDragStart = useCallback(
    (data: any) => (event: React.DragEvent) => {
      setIsDragging(true)
      event.dataTransfer.setData(dataType, JSON.stringify(data))

      // Create a drag preview element
      const dragPreview = document.createElement("div")
      dragPreview.className = "bg-white p-2 rounded border shadow-md text-sm"
      dragPreview.textContent = typeof data === "object" && data.name ? data.name : "Dragging item"
      dragPreview.style.position = "absolute"
      dragPreview.style.top = "-1000px"
      document.body.appendChild(dragPreview)

      // Set the drag image
      try {
        event.dataTransfer.setDragImage(dragPreview, 0, 0)
      } catch (err) {
        console.error("Error setting drag image:", err)
      }

      // Remove the element after a short period
      setTimeout(() => {
        document.body.removeChild(dragPreview)
      }, 0)

      onDragStart?.(data, event)
    },
    [dataType, onDragStart],
  )

  const handleDragEnd = useCallback(
    (event: React.DragEvent) => {
      setIsDragging(false)
      onDragEnd?.()
    },
    [onDragEnd],
  )

  const handleDragOver = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()
      if (!isOver) {
        setIsOver(true)
      }
    },
    [isOver],
  )

  const handleDragLeave = useCallback(() => {
    setIsOver(false)
  }, [])

  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()
      setIsOver(false)

      try {
        const data = JSON.parse(event.dataTransfer.getData(dataType))

        // Check if the dropped data is of an accepted type
        if (acceptTypes.length > 0) {
          const type = data.type || ""
          if (!acceptTypes.includes(type)) {
            return
          }
        }

        onDrop?.(data, event)
      } catch (error) {
        console.error("Error processing drop:", error)
      }
    },
    [dataType, acceptTypes, onDrop],
  )

  return {
    isDragging,
    isOver,
    handleDragStart,
    handleDragEnd,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    dragProps: {
      draggable: true,
      onDragStart: handleDragStart,
      onDragEnd: handleDragEnd,
    },
    dropProps: {
      onDragOver: handleDragOver,
      onDragLeave: handleDragLeave,
      onDrop: handleDrop,
    },
  }
}
