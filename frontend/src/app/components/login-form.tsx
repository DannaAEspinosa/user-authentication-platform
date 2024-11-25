'use client'

import { useState } from 'react'
import { login } from '../actions/auth'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useRouter } from 'next/navigation'
import { Loader2, LogIn } from 'lucide-react'

export default function LoginForm() {
  const router = useRouter()
  const [state, setState] = useState<{ success: boolean; message: string } | null>(null)
  const [isPending, setIsPending] = useState(false)

  const handleSubmit = async (formData: FormData) => {
    setIsPending(true)
    const response = await login(null, formData)
    setState(response)
    setIsPending(false)

    if (response.success) {
      router.push('/')
    }
  }

  return (
    <Card className="w-[350px] shadow-lg">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold">Iniciar sesión</CardTitle>
        <CardDescription>Ingresa tus credenciales para acceder</CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            const formData = new FormData(e.target as HTMLFormElement)
            handleSubmit(formData)
          }}
          className="space-y-4"
        >
          <div className="space-y-2">
            <Label htmlFor="username">Nombre de usuario</Label>
            <Input id="username" name="username" type="text" placeholder="usuario" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Contraseña</Label>
            <Input id="password" name="password" type="password" required />
          </div>
          <Button type="submit" className="w-full" disabled={isPending}>
            {isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <LogIn className="h-4 w-4 mr-2" />
            )}
            {isPending ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </Button>
        </form>
      </CardContent>
      {state && (
        <CardFooter>
          <Alert className={`w-full ${state.success ? 'bg-green-100' : 'bg-red-100'}`}>
            <AlertDescription>{state.message}</AlertDescription>
          </Alert>
        </CardFooter>
      )}
    </Card>
  )
}

