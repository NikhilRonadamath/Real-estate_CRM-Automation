import type { ReactNode } from 'react'

interface FormFieldProps {
  label: string
  required?: boolean
  children: ReactNode
  fullWidth?: boolean
}

export default function FormField({ label, required = false, children, fullWidth = false }: FormFieldProps) {
  return (
    <div className={`space-y-2 ${fullWidth ? 'sm:col-span-2' : ''}`}>
      <label className="block text-sm font-medium text-slate-700">
        {label}
        {required && <span className="ml-1 text-red-500">*</span>}
      </label>
      {children}
    </div>
  )
}
