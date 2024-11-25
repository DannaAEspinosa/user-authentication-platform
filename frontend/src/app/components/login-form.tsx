'use client'

import { useState } from 'react'
import { login } from '../actions/auth'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useRouter } from 'next/navigation'

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
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Iniciar sesión</CardTitle>
        <CardDescription>Ingresa tus credenciales para acceder</CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            const formData = new FormData(e.target as HTMLFormElement)
            handleSubmit(formData)
          }}
        >
          <div className="grid w-full items-center gap-4">
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="username">Nombre de usuario</Label>
              <Input id="username" name="username" type="text" placeholder="usuario" required />
            </div>
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="password">Contraseña</Label>
              <Input id="password" name="password" type="password" required />
            </div>
          </div>
          {state && (
            <Alert className={`mt-4 ${state.success ? 'bg-green-100' : 'bg-red-100'}`}>
              <AlertDescription>{state.message}</AlertDescription>
            </Alert>
          )}
          <CardFooter className="flex justify-between mt-4 p-0">
            <Button type="submit" disabled={isPending}>
              {isPending ? 'Iniciando sesión...' : 'Iniciar sesión'}
            </Button>
          </CardFooter>
        </form>
      </CardContent>
    </Card>
  )
}

