"use client";
"use strict";
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.IconButton = IconButton;
var utils_1 = require("@/lib/utils");
/**
 * IconButton component
 *
 * A button that displays an icon, optionally with a label.
 *
 * @example
 * ```tsx
 * <IconButton
 *   icon={<PlusIcon />}
 *   label="Add Item"
 *   onClick={handleAdd}
 *   variant="outline"
 * />
 * ```
 */
function IconButton(_a) {
    var icon = _a.icon, label = _a.label, _b = _a.variant, variant = _b === void 0 ? "default" : _b, _c = _a.size, size = _c === void 0 ? "md" : _c, _d = _a.displayMode, displayMode = _d === void 0 ? "icon-only" : _d, _e = _a.loading, loading = _e === void 0 ? false : _e, className = _a.className, props = __rest(_a, ["icon", "label", "variant", "size", "displayMode", "loading", "className"]);
    // Size classes
    var sizeClasses = {
        xs: "h-6 w-6 text-xs",
        sm: "h-8 w-8 text-sm",
        md: "h-10 w-10 text-base",
        lg: "h-12 w-12 text-lg",
        xl: "h-14 w-14 text-xl",
    };
    // Variant classes
    var variantClasses = {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
    };
    // Display mode classes
    var displayModeClasses = {
        "icon-only": "p-0",
        "icon-and-label": "flex items-center justify-center gap-1 px-3",
    };
    return (<button type="button" className={(0, utils_1.cn)("inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none", displayMode === "icon-only" ? sizeClasses[size] : "", variantClasses[variant], displayModeClasses[displayMode], className)} aria-label={label} disabled={loading || props.disabled} {...props}>
      {icon}
      {displayMode === "icon-and-label" && <span>{label}</span>}
      {loading && (<span className="absolute inset-0 flex items-center justify-center">
          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>)}
    </button>);
}
