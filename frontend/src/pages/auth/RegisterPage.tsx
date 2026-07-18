import { useState } from "react"

import { zodResolver } from "@hookform/resolvers/zod"
import {
  Eye,
  EyeOff,
  LoaderCircle,
  UserPlus,
} from "lucide-react"
import { useForm } from "react-hook-form"
import {
  Link,
  Navigate,
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
import { useRegister } from "@/hooks/useRegister"
import { useAuthStore } from "@/store/authStore"
import { getApiError } from "@/utils/getApiError"

const passwordRule =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$/

const registerSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(
        2,
        "Name must contain at least 2 characters",
      )
      .max(
        100,
        "Name must not exceed 100 characters",
      ),

    email: z
      .string()
      .trim()
      .min(1, "Email is required")
      .email(
        "Enter a valid email address",
      ),

    password: z
      .string()
      .min(
        8,
        "Password must contain at least 8 characters",
      )
      .max(
        72,
        "Password must not exceed 72 characters",
      )
      .regex(
        passwordRule,
        "Password must include uppercase, lowercase, number and special character",
      ),

    confirmPassword: z
      .string()
      .min(
        1,
        "Please confirm your password",
      ),
  })
  .refine(
    (values) =>
      values.password ===
      values.confirmPassword,
    {
      message: "Passwords do not match",
      path: ["confirmPassword"],
    },
  )

type RegisterFormValues = z.infer<
  typeof registerSchema
>

export function RegisterPage() {
  const navigate = useNavigate()

  const isAuthenticated =
    useAuthStore(
      (state) => state.isAuthenticated,
    )

  const registerMutation =
    useRegister()

  const [
    showPassword,
    setShowPassword,
  ] = useState(false)

  const [
    showConfirmPassword,
    setShowConfirmPassword,
  ] = useState(false)

  const [
    serverError,
    setServerError,
  ] = useState<string | null>(null)

  const form =
    useForm<RegisterFormValues>({
      resolver: zodResolver(
        registerSchema,
      ),

      defaultValues: {
        name: "",
        email: "",
        password: "",
        confirmPassword: "",
      },
    })

  const isSubmitting =
    registerMutation.isPending

  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  const onSubmit = async (
    values: RegisterFormValues,
  ): Promise<void> => {
    setServerError(null)

    try {
      await registerMutation.mutateAsync({
        name: values.name.trim(),

        email: values.email
          .trim()
          .toLowerCase(),

        password: values.password,
      })

      toast.success(
        "Account created successfully. Please sign in.",
      )

      navigate("/login", {
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
          Create account
        </CardTitle>

        <CardDescription>
          Register as an employee to
          access the Enterprise AI
          Workspace.
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
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Full name
                  </FormLabel>

                  <FormControl>
                    <Input
                      type="text"
                      placeholder="Enter your full name"
                      autoComplete="name"
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
                  <FormLabel>
                    Password
                  </FormLabel>

                  <FormControl>
                    <div className="relative">
                      <Input
                        type={
                          showPassword
                            ? "text"
                            : "password"
                        }
                        placeholder="Create password"
                        autoComplete="new-password"
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

            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Confirm password
                  </FormLabel>

                  <FormControl>
                    <div className="relative">
                      <Input
                        type={
                          showConfirmPassword
                            ? "text"
                            : "password"
                        }
                        placeholder="Confirm password"
                        autoComplete="new-password"
                        disabled={isSubmitting}
                        className="pr-11"
                        {...field}
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowConfirmPassword(
                            (current) =>
                              !current,
                          )
                        }
                        disabled={isSubmitting}
                        aria-label={
                          showConfirmPassword
                            ? "Hide confirm password"
                            : "Show confirm password"
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition-colors hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {showConfirmPassword ? (
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

            <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
              Password must contain at
              least 8 characters, including
              uppercase, lowercase, number,
              and special character.
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                <>
                  <UserPlus className="h-4 w-4" />
                  Create account
                </>
              )}
            </Button>
          </form>
        </Form>

        <p className="mt-6 text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-semibold text-violet-700 hover:underline"
          >
            Sign in
          </Link>
        </p>
      </CardContent>
    </Card>
  )
}