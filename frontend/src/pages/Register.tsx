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
import { Mail, Lock, User, Building, AlertCircle, UserPlus } from 'lucide-react'

const registerSchema = z.object({
  fullName: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  email: z.string().email('E-mail inválido'),
  password: z.string().min(8, 'Senha deve ter pelo menos 8 caracteres'),
  confirmPassword: z.string(),
  companyName: z.string().min(2, 'Nome da empresa deve ter pelo menos 2 caracteres'),
  companyCnpj: z.string().min(14, 'CNPJ inválido'),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Senhas não conferem',
  path: ['confirmPassword'],
})

type RegisterForm = z.infer<typeof registerSchema>

export function Register() {
  const navigate = useNavigate()
  const { register: registerUser } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      fullName: '',
      email: '',
      password: '',
      confirmPassword: '',
      companyName: '',
      companyCnpj: '',
    },
  })

  const password = watch('password')

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true)
    setError('')

    try {
      await registerUser({
        email: data.email,
        password: data.password,
        fullName: data.fullName,
        companyName: data.companyName,
        companyCnpj: data.companyCnpj.replace(/\D/g, ''),
      })
      toast.success('Conta criada com sucesso! Bem-vindo ao AvertaSaaS.')
      navigate('/dashboard')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao criar conta'
      setError(message)
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const getPasswordStrength = (pwd: string) => {
    let strength = 0
    if (pwd.length >= 8) strength++
    if (/[A-Z]/.test(pwd)) strength++
    if (/[a-z]/.test(pwd)) strength++
    if (/[0-9]/.test(pwd)) strength++
    if (/[^A-Za-z0-9]/.test(pwd)) strength++
    return strength
  }

  const strength = getPasswordStrength(password)
  const strengthLabels = ['Muito fraca', 'Fraca', 'Média', 'Forte', 'Muito forte']
  const strengthColors = ['bg-danger-500', 'bg-danger-500', 'bg-warning-500', 'bg-primary-500', 'bg-success-500']

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-secondary-900">Criar conta</h2>
        <p className="text-secondary-500 mt-2">Comece a auditar seus fretes hoje mesmo</p>
      </div>

      {error && (
        <div className={cn('flex items-center gap-2 p-3 rounded-lg bg-danger-50 text-danger-700 text-sm', 'animate-in')}>
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Nome completo"
            type="text"
            placeholder="João da Silva"
            autoComplete="name"
            error={errors.fullName?.message}
            {...register('fullName')}
            disabled={isLoading}
            icon={<User className="h-5 w-5 text-secondary-400" />}
          />
          <Input
            label="E-mail corporativo"
            type="email"
            placeholder="joao@empresa.com.br"
            autoComplete="email"
            error={errors.email?.message}
            {...register('email')}
            disabled={isLoading}
            icon={<Mail className="h-5 w-5 text-secondary-400" />}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Nome da empresa"
            type="text"
            placeholder="Empresa Ltda"
            autoComplete="organization"
            error={errors.companyName?.message}
            {...register('companyName')}
            disabled={isLoading}
            icon={<Building className="h-5 w-5 text-secondary-400" />}
          />
          <Input
            label="CNPJ da empresa"
            type="text"
            placeholder="00.000.000/0000-00"
            autoComplete="off"
            error={errors.companyCnpj?.message}
            {...register('companyCnpj', {
              onChange: (e) => {
                let value = e.target.value.replace(/\D/g, '')
                if (value.length > 14) value = value.slice(0, 14)
                // Format: 00.000.000/0000-00
                if (value.length > 12) value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
                else if (value.length > 8) value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{0,4})$/, '$1.$2.$3/$4')
                else if (value.length > 5) value = value.replace(/^(\d{2})(\d{3})(\d{0,3})$/, '$1.$2.$3')
                else if (value.length > 2) value = value.replace(/^(\d{2})(\d{0,3})$/, '$1.$2')
                register('companyCnpj').onChange({ target: { value } } as any)
              },
            })}
            disabled={isLoading}
            icon={<Building className="h-5 w-5 text-secondary-400" />}
          />
        </div>

        <Input
          label="Senha"
          type="password"
          placeholder="••••••••"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register('password')}
          disabled={isLoading}
          icon={<Lock className="h-5 w-5 text-secondary-400" />}
          helperText={
            password && (
              <div className="mt-2 space-y-1">
                <div className="h-1.5 rounded-full overflow-hidden bg-secondary-200">
                  <div
                    className={cn('h-full transition-all duration-300', strengthColors[strength - 1] || 'bg-secondary-200')}
                    style={{ width: `${(strength / 5) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-secondary-500">Força da senha: {strengthLabels[strength - 1] || 'Muito fraca'}</p>
              </div>
            )
          }
        />

        <Input
          label="Confirmar senha"
          type="password"
          placeholder="••••••••"
          autoComplete="new-password"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
          disabled={isLoading}
          icon={<Lock className="h-5 w-5 text-secondary-400" />}
        />

        <div className="flex items-start gap-2">
          <input
            type="checkbox"
            id="terms"
            required
            className="mt-1 h-4 w-4 rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
          />
          <label htmlFor="terms" className="text-sm text-secondary-600">
            Aceito os{' '}
            <a href="#" className="text-primary-600 hover:underline">Termos de Uso</a>
            {' '}e a{' '}
            <a href="#" className="text-primary-600 hover:underline">Política de Privacidade</a>
          </label>
        </div>

        <Button type="submit" className="w-full" size="lg" loading={isLoading}>
          <UserPlus className="h-5 w-5" />
          Criar minha conta
        </Button>
      </form>

      <p className="text-center text-sm text-secondary-500">
        Já tem conta?{' '}
        <Link to="/login" className="text-primary-600 hover:underline font-medium">
          Entrar
        </Link>
      </p>
    </div>
  )
}