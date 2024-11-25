'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import {logout ,getUserInfo} from '../actions/auth'
import AdminDashboard from './admin-dashboard'
import UserDashboard from './user-dashboard'

export default function Home() {
  const [userInfo, setUserInfo] = useState<{ username: string; isAdmin: boolean; lastLogin?: string } | null>(null)
  const router = useRouter()

  useEffect(() => {
    const fetchUserInfo = async () => {
      const info = await getUserInfo()
      if (info) {
        setUserInfo(info)
      } else {
        router.push('/login')
      }
    }
    fetchUserInfo()
  }, [router])

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  if (!userInfo) {
    
    return <div>Cargando...</div>
  }

  return (
    <div className="container mx-auto p-4">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Bienvenido, {userInfo.username}</CardTitle>
          <CardDescription>
            {userInfo.isAdmin ? 'Panel de Administrador' : 'Panel de Usuario'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleLogout}>Cerrar sesión</Button>
        </CardContent>
      </Card>
      
      {userInfo.isAdmin ? (
        <AdminDashboard />
      ) : (
        <UserDashboard username={userInfo.username} lastLogin={userInfo.lastLogin} />
      )}
    </div>
  )
}

