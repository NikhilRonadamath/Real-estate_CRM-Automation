import type { ReactNode } from 'react'

interface FormSectionProps {
  title: string
  description?: string
  icon?: ReactNode
  children: ReactNode
}

export default function FormSection({ title, description, icon, children }: FormSectionProps) {
  return (
    <section className="space-y-5">
      <div className="flex items-start gap-3 border-b border-slate-100 pb-4">
        {icon && (
          <div className="rounded-lg bg-slate-100 p-2 text-slate-700">
            {icon}
          </div>
        )}

        <div>
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          {description && (
            <p className="mt-1 text-sm text-slate-500">{description}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">{children}</div>
    </section>
  )
}
