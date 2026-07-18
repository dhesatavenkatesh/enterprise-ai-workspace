import {
  apiClient,
} from "@/services/apiClient"

import type {
  CreatePromptTemplateRequest,
  PromptTemplate,
  PromptTemplateListResponse,
  PromptTemplateQueryParams,
  UpdatePromptTemplateRequest,
} from "@/types/promptTemplate"

function normalizeTemplateList(
  data:
    | PromptTemplate[]
    | PromptTemplateListResponse,
): PromptTemplateListResponse {
  if (Array.isArray(data)) {
    return {
      items: data,
      total: data.length,
      page: 1,
      page_size: data.length,
      total_pages: 1,
    }
  }

  return data
}

export const promptTemplateService = {
  async listTemplates(
    params: PromptTemplateQueryParams = {},
  ): Promise<PromptTemplateListResponse> {
    const response =
      await apiClient.get<
        PromptTemplate[] |
        PromptTemplateListResponse
      >(
        "/api/prompt-templates",
        {
          params,
        },
      )

    return normalizeTemplateList(
      response.data,
    )
  },

  async getTemplate(
    templateId: string,
  ): Promise<PromptTemplate> {
    const response =
      await apiClient.get<PromptTemplate>(
        `/api/prompt-templates/${templateId}`,
      )

    return response.data
  },

  async createTemplate(
    payload: CreatePromptTemplateRequest,
  ): Promise<PromptTemplate> {
    const response =
      await apiClient.post<PromptTemplate>(
        "/api/prompt-templates",
        payload,
      )

    return response.data
  },

  async updateTemplate(
    templateId: string,
    payload: UpdatePromptTemplateRequest,
  ): Promise<PromptTemplate> {
    const response =
      await apiClient.patch<PromptTemplate>(
        `/api/prompt-templates/${templateId}`,
        payload,
      )

    return response.data
  },

  async deleteTemplate(
    templateId: string,
  ): Promise<void> {
    await apiClient.delete(
      `/api/prompt-templates/${templateId}`,
    )
  },

  async incrementUsage(
    templateId: string,
  ): Promise<PromptTemplate> {
    const response =
      await apiClient.post<PromptTemplate>(
        `/api/prompt-templates/${templateId}/use`,
      )

    return response.data
  },
}