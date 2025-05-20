import type React from "react"
import type {
  BaseComponentParams,
  LoadingStateParams,
  FocusStateParams,
  ErrorStateParams,
  ResponsiveParams,
  TransitionParams,
  AnimationParams,
} from "@/types/component-params"

/**
 * Parameters for the ChatInput component
 */
export interface ChatInputParams
  extends BaseComponentParams<HTMLDivElement>,
    LoadingStateParams,
    FocusStateParams,
    ErrorStateParams,
    ResponsiveParams,
    TransitionParams,
    AnimationParams {
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
  onDragOver: (e: React.DragEvent<HTMLDivElement>) => void

  /**
   * Callback fired when a drag-leave event occurs
   */
  onDragLeave: (e: React.DragEvent<HTMLDivElement>) => void

  /**
   * Callback fired when a drop event occurs
   */
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void

  /**
   * Files that have been uploaded
   * @default []
   */
  uploadedFiles: File[]

  /**
   * Callback fired when files are selected
   */
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void

  /**
   * Callback fired when a file is removed
   */
  onRemoveFile: (index: number) => void

  /**
   * Whether to enable file uploads
   * @default true
   */
  enableFileUploads?: boolean

  /**
   * Allowed file types for uploads
   * @default ["image/*", "application/pdf", ".txt", ".md", ".csv"]
   */
  allowedFileTypes?: string[]

  /**
   * Maximum file size for uploads in bytes
   * @default 10485760 (10MB)
   */
  maxFileSize?: number

  /**
   * Maximum number of files that can be uploaded
   * @default 10
   */
  maxFiles?: number

  /**
   * Placeholder text for the input field
   * @default "Type your message here..."
   */
  placeholder?: string

  /**
   * Initial value for the input field
   * @default ""
   */
  initialValue?: string

  /**
   * Maximum length of the input in characters
   * @default 0 (no limit)
   */
  maxLength?: number

  /**
   * Minimum length of the input in characters
   * @default 0
   */
  minLength?: number

  /**
   * Whether to show a character counter
   * @default false
   */
  showCharacterCounter?: boolean

  /**
   * Maximum height of the input field in pixels
   * @default 200
   */
  maxHeight?: number

  /**
   * Minimum height of the input field in pixels
   * @default 40
   */
  minHeight?: number

  /**
   * Whether to enable auto-resize of the input field
   * @default true
   */
  enableAutoResize?: boolean

  /**
   * Whether to enable auto-focus of the input field
   * @default false
   */
  enableAutoFocus?: boolean

  /**
   * Whether to enable spell checking
   * @default true
   */
  enableSpellCheck?: boolean

  /**
   * Whether to enable auto-complete
   * @default true
   */
  enableAutoComplete?: boolean

  /**
   * Whether to enable auto-correct
   * @default true
   */
  enableAutoCorrect?: boolean

  /**
   * Whether to enable auto-capitalize
   * @default true
   */
  enableAutoCapitalize?: boolean

  /**
   * Whether to enable emoji picker
   * @default false
   */
  enableEmojiPicker?: boolean

  /**
   * Whether to enable mentions
   * @default false
   */
  enableMentions?: boolean

  /**
   * Whether to enable markdown formatting
   * @default false
   */
  enableMarkdown?: boolean

  /**
   * Whether to enable keyboard shortcuts
   * @default true
   */
  enableKeyboardShortcuts?: boolean

  /**
   * Whether to enable drag and drop
   * @default true
   */
  enableDragAndDrop?: boolean

  /**
   * Whether to enable paste from clipboard
   * @default true
   */
  enablePaste?: boolean

  /**
   * Whether to enable voice input
   * @default false
   */
  enableVoiceInput?: boolean

  /**
   * Whether to enable suggestions
   * @default false
   */
  enableSuggestions?: boolean

  /**
   * Suggestions to display
   * @default []
   */
  suggestions?: string[]

  /**
   * Whether to enable commands
   * @default false
   */
  enableCommands?: boolean

  /**
   * Commands to enable
   * @default []
   */
  commands?: { name: string; description: string; action: () => void }[]

  /**
   * Whether to enable rich text editing
   * @default false
   */
  enableRichText?: boolean

  /**
   * Whether to enable file preview
   * @default true
   */
  enableFilePreview?: boolean

  /**
   * Whether to enable file drag preview
   * @default true
   */
  enableFileDragPreview?: boolean

  /**
   * Whether to enable file progress
   * @default true
   */
  enableFileProgress?: boolean

  /**
   * Whether to enable file retry
   * @default true
   */
  enableFileRetry?: boolean

  /**
   * Whether to enable file cancel
   * @default true
   */
  enableFileCancel?: boolean

  /**
   * Whether to enable send button
   * @default true
   */
  enableSendButton?: boolean

  /**
   * Whether to enable send on Enter
   * @default true
   */
  enableSendOnEnter?: boolean

  /**
   * Whether to enable send on Ctrl+Enter
   * @default false
   */
  enableSendOnCtrlEnter?: boolean

  /**
   * Whether to enable send on Shift+Enter
   * @default false
   */
  enableSendOnShiftEnter?: boolean

  /**
   * Whether to enable send on Meta+Enter
   * @default false
   */
  enableSendOnMetaEnter?: boolean

  /**
   * Whether to enable send on Alt+Enter
   * @default false
   */
  enableSendOnAltEnter?: boolean

  /**
   * Custom renderer for the input field
   * If provided, the default input field renderer will be ignored
   */
  inputRenderer?: (props: {
    value: string
    onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
    onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void
    placeholder: string
    disabled: boolean
    ref: React.RefObject<HTMLTextAreaElement>
  }) => React.ReactNode

  /**
   * Custom renderer for the send button
   * If provided, the default send button renderer will be ignored
   */
  sendButtonRenderer?: (props: {
    onClick: () => void
    disabled: boolean
  }) => React.ReactNode

  /**
   * Custom renderer for the file upload button
   * If provided, the default file upload button renderer will be ignored
   */
  fileUploadButtonRenderer?: (props: {
    onClick: () => void
    disabled: boolean
  }) => React.ReactNode

  /**
   * Custom renderer for the uploaded files list
   * If provided, the default uploaded files list renderer will be ignored
   */
  uploadedFilesRenderer?: (props: {
    files: File[]
    onRemove: (index: number) => void
  }) => React.ReactNode

  /**
   * Callback fired when the input value changes
   */
  onChange?: (value: string) => void

  /**
   * Callback fired when the input field is focused
   */
  onFocus?: () => void

  /**
   * Callback fired when the input field is blurred
   */
  onBlur?: () => void

  /**
   * Callback fired when a key is pressed in the input field
   */
  onKeyDown?: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when a key is released in the input field
   */
  onKeyUp?: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when the input field is clicked
   */
  onClick?: (e: React.MouseEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when the input field is double-clicked
   */
  onDoubleClick?: (e: React.MouseEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when the input field is right-clicked
   */
  onContextMenu?: (e: React.MouseEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when text is pasted into the input field
   */
  onPaste?: (e: React.ClipboardEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when text is cut from the input field
   */
  onCut?: (e: React.ClipboardEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when text is copied from the input field
   */
  onCopy?: (e: React.ClipboardEvent<HTMLTextAreaElement>) => void

  /**
   * Callback fired when a command is executed
   */
  onCommand?: (command: string) => void

  /**
   * Callback fired when a mention is selected
   */
  onMention?: (mention: string) => void

  /**
   * Callback fired when an emoji is selected
   */
  onEmoji?: (emoji: string) => void

  /**
   * Callback fired when a suggestion is selected
   */
  onSuggestion?: (suggestion: string) => void

  /**
   * Callback fired when voice input starts
   */
  onVoiceInputStart?: () => void

  /**
   * Callback fired when voice input ends
   */
  onVoiceInputEnd?: () => void

  /**
   * Callback fired when voice input results are available
   */
  onVoiceInputResult?: (result: string) => void

  /**
   * Callback fired when voice input errors occur
   */
  onVoiceInputError?: (error: Error) => void
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
