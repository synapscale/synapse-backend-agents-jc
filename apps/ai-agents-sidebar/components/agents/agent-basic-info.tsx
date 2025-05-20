"use client"
import { InputField } from "@/components/form/input-field"
import { SelectField } from "@/components/form/select-field"
import { MODEL_OPTIONS, STATUS_OPTIONS, TYPE_OPTIONS } from "@/constants/agent-constants"
import type { AgentBasicInfoProps } from "@/types/component-params"

/**
 * Component for the basic information section of the agent form
 *
 * This component displays and manages the basic information fields for an agent,
 * including name, type, model, description, and status.
 *
 * @example
 * ```tsx
 * <AgentBasicInfo
 *   name={form.values.name}
 *   type={form.values.type}
 *   model={form.values.model}
 *   description={form.values.description}
 *   status={form.values.status}
 *   onChangeName={(value) => form.handleChange("name", value)}
 *   onChangeType={(value) => form.handleChange("type", value)}
 *   onChangeModel={(value) => form.handleChange("model", value)}
 *   onChangeDescription={(value) => form.handleChange("description", value)}
 *   onChangeStatus={(value) => form.handleChange("status", value)}
 *   onBlurName={() => form.handleBlur("name")}
 *   nameError={form.errors.name}
 *   isNewAgent={true}
 * />
 * ```
 *
 * @param props - Component properties
 * @returns React component
 */
export function AgentBasicInfo({
  // Required props
  name,
  type,
  model,
  description,
  status,
  onChangeName,
  onChangeType,
  onChangeModel,
  onChangeDescription,
  onChangeStatus,
  onBlurName,
  isNewAgent,

  // Optional props with defaults
  nameError,
  descriptionMaxLength = 200,
  nameMaxLength = 50,
  descriptionPlaceholder = "Breve descrição do agente",
  namePlaceholder = "Digite o nome do agente",

  // Accessibility props
  className,
  id,
  testId,
  ariaLabel,
}: AgentBasicInfoProps) {
  const componentId = id || "agent-basic-info"

  return (
    <div
      className={className}
      id={componentId}
      data-testid={testId}
      aria-label={ariaLabel || "Informações básicas do agente"}
    >
      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <div className="w-full sm:w-1/2">
          <InputField
            id={`${componentId}-name`}
            label="Nome do Agente"
            name="name"
            value={name}
            onChange={onChangeName}
            onBlur={onBlurName}
            placeholder={namePlaceholder}
            required
            error={nameError}
            maxLength={nameMaxLength}
            autoFocus={isNewAgent}
            aria-describedby={nameError ? `${componentId}-name-error` : undefined}
          />
        </div>

        <div className="w-full sm:w-1/2 flex gap-3 sm:gap-4">
          <div className="w-1/2">
            <SelectField
              id={`${componentId}-type`}
              label="Tipo"
              name="type"
              value={type}
              onChange={onChangeType}
              options={TYPE_OPTIONS}
              aria-label="Tipo do agente"
            />
          </div>

          <div className="w-1/2">
            <SelectField
              id={`${componentId}-model`}
              label="Modelo"
              name="model"
              value={model}
              onChange={onChangeModel}
              options={MODEL_OPTIONS}
              aria-label="Modelo do agente"
            />
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mt-3 sm:mt-4">
        <div className="w-full sm:w-1/2">
          <InputField
            id={`${componentId}-description`}
            label="Descrição"
            name="description"
            value={description}
            onChange={onChangeDescription}
            placeholder={descriptionPlaceholder}
            maxLength={descriptionMaxLength}
            aria-label="Descrição do agente"
          />
        </div>

        <div className="w-full sm:w-1/2">
          <SelectField
            id={`${componentId}-status`}
            label="Status"
            name="status"
            value={status}
            onChange={onChangeStatus}
            options={STATUS_OPTIONS}
            aria-label="Status do agente"
          />
        </div>
      </div>
    </div>
  )
}
