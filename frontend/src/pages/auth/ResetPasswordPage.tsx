import {
  useState,
} from "react"

import {
  zodResolver,
} from "@hookform/resolvers/zod"

import {
  Eye,
  EyeOff,
  KeyRound,
} from "lucide-react"

import {
  useForm,
} from "react-hook-form"

import {
  Link,
  useNavigate,
} from "react-router-dom"

import {
  toast,
} from "sonner"

import {
  z,
} from "zod"

import {
  Button,
} from "@/components/ui/button"

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

import {
  Input,
} from "@/components/ui/input"

const passwordRule =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$/

const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(
        8,
        "Password must contain at least 8 characters",
      )
      .regex(
        passwordRule,
        "Use uppercase, lowercase, number and special character",
      ),

    confirmPassword: z.string(),
  })
  .refine(
    (data) =>
      data.password ===
      data.confirmPassword,
    {
      message: "Passwords do not match",
      path: ["confirmPassword"],
    },
  )

type ResetPasswordValues =
  z.infer<typeof resetPasswordSchema>

export function ResetPasswordPage() {
  const navigate = useNavigate()

  const [showPassword, setShowPassword] =
    useState(false)

  const form =
    useForm<ResetPasswordValues>({
      resolver: zodResolver(
        resetPasswordSchema,
      ),

      defaultValues: {
        password: "",
        confirmPassword: "",
      },
    })

  const onSubmit = (
    values: ResetPasswordValues,
  ) => {
    console.log(values)

    toast.success(
      "Password reset successfully.",
    )

    navigate("/login")
  }

  return (
    <Card className="shadow-xl">
      <CardHeader>
        <CardTitle className="text-2xl">
          Reset password
        </CardTitle>

        <CardDescription>
          Enter and confirm your new
          password.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="space-y-5"
          >
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    New password
                  </FormLabel>

                  <FormControl>
                    <div className="relative">
                      <Input
                        type={
                          showPassword
                            ? "text"
                            : "password"
                        }
                        className="pr-11"
                        {...field}
                      />

                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword(
                            (current) => !current,
                          )
                        }
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500"
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
                    <Input
                      type="password"
                      {...field}
                    />
                  </FormControl>

                  <FormMessage />
                </FormItem>
              )}
            />

            <Button
              type="submit"
              className="w-full"
            >
              <KeyRound />
              Reset password
            </Button>
          </form>
        </Form>

        <Link
          to="/login"
          className="mt-4 block text-center text-sm font-medium hover:underline"
        >
          Return to login
        </Link>
      </CardContent>
    </Card>
  )
}