import { ReactNode } from 'react'
import { Outlet } from 'react-router-dom'
import { cn } from '../utils/helpers'

interface AuthLayoutProps {
  title?: string
  subtitle?: string
}

export function AuthLayout({ title = 'AvertaSaaS', subtitle = 'Auditoria de Frete com Cobrança por Êxito' }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex">
      {/* Brand side */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary-600 p-12 flex-col justify-between relative overflow-hidden">
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div className="h-12 w-12 rounded-xl bg-white flex items-center justify-center">
              <span className="text-primary-600 font-bold text-2xl">A</span>
            </div>
            <span className="text-2xl font-bold text-white">AvertaSaaS</span>
          </div>
        </div>
        <div className="text-center">
          <h1 className="text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
            {title}
          </h1>
          <p className="text-primary-100 text-lg max-w-md mx-auto">
            {subtitle}
          </p>
        </div>
        <div className="text-primary-200 text-sm">
          © 2024 AvertaSaaS. Todos os direitos reservados.
        </div>

        {/* Decorative elements */}
        <div className="absolute top-20 right-10 h-64 w-64 bg-primary-400/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-10 h-64 w-64 bg-primary-400/20 rounded-full blur-3xl" />
      </div>

      {/* Form side */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8 bg-secondary-50">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8 justify-center">
            <div className="h-10 w-10 rounded-lg bg-primary-600 flex items-center justify-center">
              <span className="text-white font-bold text-xl">A</span>
            </div>
            <span className="text-xl font-bold text-secondary-900">AvertaSaaS</span>
          </div>
          <Outlet />
        </div>
      </div>
    </div>
  )
}