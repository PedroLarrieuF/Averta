import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { useAuth } from '../store/auth-context'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { cn } from '../utils/helpers'
import { Mail, Lock, AlertCircle } from 'lucide-react'

const loginSchema = z.object({
  email: z.string().email('E-mail inválido'),
  password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
})

type LoginForm = z.infer<typeof loginSchema>

export function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    setError('')

    try {
      await login(data.email, data.password)
      toast.success('Login realizado com sucesso!')
      navigate('/dashboard')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Credenciais inválidas'
      setError(message)
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-secondary-900">Entrar na sua conta</h2>
        <p className="text-secondary-500 mt-2">Acesse o painel de auditoria de frete</p>
      </div>

      {error && (
        <div className={cn('flex items-center gap-2 p-3 rounded-lg bg-danger-50 text-danger-700 text-sm', 'animate-in')}>
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
        <Input
          label="E-mail"
          type="email"
          placeholder="seu@email.com"
          autoComplete="email"
          error={errors.email?.message}
          {...register('email')}
          disabled={isLoading}
          icon={<Mail className="h-5 w-5 text-secondary-400" />}
        />

        <div className="relative">
          <Input
            label="Senha"
            type="password"
            placeholder="••••••••"
            autoComplete="current-password"
            error={errors.password?.message}
            {...register('password')}
            disabled={isLoading}
            icon={<Lock className="h-5 w-5 text-secondary-400" />}
          />
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-secondary-600">Lembrar-me</span>
          </label>
          <Link to="/forgot-password" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            Esqueci a senha
          </Link>
        </div>

        <Button type="submit" className="w-full" size="lg" loading={isLoading}>
          Entrar
        </Button>
      </form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-secondary-200" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-4 bg-secondary-50 text-secondary-500">Ou</span>
        </div>
      </div>

      <Button
        variant="secondary"
        className="w-full"
        size="lg"
        onClick={() => navigate('/register')}
      >
        Criar nova conta
      </Button>

      <p className="text-center text-sm text-secondary-500">
        Ao continuar, você concorda com nossos{' '}
        <a href="#" className="text-primary-600 hover:underline">Termos de Uso</a>
        {' '}e{' '}
        <a href="#" className="text-primary-600 hover:underline">Política de Privacidade</a>
      </p>
    </div>
  )
}