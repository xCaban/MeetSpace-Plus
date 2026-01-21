/**
 * Typy DTO zgodne z API MeetSpace Plus.
 */

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  roles: string[]
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface TokenRefreshResponse {
  access: string
}

export interface Room {
  id: number
  name: string
  capacity: number
  location: string
  equipment?: { name: string; qty: number }[]
  created_at: string
  updated_at: string
}

export interface RoomDetail extends Room {
  equipment: { name: string; qty: number }[]
}

export interface ReservationStatus {
  pending: "pending"
  confirmed: "confirmed"
  canceled: "canceled"
}

export type ReservationStatusValue = "pending" | "confirmed" | "canceled"

export interface Reservation {
  id: number
  user: number
  user_email: string
  room: number
  room_name: string
  status: ReservationStatusValue
  start_at: string
  end_at: string
  hold_expires_at: string | null
  created_at: string
  updated_at: string
}

export interface ReservationCreate {
  room_id: number
  start_at: string
  end_at: string
}

export interface ApiError {
  detail?: string
  [key: string]: string | string[] | undefined
}
