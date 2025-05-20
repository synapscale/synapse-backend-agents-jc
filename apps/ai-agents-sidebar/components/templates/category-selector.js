"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CategorySelector = CategorySelector;
var lucide_react_1 = require("lucide-react");
var badge_1 = require("@/components/ui/badge");
var button_1 = require("@/components/ui/button");
var form_field_1 = require("@/components/form/form-field");
var popover_1 = require("@/components/ui/popover");
var command_1 = require("@/components/ui/command");
var use_disclosure_1 = require("@hooks/use-disclosure");
function CategorySelector(_a) {
    var selectedCategories = _a.selectedCategories, availableCategories = _a.availableCategories, onAddCategory = _a.onAddCategory, onRemoveCategory = _a.onRemoveCategory, onManageCategories = _a.onManageCategories;
    var popover = (0, use_disclosure_1.useDisclosure)();
    return (<form_field_1.FormField label="Categorias" headerRight={<button_1.Button variant="ghost" size="sm" className="h-7 sm:h-8 px-2 text-xs" onClick={onManageCategories}>
          <lucide_react_1.Tag className="h-3 w-3 sm:h-3.5 sm:w-3.5 mr-1" aria-hidden="true"/>
          Gerenciar Categorias
        </button_1.Button>}>
      <div className="flex flex-col gap-2">
        <div className="flex flex-wrap gap-1.5 sm:gap-2 mb-2" role="group" aria-label="Categorias selecionadas">
          {selectedCategories.map(function (category) { return (<badge_1.Badge key={category} variant="secondary" className="px-1.5 sm:px-2 py-0.5 sm:py-1 text-xs">
              {category}
              <button className="ml-1 text-muted-foreground hover:text-foreground p-0.5" onClick={function () { return onRemoveCategory(category); }} aria-label={"Remover categoria ".concat(category)} disabled={selectedCategories.length <= 1}>
                <lucide_react_1.X className="h-2.5 w-2.5 sm:h-3 sm:w-3" aria-hidden="true"/>
              </button>
            </badge_1.Badge>); })}
        </div>

        <popover_1.Popover open={popover.isOpen} onOpenChange={popover.toggle}>
          <popover_1.PopoverTrigger asChild>
            <button_1.Button variant="outline" size="sm" className="w-full justify-start h-8 sm:h-9 text-xs sm:text-sm" aria-label="Adicionar categoria">
              <lucide_react_1.Plus className="mr-1.5 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true"/>
              Adicionar categoria
            </button_1.Button>
          </popover_1.PopoverTrigger>
          <popover_1.PopoverContent className="p-0" align="start" side="bottom">
            <command_1.Command>
              <command_1.CommandInput placeholder="Buscar categoria..." className="h-9"/>
              <command_1.CommandList className="max-h-[200px] sm:max-h-[250px]">
                <command_1.CommandEmpty>Nenhuma categoria encontrada.</command_1.CommandEmpty>
                <command_1.CommandGroup>
                  {availableCategories.map(function (category) { return (<command_1.CommandItem key={category} onSelect={function () {
                onAddCategory(category);
                popover.close();
            }} disabled={selectedCategories.includes(category)} className="py-1.5 sm:py-2">
                      <lucide_react_1.Check className={"mr-1.5 h-3.5 w-3.5 sm:h-4 sm:w-4 ".concat(selectedCategories.includes(category) ? "opacity-100" : "opacity-0")} aria-hidden="true"/>
                      {category}
                    </command_1.CommandItem>); })}
                </command_1.CommandGroup>
              </command_1.CommandList>
            </command_1.Command>
          </popover_1.PopoverContent>
        </popover_1.Popover>
      </div>
    </form_field_1.FormField>);
}
