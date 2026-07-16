import { useState } from "react"

import { zodResolver } from "@hookform/resolvers/zod"
import {
  Eye,
  EyeOff,
  LoaderCircle,
  LogIn,
} from "lucide-react"
import { useForm } from "react-hook-form"
import {
  Link,
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom"
import { toast } from "sonner"
import { z } from "zod"

import {
  Alert,
  AlertDescription,
} from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useLogin } from "@/hooks/useLogin"
import { useAuthStore } from "@/store/authStore"
import { getApiError } from "@/utils/getApiError"

const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, "Email is required")
    .email("Enter a valid email address"),

  password: z
    .string()
    .min(1, "Password is required")
    .min(
      8,
      "Password must contain at least 8 characters",
    ),
})

type LoginFormValues = z.infer<
  typeof loginSchema
>

interface LoginLocationState {
  from?: {
    pathname?: string
  }
}

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const isAuthenticated =
    useAuthStore(
      (state) => state.isAuthenticated,
    )

  const loginMutation = useLogin()

  const [
    showPassword,
    setShowPassword,
  ] = useState(false)

  const [
    serverError,
    setServerError,
  ] = useState<string | null>(null)

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),

    defaultValues: {
      email: "",
      password: "",
    },
  })

  const isSubmitting =
    loginMutation.isPending

  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  const onSubmit = async (
    values: LoginFormValues,
  ): Promise<void> => {
    setServerError(null)

    try {
      const response =
        await loginMutation.mutateAsync({
          email: values.email
            .trim()
            .toLowerCase(),

          password: values.password,
        })

      toast.success(
        `Welcome back, ${response.user.name}`,
      )

      const state =
        location.state as
          | LoginLocationState
          | null

      const destination =
        state?.from?.pathname ??
        "/dashboard"

      navigate(destination, {
        replace: true,
      })
    } catch (error) {
      const message =
        getApiError(error)

      setServerError(message)
      toast.error(message)
    }
  }

  return (
    <Card className="border-slate-200 shadow-xl">
      <CardHeader className="space-y-2">
        <CardTitle className="text-2xl">
          Sign in
        </CardTitle>

        <CardDescription>
          Enter your credentials to access
          the Enterprise AI Workspace.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(
              onSubmit,
            )}
            className="space-y-5"
            noValidate
          >
            {serverError && (
              <Alert variant="destructive">
                <AlertDescription>
                  {serverError}
                </AlertDescription>
              </Alert>
            )}

            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Email address
                  </FormLabel>

                  <FormControl>
                    <Input
                      type="email"
                      placeholder="name@company.com"
                      autoComplete="email"
                      disabled={isSubmitting}
                      {...field}
                    />
                  </FormControl>

                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center justify-between gap-4">
                    <FormLabel>
                      Password
                    </FormLabel>

                    <Link
                      to="/forgot-password"
                      className="text-sm font-medium text-violet-700 hover:underline"
                    >
                      Forgot password?
                    </Link>
                  </div>

                  <FormControl>
                    <div className="relative">
                      <Input
                        type={
                          showPassword
                            ? "text"
                            : "password"
                        }
                        placeholder="Enter password"
                        autoComplete="current-password"
                        disabled={isSubmitting}
                        className="pr-11"
                        {...field}
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword(
                            (current) =>
                              !current,
                          )
                        }
                        disabled={isSubmitting}
                        aria-label={
                          showPassword
                            ? "Hide password"
                            : "Show password"
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition-colors hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {showPassword ? (
                          <EyeOff className="h-5 w-5" />
                        ) : (
                          <Eye className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </FormControl>

                  <FormMessage />
                </FormItem>
              )}
            />

            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn className="h-4 w-4" />
                  Sign in
                </>
              )}
            </Button>
          </form>
        </Form>

        <p className="mt-6 text-center text-sm text-slate-600">
          Do not have an account?{" "}
          <Link
            to="/register"
            className="font-semibold text-violet-700 hover:underline"
          >
            Create account
          </Link>
        </p>
      </CardContent>
    </Card>
  )
}