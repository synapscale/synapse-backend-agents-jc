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
exports.FormField = void 0;
var utils_1 = require("@/lib/utils");
var label_1 = require("@/components/ui/label");
/**
 * FormField component
 *
 * A wrapper for form inputs that provides consistent styling and layout,
 * including label, error message, and helper text.
 *
 * @example
 * \`\`\`tsx
 * <FormField
 *   label="Email Address"
 *   name="email"
 *   required
 *   error={errors.email}
 *   helperText="We'll never share your email with anyone else."
 * >
 *   <input type="email" name="email" />
 * </FormField>
 * \`\`\`
 */
var FormField = function (_a) {
    var className = _a.className, children = _a.children, label = _a.label, name = _a.name, error = _a.error, _b = _a.required, required = _b === void 0 ? false : _b, helperText = _a.helperText, id = _a.id, headerRight = _a.headerRight, props = __rest(_a, ["className", "children", "label", "name", "error", "required", "helperText", "id", "headerRight"]);
    var inputId = id || name;
    return (<div className={(0, utils_1.cn)("mb-4", className)} {...props}>
      <div className="flex items-center justify-between">
        {label && (<label_1.Label htmlFor={inputId} className="mb-1 block text-sm font-medium text-gray-700">
            {label}
            {required && <span className="ml-1 text-red-500">*</span>}
          </label_1.Label>)}
        {headerRight}
      </div>
      {children}
      {helperText && !error && <p className="mt-1 text-sm text-gray-500">{helperText}</p>}
      {error && (<p className="mt-1 text-sm text-red-600" id={"".concat(inputId, "-error")}>
          {error}
        </p>)}
    </div>);
};
exports.FormField = FormField;
