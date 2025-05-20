"use client"

import type React from "react"
import { useState } from "react"
import type { Skill, SkillVersion } from "@/types/skill-types"
import { MarketplaceService } from "@/services/marketplace-service"

/**
 * LicenseType - Enum for skill license types
 *
 * @enum {string}
 * @property {string} MIT - MIT License (most permissive)
 * @property {string} APACHE - Apache License 2.0
 * @property {string} GPL - GNU General Public License v3.0 (most restrictive)
 * @property {string} PROPRIETARY - Proprietary License (custom terms)
 */
export enum LicenseType {
  MIT = "MIT",
  APACHE = "Apache-2.0",
  GPL = "GPL-3.0",
  PROPRIETARY = "Proprietary",
}

/**
 * VisibilityType - Enum for skill visibility types
 *
 * @enum {string}
 * @property {string} PUBLIC - Visible to everyone
 * @property {string} UNLISTED - Only accessible with direct link
 * @property {string} PRIVATE - Only visible to the creator
 */
export enum VisibilityType {
  PUBLIC = "public",
  UNLISTED = "unlisted",
  PRIVATE = "private",
}

/**
 * PricingType - Enum for skill pricing types
 *
 * @enum {string}
 * @property {string} FREE - Free to use
 * @property {string} PAID - Requires payment
 */
export enum PricingType {
  FREE = "free",
  PAID = "paid",
}

/**
 * PublishFormData - Interface for skill publication form data
 *
 * @property {string} name - Skill name
 * @property {string} description - Skill description
 * @property {string[]} tags - Skill tags
 * @property {LicenseType} license - License type
 * @property {VisibilityType} visibility - Visibility type
 * @property {PricingType} pricing - Pricing type
 * @property {number} [price] - Price (required if pricing is PAID)
 * @property {string} [imageUrl] - Optional skill image URL
 * @property {string} [customLicenseTerms] - Custom license terms (required if license is PROPRIETARY)
 * @property {string} [version] - Version string (defaults to "1.0.0")
 * @property {string} [categoryId] - Optional category ID
 */
export interface PublishFormData {
  name: string
  description: string
  tags: string[]
  license: LicenseType
  visibility: VisibilityType
  pricing: PricingType
  price?: number
  imageUrl?: string
  customLicenseTerms?: string
  version?: string
  categoryId?: string
}

/**
 * PublishSkillFormProps - Interface for the PublishSkillForm component props
 *
 * @property {Skill} skill - The skill to publish
 * @property {SkillVersion} [skillVersion] - Optional specific version of the skill to publish
 * @property {(success: boolean, itemId?: string) => void} onComplete - Callback when publishing is complete
 * @property {() => void} onCancel - Callback when publishing is cancelled
 * @property {PublishFormData} [initialData] - Optional initial form data
 * @property {boolean} [isUpdate=false] - Whether this is an update to an existing marketplace item
 * @property {string} [existingItemId] - ID of the existing marketplace item (required if isUpdate is true)
 * @property {string} [className] - Optional additional CSS classes
 * @property {string} [title] - Optional custom title for the form
 * @property {string} [submitButtonText] - Optional custom text for the submit button
 * @property {boolean} [showCancelButton=true] - Whether to show the cancel button
 * @property {string} [cancelButtonText] - Optional custom text for the cancel button
 * @property {boolean} [showImageUpload=true] - Whether to show the image upload field
 * @property {boolean} [showVersionField=true] - Whether to show the version field
 * @property {boolean} [showCategoryField=true] - Whether to show the category field
 * @property {boolean} [requireDescription=true] - Whether the description field is required
 * @property {(formData: PublishFormData) => Promise<boolean>} [onValidate] - Optional custom validation function
 */
interface PublishSkillFormProps {
  skill: Skill
  skillVersion?: SkillVersion
  onComplete: (success: boolean, itemId?: string) => void
  onCancel: () => void
  initialData?: Partial<PublishFormData>
  isUpdate?: boolean
  existingItemId?: string
  className?: string
  title?: string
  submitButtonText?: string
  showCancelButton?: boolean
  cancelButtonText?: string
  showImageUpload?: boolean
  showVersionField?: boolean
  showCategoryField?: boolean
  requireDescription?: boolean
  onValidate?: (formData: PublishFormData) => Promise<boolean>
}

