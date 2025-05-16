"use client"

import type React from "react"

import { useRef, useCallback, useState, useEffect, useMemo } from "react"
import { Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { FileUploadButton } from "./file-upload-button"
import { UploadedFilesList } from "./uploaded-files-list"
import type { ChatInputParams } from "./types"
import { cn } from "@/lib/utils"

/**
 * ChatInput component
 *
 * A highly configurable input component for chat interfaces with support for
 * file uploads, auto-resizing, and various input methods.
 */
export function ChatInput({
  onSendMessage,
  isLoading = false,
  loadingText = "Sending...",
  loadingComponent,
  disableWhileLoading = true,
  loadingAnimation = "pulse",
  disabled = false,
  isDragOver = false,
  onDragOver,
  onDragLeave,
  onDrop,
  uploadedFiles = [],
  onFileSelect,
  onRemoveFile,
  enableFileUploads = true,
  allowedFileTypes = ["image/*", "application/pdf", ".txt", ".md", ".csv"],
  maxFileSize = 10 * 1024 * 1024, // 10MB
  maxFiles = 10,
  placeholder = "Type your message here...",
  initialValue = "",
  maxLength = 0,
  minLength = 0,
  showCharacterCounter = false,
  maxHeight = 200,
  minHeight = 40,
  enableAutoResize = true,
  enableAutoFocus = false,
  enableSpellCheck = true,
  enableAutoComplete = true,
  enableAutoCorrect = true,
  enableAutoCapitalize = true,
  enableEmojiPicker = false,
  enableMentions = false,
  enableMarkdown = false,
  enableKeyboardShortcuts = true,
  enableDragAndDrop = true,
  enablePaste = true,
  enableVoiceInput = false,
  enableSuggestions = false,
  suggestions = [],
  enableCommands = false,
  commands = [],
  enableRichText = false,
  enableFilePreview = true,
  enableFileDragPreview = true,
  enableFileProgress = true,
  enableFileRetry = true,
  enableFileCancel = true,
  enableSendButton = true,
  enableSendOnEnter = true,
  enableSendOnCtrlEnter = false,
  enableSendOnShiftEnter = false,
  enableSendOnMetaEnter = false,
  enableSendOnAltEnter = false,
  inputRenderer,
  sendButtonRenderer,
  fileUploadButtonRenderer,
  uploadedFilesRenderer,
  onChange,
  onFocus,
  onBlur,
  onKeyDown,
  onKeyUp,
  onClick,
  onDoubleClick,
  onContextMenu,
  onPaste,
  onCut,
  onCopy,
  onCommand,
  onMention,
  onEmoji,
  onSuggestion,
  onVoiceInputStart,
  onVoiceInputEnd,
  onVoiceInputResult,
  onVoiceInputError,
  className = "",
  style,
  id,
  dataAttributes,
  ariaAttributes,
  focusable = true,
  tabIndex,
  interactive = true,
  showFocusRing = true,
  focusRingColor = "primary",
  autoFocus = false,
  hasError = false,
  errorMessage,
  errorMessagePosition = "bottom",
  animated = true,
  animation = "fade",
  animationDuration = 300,
  animationDelay = 0,
  animationEasing = "ease",
  hideOnMobile = false,
  hideOnTablet = false,
  hideOnDesktop = false,
  responsive = true,
  transition = true,
  transitionDuration = 200,
  transitionProperties = ["all"],
  transitionEasing = "ease",
}: ChatInputParams) {
  // Refs
  const chatAreaRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // State
  const [value, setValue] = useState(initialValue)
  const [isFocused, setIsFocused] = useState(false)
  const [charCount, setCharCount] = useState(initialValue.length)

  // Effects

  // Auto-focus the textarea when the component mounts
  useEffect(() => {
    if (enableAutoFocus || autoFocus) {
      textareaRef.current?.focus()
    }
  }, [enableAutoFocus, autoFocus])

  // Update character count when value changes
  useEffect(() => {
    setCharCount(value.length)
  }, [value])

  // Callbacks

  // Handle textarea input
  const handleInput = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const textarea = e.target
      const newValue = textarea.value

      // Check max length
      if (maxLength > 0 && newValue.length > maxLength) {
        return
      }

      setValue(newValue)
      onChange?.(newValue)

      // Auto-resize the textarea
      if (enableAutoResize) {
        textarea.style.height = "auto"
        textarea.style.height = `${Math.min(Math.max(textarea.scrollHeight, minHeight), maxHeight)}px`
      }
    },
    [maxLength, onChange, enableAutoResize, minHeight, maxHeight],
  )

  // Handle key down events
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Call the onKeyDown callback
      onKeyDown?.(e)

      // Handle keyboard shortcuts
      if (enableKeyboardShortcuts) {
        const isCtrlPressed = e.ctrlKey || e.metaKey
        const isShiftPressed = e.shiftKey
        const isAltPressed = e.altKey

        // Send on Enter
        if (e.key === "Enter") {
          // Check various send conditions
          const shouldSendOnEnter = enableSendOnEnter && !isCtrlPressed && !isShiftPressed && !isAltPressed
          const shouldSendOnCtrlEnter = enableSendOnCtrlEnter && isCtrlPressed && !isShiftPressed && !isAltPressed
          const shouldSendOnShiftEnter = enableSendOnShiftEnter && !isCtrlPressed && isShiftPressed && !isAltPressed
          const shouldSendOnMetaEnter = enableSendOnMetaEnter && isCtrlPressed && !isShiftPressed && !isAltPressed
          const shouldSendOnAltEnter = enableSendOnAltEnter && !isCtrlPressed && !isShiftPressed && isAltPressed

          if (
            shouldSendOnEnter ||
            shouldSendOnCtrlEnter ||
            shouldSendOnShiftEnter ||
            shouldSendOnMetaEnter ||
            shouldSendOnAltEnter
          ) {
            e.preventDefault()
            handleSubmit()
          }
        }
      }
    },
    [
      enableKeyboardShortcuts,
      enableSendOnEnter,
      enableSendOnCtrlEnter,
      enableSendOnShiftEnter,
      enableSendOnMetaEnter,
      enableSendOnAltEnter,
      onKeyDown,
    ],
  )

  // Handle focus events
  const handleFocus = useCallback(() => {
    setIsFocused(true)
    onFocus?.()
  }, [onFocus])

  // Handle blur events
  const handleBlur = useCallback(() => {
    setIsFocused(false)
    onBlur?.()
  }, [onBlur])

  // Handle paste events
  const handlePaste = useCallback(
    (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
      if (!enablePaste) {
        e.preventDefault()
        return
      }

      onPaste?.(e)
    },
    [enablePaste, onPaste],
  )

  // Handle submit
  const handleSubmit = useCallback(() => {
    if (value.trim() && !isLoading && !disabled) {
      // Check minimum length
      if (minLength > 0 && value.length < minLength) {
        return
      }

      onSendMessage(value)
      setValue("")

      // Reset textarea height
      if (enableAutoResize && textareaRef.current) {
        textareaRef.current.style.height = "auto"
      }
    }
  }, [value, isLoading, disabled, minLength, onSendMessage, enableAutoResize])

  // Handle file input click
  const handleFileInputClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  // Memoized values

  // Determine if the submit button should be disabled
  const isSubmitDisabled = useMemo(() => {
    if (disabled || (disableWhileLoading && isLoading)) {
      return true
    }

    if (!value.trim()) {
      return true
    }

    if (minLength > 0 && value.length < minLength) {
      return true
    }

    return false
  }, [disabled, disableWhileLoading, isLoading, value, minLength])

  // Prepare animation and transition styles
  const animationStyle = useMemo(() => {
    if (!animated) return {}

    return {
      animation: `${animation} ${animationDuration}ms ${animationEasing} ${animationDelay}ms`,
    }
  }, [animated, animation, animationDuration, animationEasing, animationDelay])

  const transitionStyle = useMemo(() => {
    if (!transition) return {}

    return {
      transition: `${transitionProperties.join(", ")} ${transitionDuration}ms ${transitionEasing}`,
    }
  }, [transition, transitionProperties, transitionDuration, transitionEasing])

  // Combine all styles
  const combinedStyle = useMemo(
    () => ({
      ...style,
      ...animationStyle,
      ...transitionStyle,
    }),
    [style, animationStyle, transitionStyle],
  )

  // Prepare responsive classes
  const responsiveClasses = useMemo(() => {
    if (!responsive) return ""

    return cn(hideOnMobile && "hidden sm:block", hideOnTablet && "hidden md:block", hideOnDesktop && "block md:hidden")
  }, [responsive, hideOnMobile, hideOnTablet, hideOnDesktop])

  // Prepare focus ring classes
  const focusRingClasses = useMemo(() => {
    if (!showFocusRing) return ""

    return cn(isFocused && `ring-2 ring-${focusRingColor}-500 ring-offset-2`)
  }, [showFocusRing, isFocused, focusRingColor])

  // Prepare error classes
  const errorClasses = useMemo(() => {
    if (!hasError) return ""

    return "border-red-500 dark:border-red-400"
  }, [hasError])

  // Combine all classes
  const allClasses = useMemo(
    () =>
      cn(
        `border ${
          isDragOver ? "border-primary border-dashed bg-primary/5" : "border-gray-200 dark:border-gray-700"
        } rounded-xl overflow-hidden shadow-sm hover:shadow transition-shadow duration-200 bg-white dark:bg-gray-800`,
        responsiveClasses,
        focusRingClasses,
        errorClasses,
        className,
      ),
    [isDragOver, responsiveClasses, focusRingClasses, errorClasses, className],
  )

  // Prepare data attributes
  const allDataAttributes = useMemo(
    () => ({
      "data-loading": isLoading ? "true" : "false",
      "data-disabled": disabled ? "true" : "false",
      "data-drag-over": isDragOver ? "true" : "false",
      "data-focused": isFocused ? "true" : "false",
      "data-has-error": hasError ? "true" : "false",
      ...(dataAttributes || {}),
    }),
    [isLoading, disabled, isDragOver, isFocused, hasError, dataAttributes],
  )

  // Prepare ARIA attributes
  const allAriaAttributes = useMemo(
    () => ({
      "aria-disabled": disabled ? "true" : "false",
      "aria-busy": isLoading ? "true" : "false",
      "aria-invalid": hasError ? "true" : "false",
      ...(ariaAttributes || {}),
    }),
    [disabled, isLoading, hasError, ariaAttributes],
  )

  return (
    <div className="space-y-2">
      <Card
        className={allClasses}
        style={combinedStyle}
        onDragOver={enableDragAndDrop ? onDragOver : undefined}
        onDragLeave={enableDragAndDrop ? onDragLeave : undefined}
        onDrop={enableDragAndDrop ? onDrop : undefined}
        ref={chatAreaRef}
        id={id}
        tabIndex={tabIndex}
        {...allDataAttributes}
        {...allAriaAttributes}
      >
        <div className="p-2">
          {/* Uploaded files list */}
          {uploadedFilesRenderer ? (
            uploadedFilesRenderer({
              files: uploadedFiles,
              onRemove: onRemoveFile,
            })
          ) : (
            <UploadedFilesList
              files={uploadedFiles}
              onRemoveFile={onRemoveFile}
              showPreviews={enableFilePreview}
              showSizes={true}
              showTypes={false}
              showProgress={enableFileProgress}
              showErrors={true}
            />
          )}

          {/* Text input */}
          <div className="relative">
            {inputRenderer ? (
              inputRenderer({
                value,
                onChange: handleInput,
                onKeyDown: handleKeyDown,
                placeholder: isDragOver ? "Drop files or components here..." : placeholder,
                disabled: disabled || (disableWhileLoading && isLoading),
                ref: textareaRef,
              })
            ) : (
              <textarea
                ref={textareaRef}
                value={value}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                onKeyUp={onKeyUp}
                onClick={onClick}
                onDoubleClick={onDoubleClick}
                onContextMenu={onContextMenu}
                onPaste={handlePaste}
                onCut={onCut}
                onCopy={onCopy}
                onFocus={handleFocus}
                onBlur={handleBlur}
                placeholder={isDragOver ? "Drop files or components here..." : placeholder}
                className={`w-full border-0 focus:ring-0 focus:outline-none resize-none p-3 pr-20 text-gray-700 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-800 transition-colors duration-200 ${
                  isDragOver ? "border-2 border-dashed border-primary/50 bg-primary/5" : ""
                }`}
                style={{
                  height: "auto",
                  minHeight: `${minHeight}px`,
                  maxHeight: `${maxHeight}px`,
                }}
                disabled={disabled || (disableWhileLoading && isLoading)}
                spellCheck={enableSpellCheck}
                autoComplete={enableAutoComplete ? "on" : "off"}
                autoCorrect={enableAutoCorrect ? "on" : "off"}
                autoCapitalize={enableAutoCapitalize ? "on" : "off"}
                maxLength={maxLength > 0 ? maxLength : undefined}
                onDragOver={enableDragAndDrop ? onDragOver : undefined}
                onDragLeave={enableDragAndDrop ? onDragLeave : undefined}
                onDrop={enableDragAndDrop ? onDrop : undefined}
              />
            )}

            {/* Action buttons */}
            <div className="absolute right-2 bottom-2 flex items-center space-x-1">
              {/* File upload button */}
              {enableFileUploads &&
                (fileUploadButtonRenderer ? (
                  fileUploadButtonRenderer({
                    onClick: handleFileInputClick,
                    disabled: disabled || (disableWhileLoading && isLoading),
                  })
                ) : (
                  <FileUploadButton
                    onFileSelect={onFileSelect}
                    acceptedFileTypes={allowedFileTypes}
                    disabled={disabled || (disableWhileLoading && isLoading)}
                    maxFileSize={maxFileSize}
                    maxFiles={maxFiles}
                    multiple={true}
                  />
                ))}

              {/* Send button */}
              {enableSendButton &&
                (sendButtonRenderer ? (
                  sendButtonRenderer({
                    onClick: handleSubmit,
                    disabled: isSubmitDisabled,
                  })
                ) : (
                  <Button
                    size="icon"
                    className="h-9 w-9 rounded-full bg-primary text-white hover:bg-primary/90 shadow-sm transition-all duration-200 hover:shadow"
                    onClick={handleSubmit}
                    disabled={isSubmitDisabled}
                  >
                    {isLoading ? (
                      loadingComponent || (
                        <div className={`animate-${loadingAnimation}`}>
                          {loadingText === "Loading..." ? (
                            <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent" />
                          ) : (
                            loadingText
                          )}
                        </div>
                      )
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                ))}
            </div>
          </div>

          {/* Character counter */}
          {showCharacterCounter && (
            <div className="text-xs text-gray-500 dark:text-gray-400 text-right mt-1 pr-2">
              {maxLength > 0 ? `${charCount}/${maxLength}` : charCount}
            </div>
          )}
        </div>
      </Card>

      {/* Error message */}
      {hasError && errorMessage && (
        <div
          className={`text-sm text-red-500 dark:text-red-400 ${
            errorMessagePosition === "top" ? "order-first" : "order-last"
          }`}
        >
          {errorMessage}
        </div>
      )}
    </div>
  )
}
