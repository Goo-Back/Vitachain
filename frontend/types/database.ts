export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string
          email: string
          full_name: string | null
          role: 'CITIZEN' | 'FARMER' | 'RESTAURANT' | 'ADMIN'
          avatar_url: string | null
          phone: string | null
          address: string | null
          created_at: string
          updated_at: string
          email_verified: boolean
          last_sign_in_at: string | null
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          role: 'CITIZEN' | 'FARMER' | 'RESTAURANT' | 'ADMIN'
          avatar_url?: string | null
          phone?: string | null
          address?: string | null
          created_at?: string
          updated_at?: string
          email_verified?: boolean
          last_sign_in_at?: string | null
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          role?: 'CITIZEN' | 'FARMER' | 'RESTAURANT' | 'ADMIN'
          avatar_url?: string | null
          phone?: string | null
          address?: string | null
          created_at?: string
          updated_at?: string
          email_verified?: boolean
          last_sign_in_at?: string | null
        }
      }
      products: {
        Row: {
          id: string
          name: string
          description: string | null
          price: number
          category: string
          farmer_id: string
          available: boolean
          created_at: string
          updated_at: string
          images: string[]
          location: string | null
          organic: boolean
          quantity: number
          unit: string
        }
        Insert: {
          id?: string
          name: string
          description?: string | null
          price: number
          category: string
          farmer_id: string
          available?: boolean
          created_at?: string
          updated_at?: string
          images?: string[]
          location?: string | null
          organic?: boolean
          quantity: number
          unit: string
        }
        Update: {
          id?: string
          name?: string
          description?: string | null
          price?: number
          category?: string
          farmer_id?: string
          available?: boolean
          created_at?: string
          updated_at?: string
          images?: string[]
          location?: string | null
          organic?: boolean
          quantity?: number
          unit?: string
        }
      }
      orders: {
        Row: {
          id: string
          customer_id: string
          farmer_id: string
          product_id: string
          quantity: number
          total_price: number
          status: 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED'
          delivery_address: string | null
          delivery_notes: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          customer_id: string
          farmer_id: string
          product_id: string
          quantity: number
          total_price: number
          status?: 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED'
          delivery_address?: string | null
          delivery_notes?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          customer_id?: string
          farmer_id?: string
          product_id?: string
          quantity?: number
          total_price?: number
          status?: 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED'
          delivery_address?: string | null
          delivery_notes?: string | null
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      user_role: 'CITIZEN' | 'FARMER' | 'RESTAURANT' | 'ADMIN'
      order_status: 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED'
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}