/**
 * PublishSkillForm - A form for publishing or updating a skill in the marketplace
 *
 * This component provides a complete form for publishing a skill to the marketplace
 * or updating an existing marketplace item. It handles form validation, submission,
 * and error handling.
 *
 * @example
 * // Basic usage for publishing a new skill
 * <PublishSkillForm
 *   skill={mySkill}
 *   onComplete={(success, itemId) => {
 *     if (success) {
 *       console.log(`Skill published with ID: ${itemId}`);
 *       router.push(`/marketplace/items/${itemId}`);
 *     }
 *   }}
 *   onCancel={() => setShowPublishForm(false)}
 * />
 *
 * @example
 * // Updating an existing marketplace item
 * <PublishSkillForm
 *   skill={mySkill}
 *   isUpdate={true}
 *   existingItemId="item-123"
 *   initialData={{
 *     name: "My Awesome Skill",
 *     description: "This skill does amazing things",
 *     tags: ["automation", "productivity"],
 *     license: LicenseType.MIT,
 *     visibility: VisibilityType.PUBLIC,
 *     pricing: PricingType.FREE
 *   }}
 *   onComplete={(success) => {
 *     if (success) {
 *       toast.success("Skill updated successfully");
 *       closeModal();
 *     }
 *   }}
 *   onCancel={closeModal}
 * />
 */
export function PublishSkillForm({
  skill,
  skillVersion,
  onComplete,
  onCancel,
  initialData = {},
  isUpdate = false,
  existingItemId,
  className = "",
  title = isUpdate ? "Update Skill" : "Publish Skill to Marketplace",
  submitButtonText = isUpdate ? "Update" : "Publish",
  showCancelButton = true,
  cancelButtonText = "Cancel",
  showImageUpload = true,
  showVersionField = true,
  showCategoryField = true,
  requireDescription = true,
  onValidate
}: PublishSkillFormProps) {
  // Form state
  const [formData, setFormData] = useState<PublishFormData>({
    name: initialData.name || skill.name,
    description: initialData.description || skill.description || "",
    tags: initialData.tags || [],
    license: initialData.license || LicenseType.MIT,
    visibility: initialData.visibility || VisibilityType.PUBLIC,
    pricing: initialData.pricing || PricingType.FREE,
    price: initialData.price,
    imageUrl: initialData.imageUrl,
    customLicenseTerms: initialData.customLicenseTerms,
    version: initialData.version || skillVersion?.version || "1.0.0",
    categoryId: initialData.categoryId
  });

  // Form submission state
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Handle form field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
    
    // Clear field-specific error when field is changed
    if (formErrors[name]) {
      setFormErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // Handle tag changes
  const handleTagsChange = (tags: string[]) => {
    setFormData((prev) => ({
      ...prev,
      tags
    }));
    
    // Clear tags error when tags are changed
    if (formErrors.tags) {
      setFormErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors.tags;
        return newErrors;
      });
    }
  };

  // Validate form data
  const validateForm = async (): Promise<boolean> => {
    const errors: Record<string, string> = {};
    
    // Required fields
    if (!formData.name.trim()) {
      errors.name = "Name is required";
    }
    
    if (requireDescription && !formData.description.trim()) {
      errors.description = "Description is required";
    }
    
    if (formData.tags.length === 0) {
      errors.tags = "At least one tag is required";
    }
    
    // Pricing validation
    if (formData.pricing === PricingType.PAID) {
      if (!formData.price || formData.price <= 0) {
        errors.price = "Price must be greater than zero";
      }
    }
    
    // License validation
    if (formData.license === LicenseType.PROPRIETARY && !formData.customLicenseTerms?.trim()) {
      errors.customLicenseTerms = "Custom license terms are required for proprietary license";
    }
    
    // Version validation
    if (showVersionField && !formData.version?.trim()) {
      errors.version = "Version is required";
    }
    
    // Update form errors
    setFormErrors(errors);
    
    // Check if there are any errors
    if (Object.keys(errors).length > 0) {
      return false;
    }
    
    // Custom validation if provided
    if (onValidate) {
      try {
        const isValid = await onValidate(formData);
        return isValid;
      } catch (error) {
        console.error("Validation error:", error);
        setError("An error occurred during validation");
        return false;
      }
    }
    
    return true;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // Validate form
    const isValid = await validateForm();
    if (!isValid) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      let itemId: string;
      
      if (isUpdate && existingItemId) {
        // Update existing marketplace item
        await MarketplaceService.updateMarketplaceItem(existingItemId, {
          ...formData,
          skillId: skill.id,
          skillVersionId: skillVersion?.id
        });
        itemId = existingItemId;
      } else {
        // Publish new marketplace item
        const result = await MarketplaceService.publishSkill({
          ...formData,
          skillId: skill.id,
          skillVersionId: skillVersion?.id
        });
        itemId = result.id;
      }
      
      onComplete(true, itemId);
    } catch (error) {
      console.error("Error publishing skill:", error);
      setError("An error occurred while publishing the skill. Please try again.");
      onComplete(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`w-full ${className}`}>
      <h2 className="text-2xl font-bold mb-6">{title}</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Name field */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full"
          />

\
