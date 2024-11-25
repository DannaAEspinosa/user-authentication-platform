'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { logout, getUserInfo } from '../actions/auth'
import AdminDashboard from './admin-dashboard'
import UserDashboard from './user-dashboard'

export default function Home() {
  const [userInfo, setUserInfo] = useState<{ username: string; is_admin: boolean; last_login?: string } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const fetchUserInfo = async () => {
      setIsLoading(true)
      try {
        const info = await getUserInfo()
        console.log('info:', info)
        if (info) {
          setUserInfo({
            username: info.username,
            is_admin: info.isAdmin, // Ajusta la propiedad aquí
            last_login: info.lastLogin, // Ajusta la propiedad aquí
          })
        } else {
          router.push('/login')
        }
      } catch (error) {
        console.error('Error fetching user info:', error)
        router.push('/login')
      } finally {
        setIsLoading(false)
      }
    }

    fetchUserInfo()
  }, [router])

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  if (isLoading) {
    return <div>Cargando...</div>
  }

  if (!userInfo) {
    return null
  }

  return (
    <div className="container mx-auto p-4">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Bienvenido, {userInfo.username}</CardTitle>
          <CardDescription>
            {userInfo.is_admin ? 'Panel de Administrador' : 'Panel de Usuario'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleLogout}>Cerrar sesión</Button>
        </CardContent>
      </Card>
      
      {userInfo.is_admin ? (
        <AdminDashboard />
      ) : (
        <UserDashboard username={userInfo.username} lastLogin={userInfo.last_login} />
      )}
    </div>
  )
}

