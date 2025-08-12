import * as React from "react"
import { cn } from "@/lib/utils"

interface ScrollAreaProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

function ScrollArea({ className, children, ...props }: ScrollAreaProps) {
  return (
    <div
      className={cn(
        "relative overflow-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export { ScrollArea }
