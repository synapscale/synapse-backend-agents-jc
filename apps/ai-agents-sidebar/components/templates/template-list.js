"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TemplateList = TemplateList;
var lucide_react_1 = require("lucide-react");
var input_1 = require("@/components/ui/input");
var button_1 = require("@/components/ui/button");
var scroll_area_1 = require("@/components/ui/scroll-area");
var template_card_1 = require("@/components/templates/template-card");
var template_preview_1 = require("@/components/templates/template-preview");
function TemplateList(_a) {
    var templates = _a.templates, categories = _a.categories, selectedTemplate = _a.selectedTemplate, filterCategory = _a.filterCategory, searchQuery = _a.searchQuery, onSelectTemplate = _a.onSelectTemplate, onEditTemplate = _a.onEditTemplate, onDeleteTemplate = _a.onDeleteTemplate, onCopyContent = _a.onCopyContent, onUseTemplate = _a.onUseTemplate, onCreateTemplate = _a.onCreateTemplate, onManageCategories = _a.onManageCategories, onFilterCategoryChange = _a.onFilterCategoryChange, onSearchQueryChange = _a.onSearchQueryChange;
    return (<div className="py-3 sm:py-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4 mb-3 sm:mb-4">
        <div className="flex gap-2 w-full sm:w-auto">
          <button_1.Button variant="outline" size="sm" className="text-xs h-8 flex-1 sm:flex-initial" onClick={onCreateTemplate} aria-label="Criar novo template">
            <lucide_react_1.Plus className="mr-1 h-3.5 w-3.5" aria-hidden="true"/>
            Novo Template
          </button_1.Button>
          <button_1.Button variant="outline" size="sm" className="text-xs h-8 flex-1 sm:flex-initial" onClick={onManageCategories} aria-label="Gerenciar categorias">
            <lucide_react_1.Tag className="mr-1 h-3.5 w-3.5" aria-hidden="true"/>
            Categorias
          </button_1.Button>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-auto">
            <lucide_react_1.Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" aria-hidden="true"/>
            <input_1.Input placeholder="Buscar templates..." value={searchQuery} onChange={function (e) { return onSearchQueryChange(e.target.value); }} className="pl-8 h-8 text-xs w-full sm:w-[200px]" aria-label="Buscar templates"/>
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <lucide_react_1.Filter className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true"/>
            <select id="filter-category" className="h-8 rounded-md border border-input bg-background px-2 py-1 text-xs w-full sm:w-auto" value={filterCategory} onChange={function (e) { return onFilterCategoryChange(e.target.value); }} aria-label="Filtrar por categoria">
              <option value="todos">Todas as categorias</option>
              {categories.map(function (category) { return (<option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>); })}
            </select>
          </div>
        </div>
      </div>

      {templates.length === 0 ? (<div className="text-center py-6 sm:py-8">
          <div className="text-muted-foreground mb-2 text-sm">Nenhum template encontrado</div>
          <p className="text-xs sm:text-sm text-muted-foreground">
            {searchQuery ? "Tente ajustar sua busca ou filtros" : "Crie um novo template para começar"}
          </p>
        </div>) : (<scroll_area_1.ScrollArea className="h-[300px] sm:h-[400px] pr-3 sm:pr-4">
          <div className="space-y-2 sm:space-y-3">
            {templates.map(function (template) { return (<template_card_1.TemplateCard key={template.id} template={template} isSelected={(selectedTemplate === null || selectedTemplate === void 0 ? void 0 : selectedTemplate.id) === template.id} onSelect={onSelectTemplate} onEdit={onEditTemplate} onDelete={onDeleteTemplate} onCopy={onCopyContent} onUse={onUseTemplate}/>); })}
          </div>
        </scroll_area_1.ScrollArea>)}

      {selectedTemplate && <template_preview_1.TemplatePreview template={selectedTemplate} onUse={onUseTemplate}/>}
    </div>);
}
