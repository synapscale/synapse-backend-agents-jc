"use client";
"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CategoryManager = CategoryManager;
var lucide_react_1 = require("lucide-react");
var button_1 = require("@/components/ui/button");
var input_1 = require("@/components/ui/input");
var badge_1 = require("@/components/ui/badge");
var scroll_area_1 = require("@/components/ui/scroll-area");
var react_1 = require("react");
function CategoryManager(_a) {
    var categories = _a.categories, onAddCategory = _a.onAddCategory, onUpdateCategory = _a.onUpdateCategory, onDeleteCategory = _a.onDeleteCategory, onBack = _a.onBack, templateCounts = _a.templateCounts;
    var _b = (0, react_1.useState)(""), newCategory = _b[0], setNewCategory = _b[1];
    var _c = (0, react_1.useState)(null), editingCategory = _c[0], setEditingCategory = _c[1];
    var handleAddCategory = function () {
        if (!newCategory.trim())
            return;
        onAddCategory(newCategory.trim().toLowerCase());
        setNewCategory("");
    };
    var handleUpdateCategory = function () {
        if (!editingCategory || !editingCategory.new.trim())
            return;
        onUpdateCategory(editingCategory.original, editingCategory.new.trim().toLowerCase());
        setEditingCategory(null);
    };
    return (<div className="py-3 sm:py-4">
      <div className="flex items-center gap-2 mb-3 sm:mb-4">
        <input_1.Input placeholder="Nova categoria..." value={newCategory} onChange={function (e) { return setNewCategory(e.target.value); }} className="flex-1 h-8 sm:h-9 text-sm" aria-label="Nome da nova categoria"/>
        <button_1.Button onClick={handleAddCategory} disabled={!newCategory.trim()} size="sm" className="h-8 sm:h-9" aria-label="Adicionar nova categoria">
          <lucide_react_1.Plus className="mr-1.5 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
          <span className="text-xs sm:text-sm">Adicionar</span>
        </button_1.Button>
      </div>

      <div className="border rounded-md">
        <div className="py-2 px-3 sm:px-4 bg-muted/50 border-b text-xs sm:text-sm font-medium">
          Categorias Existentes
        </div>
        <scroll_area_1.ScrollArea className="h-[250px] sm:h-[300px]">
          <div className="p-3 sm:p-4 space-y-1.5 sm:space-y-2">
            {categories.map(function (category) { return (<div key={category} className="flex items-center justify-between p-1.5 sm:p-2 border rounded-md group">
                {editingCategory && editingCategory.original === category ? (<div className="flex items-center gap-1.5 sm:gap-2 flex-1">
                    <input_1.Input value={editingCategory.new} onChange={function (e) { return setEditingCategory(__assign(__assign({}, editingCategory), { new: e.target.value })); }} className="h-7 sm:h-8 text-xs sm:text-sm" autoFocus aria-label={"Editar categoria ".concat(category)}/>
                    <button_1.Button size="sm" variant="ghost" onClick={handleUpdateCategory} className="h-7 w-7 sm:h-8 sm:w-8 p-0" aria-label="Salvar alterações">
                      <lucide_react_1.Check className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
                    </button_1.Button>
                    <button_1.Button size="sm" variant="ghost" onClick={function () { return setEditingCategory(null); }} className="h-7 w-7 sm:h-8 sm:w-8 p-0" aria-label="Cancelar edição">
                      <lucide_react_1.X className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
                    </button_1.Button>
                  </div>) : (<>
                    <div className="flex items-center gap-2">
                      <badge_1.Badge variant="outline" className="bg-muted/30 text-xs">
                        {category}
                      </badge_1.Badge>
                      <span className="text-xs text-muted-foreground">{templateCounts[category] || 0} templates</span>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button_1.Button size="sm" variant="ghost" className="h-7 w-7 sm:h-8 sm:w-8 p-0" onClick={function () { return setEditingCategory({ original: category, new: category }); }} disabled={category === "geral"} // Não permitir editar a categoria "geral"
             aria-label={"Editar categoria ".concat(category)}>
                        <lucide_react_1.Edit className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
                        <span className="sr-only">Editar</span>
                      </button_1.Button>
                      <button_1.Button size="sm" variant="ghost" className="h-7 w-7 sm:h-8 sm:w-8 p-0 text-destructive hover:text-destructive" onClick={function () { return onDeleteCategory(category); }} disabled={category === "geral"} // Não permitir excluir a categoria "geral"
             aria-label={"Excluir categoria ".concat(category)}>
                        <lucide_react_1.Trash2 className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
                        <span className="sr-only">Excluir</span>
                      </button_1.Button>
                    </div>
                  </>)}
              </div>); })}
          </div>
        </scroll_area_1.ScrollArea>
      </div>

      <div className="flex justify-end mt-4">
        <button_1.Button variant="outline" size="sm" className="w-full sm:w-auto h-9" onClick={onBack}>
          Voltar
        </button_1.Button>
      </div>
    </div>);
}
