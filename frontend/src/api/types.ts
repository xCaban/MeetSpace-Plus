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

export interface RegisterRequest {
  email: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface TokenRefreshResponse {
  access: string
}

export interface Equipment {
  id: number
  name: string
  created_at: string
  updated_at: string
}

export interface RoomEquipmentItem {
  id: number
  name: string
  qty: number
}

export interface RoomEquipmentInput {
  equipment_id: number
  qty: number
}

export interface Room {
  id: number
  name: string
  capacity: number
  location: string
  equipment?: RoomEquipmentItem[]
  created_at: string
  updated_at: string
}

export interface RoomDetail extends Room {
  equipment: RoomEquipmentItem[]
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
  user_first_name: string
  user_last_name: string
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

// --- Admin User Management ---

export interface AdminUser {
  id: number
  email: string
  first_name: string
  last_name: string
  is_admin: boolean
  last_login: string | null
  created_at: string
  updated_at?: string
}

export interface AdminUserCreate {
  email: string
  password: string
  first_name?: string
  last_name?: string
  is_admin?: boolean
}

export interface AdminUserUpdate {
  email?: string
  first_name?: string
  last_name?: string
  is_admin?: boolean
}
