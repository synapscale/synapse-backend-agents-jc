"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TemplateCard = TemplateCard;
var lucide_react_1 = require("lucide-react");
var button_1 = require("@/components/ui/button");
var badge_1 = require("@/components/ui/badge");
var dropdown_menu_1 = require("@/components/ui/dropdown-menu");
var utils_1 = require("@/lib/utils");
function TemplateCard(_a) {
    var template = _a.template, isSelected = _a.isSelected, onSelect = _a.onSelect, onEdit = _a.onEdit, onDelete = _a.onDelete, onCopy = _a.onCopy, onUse = _a.onUse;
    return (<div className={(0, utils_1.cn)("p-2.5 sm:p-3 border rounded-lg hover:border-purple-200 transition-colors cursor-pointer", isSelected && "border-purple-300 bg-purple-50")} onClick={function () { return onSelect(template); }} role="button" tabIndex={0} aria-label={"Template: ".concat(template.name)} onKeyDown={function (e) {
            if (e.key === "Enter" || e.key === " ") {
                onSelect(template);
            }
        }}>
      <div className="flex justify-between items-start">
        <div className="mr-2">
          <h4 className="font-medium text-xs sm:text-sm">{template.name}</h4>
          <p className="text-xs text-gray-500 mt-0.5 sm:mt-1 line-clamp-1">{template.description}</p>
        </div>
        <dropdown_menu_1.DropdownMenu>
          <dropdown_menu_1.DropdownMenuTrigger asChild>
            <button_1.Button variant="ghost" size="icon" className="h-6 w-6 sm:h-7 sm:w-7" onClick={function (e) { return e.stopPropagation(); }} aria-label="Opções do template">
              <lucide_react_1.MoreHorizontal className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
              <span className="sr-only">Ações</span>
            </button_1.Button>
          </dropdown_menu_1.DropdownMenuTrigger>
          <dropdown_menu_1.DropdownMenuContent align="end" className="w-[180px]">
            <dropdown_menu_1.DropdownMenuItem onClick={function (e) {
            e.stopPropagation();
            onUse(template);
        }} className="text-xs sm:text-sm py-1.5">
              <lucide_react_1.Check className="mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
              Usar Template
            </dropdown_menu_1.DropdownMenuItem>
            <dropdown_menu_1.DropdownMenuItem onClick={function (e) {
            e.stopPropagation();
            onEdit(template);
        }} className="text-xs sm:text-sm py-1.5">
              <lucide_react_1.Edit className="mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
              Editar
            </dropdown_menu_1.DropdownMenuItem>
            <dropdown_menu_1.DropdownMenuItem onClick={function (e) {
            e.stopPropagation();
            onCopy(template.content);
        }} className="text-xs sm:text-sm py-1.5">
              <lucide_react_1.Copy className="mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
              Copiar Conteúdo
            </dropdown_menu_1.DropdownMenuItem>
            <dropdown_menu_1.DropdownMenuItem className="text-red-600 text-xs sm:text-sm py-1.5" onClick={function (e) {
            e.stopPropagation();
            onDelete(template.id);
        }}>
              <lucide_react_1.Trash2 className="mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
              Excluir
            </dropdown_menu_1.DropdownMenuItem>
          </dropdown_menu_1.DropdownMenuContent>
        </dropdown_menu_1.DropdownMenu>
      </div>
      <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mt-1.5 sm:mt-2">
        {template.categories.map(function (category) { return (<badge_1.Badge key={category} variant="outline" className="bg-muted/30 px-1.5 sm:px-2 py-0 sm:py-0.5 text-[10px] sm:text-xs">
            {category}
          </badge_1.Badge>); })}
        <span className="text-[10px] sm:text-xs text-gray-400">
          {new Date(template.createdAt).toLocaleDateString()}
        </span>
      </div>
    </div>);
}
