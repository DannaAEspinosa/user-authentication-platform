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

interface User {
  id: number
  username: string
  last_login: string
}

export default function AdminDashboard() {
  const [users, setUsers] = useState<User[]>([])
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [newUsername, setNewUsername] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [passwordChangeUserId, setPasswordChangeUserId] = useState<number | null>(null)
  const [newUserPassword, setNewUserPassword] = useState('')
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    const result = await getUsers()
    if (result.success) {
      setUsers(result.data)
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
      setPasswordChangeUserId(null)
      setNewUserPassword('')
      setIsDialogOpen(false)  // Close the dialog on success
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
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Gestión de Usuarios</CardTitle>
        </CardHeader>
        <CardContent>
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
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.last_login}</TableCell>
                  <TableCell>
                    <Button onClick={() => handleDeleteUser(user.id)} variant="destructive" className="mr-2">
                      Eliminar
                    </Button>
                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                      <DialogTrigger asChild>
                        <Button onClick={() => {
                          setPasswordChangeUserId(user.id)
                          setIsDialogOpen(true)
                        }} className="mr-2">
                          Cambiar Contraseña
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Cambiar Contraseña</DialogTitle>
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
                      </DialogContent>
                    </Dialog>
                    <Button onClick={() => handleResetPassword(user.id)} variant="outline">
                      Poner en Blanco
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Registrar Nuevo Usuario</CardTitle>
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
            <Button type="submit">Registrar Usuario</Button>
          </form>
        </CardContent>
      </Card>

      {message && (
        <Alert className={`mt-4 ${message.type === 'success' ? 'bg-green-100' : 'bg-red-100'}`}>
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}

