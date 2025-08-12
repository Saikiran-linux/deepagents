import * as React from "react"
import { ChevronDown, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

interface CollapsibleProps {
  children: React.ReactNode
  title: string
  defaultOpen?: boolean
  className?: string
  titleClassName?: string
}

export function Collapsible({ 
  children, 
  title, 
  defaultOpen = false, 
  className,
  titleClassName 
}: CollapsibleProps) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen)

  return (
    <div className={cn("border rounded-lg", className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center justify-between w-full px-3 py-2 text-left text-sm font-medium hover:bg-muted/50 transition-colors",
          titleClassName
        )}
      >
        <span className="flex items-center gap-2">
          {isOpen ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )}
          {title}
        </span>
      </button>
      {isOpen && (
        <div className="px-3 pb-3 pt-1 border-t bg-muted/20">
          {children}
        </div>
      )}
    </div>
  )
}
