"use client";
"use strict";
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TemplateForm = TemplateForm;
var lucide_react_1 = require("lucide-react");
var button_1 = require("@/components/ui/button");
var input_field_1 = require("@/components/form/input-field");
var textarea_1 = require("@/components/ui/textarea");
var form_field_1 = require("@/components/form/form-field");
var category_selector_1 = require("@/components/templates/category-selector");
function TemplateForm(_a) {
    var template = _a.template, onChange = _a.onChange, onSubmit = _a.onSubmit, onCancel = _a.onCancel, onManageCategories = _a.onManageCategories, categories = _a.categories, isValid = _a.isValid, _b = _a.isEdit, isEdit = _b === void 0 ? false : _b;
    return (<div className="grid gap-3 sm:gap-4 py-3 sm:py-4">
      <input_field_1.InputField id="template-name" label="Nome do Template" value={template.name || ""} onChange={function (value) { return onChange("name", value); }} placeholder="Ex: Assistente de Vendas" required/>

      <input_field_1.InputField id="template-description" label="Descrição" value={template.description || ""} onChange={function (value) { return onChange("description", value); }} placeholder="Descreva o propósito deste template"/>

      <category_selector_1.CategorySelector selectedCategories={template.categories || []} availableCategories={categories} onAddCategory={function (category) {
            var currentCategories = template.categories || [];
            if (!currentCategories.includes(category)) {
                onChange("categories", __spreadArray(__spreadArray([], currentCategories, true), [category], false));
            }
        }} onRemoveCategory={function (category) {
            var currentCategories = template.categories || [];
            if (currentCategories.length > 1) {
                onChange("categories", currentCategories.filter(function (c) { return c !== category; }));
            }
        }} onManageCategories={onManageCategories}/>

      <form_field_1.FormField label="Conteúdo do Template" htmlFor="template-content" required>
        <textarea_1.Textarea id="template-content" value={template.content || ""} onChange={function (e) { return onChange("content", e.target.value); }} placeholder="# Título do Prompt&#10;&#10;Você é um assistente especializado em...&#10;&#10;## Capacidades:&#10;- Capacidade 1&#10;- Capacidade 2" className="min-h-[150px] sm:min-h-[200px] font-mono text-xs sm:text-sm"/>
      </form_field_1.FormField>

      <div className="flex flex-col sm:flex-row justify-end gap-2 sm:gap-3 mt-2">
        <button_1.Button variant="outline" size="sm" className="w-full sm:w-auto h-9" onClick={onCancel}>
          Cancelar
        </button_1.Button>
        <button_1.Button size="sm" className="w-full sm:w-auto h-9" onClick={onSubmit} disabled={!isValid}>
          <lucide_react_1.Save className="mr-1.5 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
          {isEdit ? "Atualizar Template" : "Salvar Template"}
        </button_1.Button>
      </div>
    </div>);
}
