"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BadgeList = BadgeList;
var react_1 = require("react");
var lucide_react_1 = require("lucide-react");
var button_1 = require("@/components/ui/button");
var input_1 = require("@/components/ui/input");
var badge_1 = require("@/components/ui/badge");
var utils_1 = require("@/lib/utils");
/**
 * A component for displaying and managing a list of badges
 *
 * This component allows users to view, add, edit, and remove badges.
 * It's useful for managing tags, categories, or any other list of items.
 *
 * @example
 * ```tsx
 * <BadgeList
 *   items={tags}
 *   onAdd={addTag}
 *   onRemove={removeTag}
 *   onEdit={editTag}
 *   addLabel="Tag"
 *   maxItems={10}
 *   emptyMessage="No tags added yet"
 * />
 * ```
 *
 * @param props - Component properties
 * @returns React component
 */
function BadgeList(_a) {
    var 
    // Required props
    items = _a.items, onAdd = _a.onAdd, onRemove = _a.onRemove, 
    // Optional props with defaults
    onEdit = _a.onEdit, _b = _a.addLabel, addLabel = _b === void 0 ? "Item" : _b, _c = _a.maxItems, maxItems = _c === void 0 ? 10 : _c, className = _a.className, _d = _a.emptyMessage, emptyMessage = _d === void 0 ? "Nenhum item adicionado" : _d, _e = _a.readOnly, readOnly = _e === void 0 ? false : _e, _f = _a.addButtonVariant, addButtonVariant = _f === void 0 ? "outline" : _f, _g = _a.badgeVariant, badgeVariant = _g === void 0 ? "secondary" : _g, _h = _a.sortable, sortable = _h === void 0 ? false : _h, onReorder = _a.onReorder, _j = _a.confirmRemoval, confirmRemoval = _j === void 0 ? false : _j, removeBadgeAriaLabel = _a.removeBadgeAriaLabel, 
    // Accessibility props
    id = _a.id, testId = _a.testId, ariaLabel = _a.ariaLabel;
    var _k = (0, react_1.useState)(null), editingId = _k[0], setEditingId = _k[1];
    var _l = (0, react_1.useState)(""), editValue = _l[0], setEditValue = _l[1];
    var inputRef = (0, react_1.useRef)(null);
    // Focus input when editing starts
    (0, react_1.useEffect)(function () {
        if (editingId && inputRef.current) {
            inputRef.current.focus();
        }
    }, [editingId]);
    var handleStartEdit = function (item) {
        if (onEdit && !readOnly) {
            setEditingId(item.id);
            setEditValue(item.label);
        }
    };
    var handleSaveEdit = function () {
        if (editingId && onEdit && editValue.trim()) {
            onEdit(editingId, editValue.trim());
            setEditingId(null);
            setEditValue("");
        }
    };
    var handleKeyDown = function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            handleSaveEdit();
        }
        else if (e.key === "Escape") {
            setEditingId(null);
            setEditValue("");
        }
    };
    var handleRemove = function (id) {
        if (confirmRemoval) {
            if (window.confirm("Are you sure you want to remove this item?")) {
                onRemove(id);
            }
        }
        else {
            onRemove(id);
        }
    };
    var componentId = id || "badge-list";
    return (<div className={(0, utils_1.cn)("space-y-3", className)} id={componentId} data-testid={testId} aria-label={ariaLabel || "List of ".concat(addLabel.toLowerCase(), "s")}>
      <div className="flex flex-wrap gap-2">
        {items.length === 0 ? (<p className="text-sm text-muted-foreground">{emptyMessage}</p>) : (items.map(function (item) { return (<div key={item.id} className="flex items-center">
              {editingId === item.id && onEdit && !readOnly ? (<div className="flex items-center border rounded-md overflow-hidden">
                  <input_1.Input ref={inputRef} type="text" value={editValue} onChange={function (e) { return setEditValue(e.target.value); }} onBlur={handleSaveEdit} onKeyDown={handleKeyDown} className="h-7 min-w-[150px] border-0 focus-visible:ring-0 focus-visible:ring-offset-0" aria-label={"Edit ".concat(addLabel.toLowerCase())} data-testid={"".concat(componentId, "-edit-input-").concat(item.id)}/>
                  <button_1.Button type="button" variant="ghost" size="sm" className="h-7 px-2" onClick={function () { return setEditingId(null); }} aria-label="Cancel editing">
                    <lucide_react_1.X className="h-3 w-3" aria-hidden="true"/>
                    <span className="sr-only">Cancelar</span>
                  </button_1.Button>
                </div>) : (<badge_1.Badge variant={badgeVariant} className="px-2 py-1 h-7 text-xs font-normal bg-gray-100 hover:bg-gray-200 group">
                  <span className={(0, utils_1.cn)("mr-1", onEdit && !readOnly && "cursor-pointer hover:underline")} onClick={function () { return onEdit && !readOnly && handleStartEdit(item); }} data-testid={"".concat(componentId, "-label-").concat(item.id)}>
                    {item.label}
                  </span>
                  {!readOnly && (<button type="button" onClick={function () { return handleRemove(item.id); }} className="inline-flex items-center justify-center rounded-full h-4 w-4 bg-gray-200 group-hover:bg-gray-300 transition-colors" aria-label={removeBadgeAriaLabel
                        ? removeBadgeAriaLabel.replace("{label}", item.label)
                        : "Remover ".concat(item.label)} data-testid={"".concat(componentId, "-remove-").concat(item.id)}>
                      <lucide_react_1.X className="h-2.5 w-2.5" aria-hidden="true"/>
                    </button>)}
                </badge_1.Badge>)}
            </div>); }))}
      </div>

      {!readOnly && items.length < maxItems && (<button_1.Button type="button" variant={addButtonVariant} size="sm" onClick={onAdd} className="h-8 text-xs bg-white hover:bg-gray-50" aria-label={"Adicionar ".concat(addLabel)} data-testid={"".concat(componentId, "-add-button")}>
          <lucide_react_1.Plus className="mr-1 h-3.5 w-3.5" aria-hidden="true"/>
          Adicionar {addLabel}
        </button_1.Button>)}
    </div>);
}
