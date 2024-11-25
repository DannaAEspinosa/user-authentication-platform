'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { getUsers, deleteUser, changeUserPassword, resetUserPassword, registerUser } from '../actions/admin'
import { Loader2, UserPlus, Key, Trash2 } from 'lucide-react'

interface User {
  id: number
  username: string
  last_login: string
  isDialogOpen: boolean;
}

export default function AdminDashboard() {
  const [users, setUsers] = useState<(User & { isDialogOpen: boolean })[]>([])
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [newUsername, setNewUsername] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [passwordChangeUserId, setPasswordChangeUserId] = useState<number | null>(null)
  const [newUserPassword, setNewUserPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    setIsLoading(true)
    const result = await getUsers()
    setIsLoading(false)
    if (result.success) {
      setUsers(result.data.map(user => ({ ...user, isDialogOpen: false })))
    } else {
      setMessage({ type: 'error', text: result.message })
    }
  }

  const handleDeleteUser = async (userId: number) => {
    const result = await deleteUser(userId)
    setMessage({ type: result.success ? 'success' : 'error', text: result.message })
    if (result.success) {
      fetchUsers()
    }
  }

  const handleChangePassword = async (userId: number) => {
    if (!newUserPassword) {
      setMessage({ type: 'error', text: 'Por favor, ingrese una nueva contraseña' })
      return
    }
    const result = await changeUserPassword(userId, newUserPassword)
    setMessage({ type: result.success ? 'success' : 'error', text: result.message })
    if (result.success) {
      setUsers(users.map(u => 
        u.id === userId ? { ...u, isDialogOpen: false } : u
      ))
      setPasswordChangeUserId(null)
      setNewUserPassword('')
    }
  }

  const handleResetPassword = async (userId: number) => {
    const result = await resetUserPassword(userId)
    setMessage({ type: result.success ? 'success' : 'error', text: result.message })
  }

  const handleRegisterUser = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newUsername || !newPassword) {
      setMessage({ type: 'error', text: 'Por favor, complete todos los campos' })
      return
    }
    const result = await registerUser(newUsername, newPassword)
    setMessage({ type: result.success ? 'success' : 'error', text: result.message })
    if (result.success) {
      setNewUsername('')
      setNewPassword('')
      fetchUsers()
    }
  }

  return (
    <div className="space-y-6">
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Gestión de Usuarios</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center items-center h-40">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre de Usuario</TableHead>
                  <TableHead>Último Login</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{new Date(user.last_login).toLocaleString()}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Dialog 
                          open={user.isDialogOpen} 
                          onOpenChange={(open) => {
                            setUsers(users.map(u => 
                              u.id === user.id ? { ...u, isDialogOpen: open } : u
                            ))
                          }}
                        >
                          <DialogTrigger asChild>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setPasswordChangeUserId(user.id)
                                setNewUserPassword('')
                              }}
                            >
                              <Key className="h-4 w-4 mr-2" />
                              Cambiar Contraseña
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Cambiar Contraseña para {user.username}</DialogTitle>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                              <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="newPassword" className="text-right">
                                  Nueva Contraseña
                                </Label>
                                <Input
                                  id="newPassword"
                                  type="password"
                                  value={newUserPassword}
                                  onChange={(e) => setNewUserPassword(e.target.value)}
                                  className="col-span-3"
                                />
                              </div>
                            </div>
                            <Button onClick={() => handleChangePassword(user.id)}>Guardar Cambios</Button>
                            {message && (
                              <Alert className={`mt-2 ${message.type === 'success' ? 'bg-green-100' : 'bg-red-100'}`}>
                                <AlertDescription>{message.text}</AlertDescription>
                              </Alert>
                            )}
                          </DialogContent>
                        </Dialog>
                        <Button onClick={() => handleResetPassword(user.id)} variant="outline" size="sm">
                          <Key className="h-4 w-4 mr-2" />
                          Poner en Blanco
                        </Button>
                        <Button onClick={() => handleDeleteUser(user.id)} variant="destructive" size="sm">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Eliminar
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Registrar Nuevo Usuario</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleRegisterUser} className="space-y-4">
            <div>
              <Label htmlFor="newUsername">Nombre de Usuario</Label>
              <Input
                id="newUsername"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="newUserPassword">Contraseña</Label>
              <Input
                id="newUserPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit">
              <UserPlus className="h-4 w-4 mr-2" />
              Registrar Usuario
            </Button>
          </form>
          {message && (
            <Alert className={`mt-4 ${message.type === 'success' ? 'bg-green-100' : 'bg-red-100'}`}>
              <AlertDescription>{message.text}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

