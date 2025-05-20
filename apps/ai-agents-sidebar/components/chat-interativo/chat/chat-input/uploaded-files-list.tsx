"use client"

interface UploadedFilesListProps {
  files: File[]
  onRemoveFile: (index: number) => void
}

export function UploadedFilesList({ files, onRemoveFile }: UploadedFilesListProps) {
  if (files.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2 mb-2 p-2">
      {files.map((file, index) => (
        <div
          key={`${file.name}-${index}`}
          className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-full px-3 py-1 text-xs"
        >
          <span className="truncate max-w-[150px]">{file.name}</span>
          <button
            className="ml-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            onClick={() => onRemoveFile(index)}
          >
            &times;
          </button>
        </div>
      ))}
    </div>
  )
}
