import type React from "react"

/**
 * Base parameters for components
 */
export interface BaseComponentParams<T> {
  /**
   * Optional CSS class for styling
   */
  className?: string

  /**
   * Optional inline style
   */
  style?: React.CSSProperties

  /**
   * Reference to the DOM element
   */
  ref?: React.Ref<T>

  /**
   * Unique identifier
   */
  id?: string

  /**
   * Custom data attributes
   */
  dataAttributes?: Record<string, string>

  /**
   * ARIA attributes for accessibility
   */
  ariaAttributes?: Record<string, string>
}

/**
 * Parameters for the ChatInput component
 */
export interface ChatInputParams {
  /**
   * Callback fired when a message is sent
   * @param message The message that was sent
   */
  onSendMessage: (message: string) => void

  /**
   * Whether the input is in a drag-over state
   * @default false
   */
  isDragOver?: boolean

  /**
   * Callback fired when a drag-over event occurs
   */
  onDragOver?: (e: React.DragEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when a drag-leave event occurs
   */
  onDragLeave?: (e: React.DragEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when a drop event occurs
   */
  onDrop?: (e: React.DragEvent<HTMLTextAreaElement>) => void

  /**
   * Additional properties for customization
   */
  [key: string]: any
}

/**
 * Parameters for the FileUploadButton component
 */
export interface FileUploadButtonParams extends BaseComponentParams<HTMLButtonElement> {
  /**
   * Callback fired when files are selected
   */
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void

  /**
   * Accepted file types
   * @default ["image/*", "application/pdf", ".txt", ".md", ".csv"]
   */
  acceptedFileTypes?: string[]

  /**
   * Whether the button is disabled
   * @default false
   */
  disabled?: boolean

  /**
   * Maximum file size in bytes
   * @default 10485760 (10MB)
   */
  maxFileSize?: number

  /**
   * Maximum number of files that can be selected
   * @default 10
   */
  maxFiles?: number

  /**
   * Whether to allow multiple file selection
   * @default true
   */
  multiple?: boolean

  /**
   * Custom renderer for the button
   * If provided, the default button renderer will be ignored
   */
  buttonRenderer?: (props: {
    onClick: () => void
    disabled: boolean
  }) => React.ReactNode

  /**
   * Tooltip text for the button
   * @default "Upload files"
   */
  tooltip?: string

  /**
   * Icon for the button
   * @default <Paperclip />
   */
  icon?: React.ReactNode
}

/**
 * Parameters for the UploadedFilesList component
 */
export interface UploadedFilesListParams extends BaseComponentParams<HTMLDivElement> {
  /**
   * Files to display
   * @default []
   */
  files: File[]

  /**
   * Callback fired when a file is removed
   */
  onRemoveFile: (index: number) => void

  /**
   * Whether to show file previews
   * @default true
   */
  showPreviews?: boolean

  /**
   * Whether to show file sizes
   * @default true
   */
  showSizes?: boolean

  /**
   * Whether to show file types
   * @default false
   */
  showTypes?: boolean

  /**
   * Whether to show file progress
   * @default false
   */
  showProgress?: boolean

  /**
   * Progress for each file (0-100)
   * @default []
   */
  progress?: number[]

  /**
   * Whether to show file errors
   * @default true
   */
  showErrors?: boolean

  /**
   * Errors for each file
   * @default []
   */
  errors?: string[]

  /**
   * Maximum length of file names
   * If a file name exceeds this length, it will be truncated with an ellipsis
   * @default 20
   */
  maxFileNameLength?: number

  /**
   * Custom renderer for each file
   * If provided, the default file renderer will be ignored
   */
  fileRenderer?: (props: {
    file: File
    index: number
    onRemove: () => void
    progress?: number
    error?: string
  }) => React.ReactNode
}
