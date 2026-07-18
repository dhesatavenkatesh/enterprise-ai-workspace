import {
  zodResolver,
} from "@hookform/resolvers/zod"

import {
  ArrowLeft,
  Mail,
} from "lucide-react"

import {
  useForm,
} from "react-hook-form"

import {
  Link,
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

const forgotPasswordSchema =
  z.object({
    email: z
      .string()
      .min(1, "Email is required")
      .email(
        "Enter a valid email address",
      ),
  })

type ForgotPasswordValues =
  z.infer<
    typeof forgotPasswordSchema
  >

export function ForgotPasswordPage() {
  const form =
    useForm<ForgotPasswordValues>({
      resolver: zodResolver(
        forgotPasswordSchema,
      ),

      defaultValues: {
        email: "",
      },
    })

  const onSubmit = (
    values: ForgotPasswordValues,
  ) => {
    console.log(values)

    toast.success(
      "Password reset instructions have been requested.",
    )

    form.reset()
  }

  return (
    <Card className="shadow-xl">
      <CardHeader>
        <CardTitle className="text-2xl">
          Forgot password
        </CardTitle>

        <CardDescription>
          Enter your email address and we
          will send reset instructions.
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
              <Mail />
              Send instructions
            </Button>
          </form>
        </Form>

       <Link
  to="/login"
  className="mt-4 flex h-9 w-full items-center justify-center gap-2 rounded-md px-4 text-sm font-medium transition-colors hover:bg-slate-100"
>
  <ArrowLeft className="h-4 w-4" />
  Back to login
</Link>
      </CardContent>
    </Card>
  )
}