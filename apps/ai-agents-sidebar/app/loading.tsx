import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <div className="p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <Skeleton className="h-10 w-64 mb-6" />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array(6)
            .fill(0)
            .map((_, index) => (
              <Skeleton key={index} className="h-48 w-full" />
            ))}
        </div>
      </div>
    </div>
  )
}
