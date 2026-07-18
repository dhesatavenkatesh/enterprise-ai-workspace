export interface ValidationErrorItem {
  loc?: Array<string | number>
  msg?: string
  type?: string
  field?: string
  message?: string
}

export interface ApiErrorResponse {
  success?: boolean

  detail?:
    | string
    | ValidationErrorItem[]

  message?: string

  errors?: ValidationErrorItem[]
}