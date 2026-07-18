import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  promptTemplateService,
} from "@/services/promptTemplateService"

import {
  queryKeys,
} from "@/services/queryKeys"

import type {
  CreatePromptTemplateRequest,
  PromptTemplateQueryParams,
  UpdatePromptTemplateRequest,
} from "@/types/promptTemplate"

export function usePromptTemplates(
  params: PromptTemplateQueryParams = {},
) {
  return useQuery({
    queryKey:
      queryKeys.promptTemplates.list(
        params,
      ),

    queryFn: () =>
      promptTemplateService.listTemplates(
        params,
      ),

    staleTime: 30_000,
  })
}

export function usePromptTemplate(
  templateId:
    | string
    | null
    | undefined,
) {
  return useQuery({
    queryKey:
      queryKeys.promptTemplates.detail(
        templateId ?? "",
      ),

    queryFn: () =>
      promptTemplateService.getTemplate(
        templateId as string,
      ),

    enabled: Boolean(
      templateId,
    ),
  })
}

export function useCreatePromptTemplate() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: (
      payload:
        CreatePromptTemplateRequest,
    ) =>
      promptTemplateService.createTemplate(
        payload,
      ),

    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.promptTemplates.all,
      })
    },
  })
}

interface UpdatePromptTemplateVariables {
  templateId: string
  payload:
    UpdatePromptTemplateRequest
}

export function useUpdatePromptTemplate() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: ({
      templateId,
      payload,
    }: UpdatePromptTemplateVariables) =>
      promptTemplateService.updateTemplate(
        templateId,
        payload,
      ),

    onSuccess: (
      updatedTemplate,
    ) => {
      queryClient.setQueryData(
        queryKeys.promptTemplates.detail(
          updatedTemplate.id,
        ),
        updatedTemplate,
      )

      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.promptTemplates.all,
      })
    },
  })
}

export function useDeletePromptTemplate() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: (
      templateId: string,
    ) =>
      promptTemplateService.deleteTemplate(
        templateId,
      ),

    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.promptTemplates.all,
      })
    },
  })
}

export function usePromptTemplateUsage() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: (
      templateId: string,
    ) =>
      promptTemplateService.incrementUsage(
        templateId,
      ),

    onSuccess: (
      updatedTemplate,
    ) => {
      queryClient.setQueryData(
        queryKeys.promptTemplates.detail(
          updatedTemplate.id,
        ),
        updatedTemplate,
      )

      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.promptTemplates.all,
      })
    },
  })
}