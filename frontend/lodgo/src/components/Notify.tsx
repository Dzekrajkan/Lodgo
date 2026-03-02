import { createContext, useContext, useState } from "react"

type NotifyType = "success" | "error" | "msg"

type NotifyItem = {
  id: number
  text: string
  type: NotifyType
}

type NotifyContextType = {
  notify: (text: string, type?: NotifyType) => void
}

const NotifyContext = createContext<NotifyContextType | null>(null)

export const useNotify = () => {
  const ctx = useContext(NotifyContext)
  if (!ctx) throw new Error("useNotify outside provider")
  return ctx
}

export const NotifyProvider = ({ children }: { children: React.ReactNode }) => {
  const [items, setItems] = useState<NotifyItem[]>([])

  const notify = (text: string, type: NotifyType = "msg") => {
    const id = Date.now()

    setItems(prev => [...prev, { id, text, type }])

    setTimeout(() => {
      setItems(prev => prev.filter(n => n.id !== id))
    }, 4000)
  }

  return (
    <NotifyContext.Provider value={{ notify }}>
      {children}

      <div className="fixed top-5 left-1/2 -translate-x-1/2 flex flex-col gap-3 z-50">
        {items.map(item => (
          <div
            key={item.id}
            className={`px-6 py-3 rounded-xl shadow-lg backdrop-blur-xl border
              ${item.type === "success" && "bg-green-500/20 border-green-400/30"}
              ${item.type === "error" && "bg-red-500/20 border-red-400/30"}
              ${item.type === "msg" && "bg-white/10 border-white/20"}
            `}
          >
            {item.text}
          </div>
        ))}
      </div>

    </NotifyContext.Provider>
  )
}