/* eslint-disable react-refresh/only-export-components */

import * as React from "react"
import * as LabelPrimitive from "@radix-ui/react-label"
import { Slot } from "@radix-ui/react-slot"
import {
  Controller,
  FormProvider,
  useFormContext,
  useFormState,
} from "react-hook-form"

import type {
  ControllerProps,
  FieldPath,
  FieldValues,
} from "react-hook-form"

import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

const Form = FormProvider

type FormFieldContextValue<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> =
    FieldPath<TFieldValues>,
> = {
  name: TName
}

const FormFieldContext =
  React.createContext<FormFieldContextValue>(
    {} as FormFieldContextValue,
  )

const FormField = <
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> =
    FieldPath<TFieldValues>,
>({
  ...props
}: ControllerProps<TFieldValues, TName>) => {
  return (
    <FormFieldContext.Provider
      value={{
        name: props.name,
      }}
    >
      <Controller {...props} />
    </FormFieldContext.Provider>
  )
}

type FormItemContextValue = {
  id: string
}

const FormItemContext =
  React.createContext<FormItemContextValue>(
    {} as FormItemContextValue,
  )

function useFormField() {
  const fieldContext =
    React.useContext(FormFieldContext)

  const itemContext =
    React.useContext(FormItemContext)

  const {
    getFieldState,
  } = useFormContext()

  const formState = useFormState({
    name: fieldContext.name,
  })

  const fieldState = getFieldState(
    fieldContext.name,
    formState,
  )

  if (!fieldContext.name) {
    throw new Error(
      "useFormField must be used inside <FormField>",
    )
  }

  return {
    id: itemContext.id,
    name: fieldContext.name,
    formItemId:
      `${itemContext.id}-form-item`,
    formDescriptionId:
      `${itemContext.id}-form-item-description`,
    formMessageId:
      `${itemContext.id}-form-item-message`,
    ...fieldState,
  }
}

function FormItem({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const id = React.useId()

  return (
    <FormItemContext.Provider
      value={{ id }}
    >
      <div
        className={cn(
          "grid gap-2",
          className,
        )}
        {...props}
      />
    </FormItemContext.Provider>
  )
}

function FormLabel({
  className,
  ...props
}: React.ComponentProps<
  typeof LabelPrimitive.Root
>) {
  const {
    error,
    formItemId,
  } = useFormField()

  return (
    <Label
      htmlFor={formItemId}
      className={cn(
        error && "text-destructive",
        className,
      )}
      {...props}
    />
  )
}

function FormControl({
  ...props
}: React.ComponentProps<typeof Slot>) {
  const {
    error,
    formItemId,
    formDescriptionId,
    formMessageId,
  } = useFormField()

  return (
    <Slot
      id={formItemId}
      aria-describedby={
        error
          ? `${formDescriptionId} ${formMessageId}`
          : formDescriptionId
      }
      aria-invalid={Boolean(error)}
      {...props}
    />
  )
}

function FormDescription({
  className,
  ...props
}: React.ComponentProps<"p">) {
  const {
    formDescriptionId,
  } = useFormField()

  return (
    <p
      id={formDescriptionId}
      className={cn(
        "text-sm text-muted-foreground",
        className,
      )}
      {...props}
    />
  )
}

function FormMessage({
  className,
  children,
  ...props
}: React.ComponentProps<"p">) {
  const {
    error,
    formMessageId,
  } = useFormField()

  const message =
    error?.message
      ? String(error.message)
      : children

  if (!message) {
    return null
  }

  return (
    <p
      id={formMessageId}
      className={cn(
        "text-sm text-destructive",
        className,
      )}
      {...props}
    >
      {message}
    </p>
  )
}

export {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  useFormField,
}