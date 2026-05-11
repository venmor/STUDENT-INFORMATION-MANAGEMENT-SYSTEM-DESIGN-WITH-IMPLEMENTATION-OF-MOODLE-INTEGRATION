export interface School {
  id: string
  code: string
  name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Department {
  id: string
  code: string
  name: string
  school: string
  school_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Programme {
  id: string
  code: string
  name: string
  department: string
  department_name: string
  level: 'UG' | 'PG'
  duration_years: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Stream {
  id: string
  code: string
  name: string
  programme: string
  programme_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}
