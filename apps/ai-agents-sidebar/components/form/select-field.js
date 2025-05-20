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
exports.SelectField = void 0;
var react_1 = require("react");
var utils_1 = require("@/lib/utils");
var form_field_1 = require("@/components/form/form-field");
var lucide_react_1 = require("lucide-react");
exports.SelectField = (0, react_1.forwardRef)(function (_a, ref) {
    var id = _a.id, name = _a.name, label = _a.label, value = _a.value, onChange = _a.onChange, options = _a.options, _b = _a.placeholder, placeholder = _b === void 0 ? "Selecione uma opção" : _b, _c = _a.required, required = _c === void 0 ? false : _c, error = _a.error, helperText = _a.helperText, className = _a.className, _d = _a.disabled, disabled = _d === void 0 ? false : _d, props = __rest(_a, ["id", "name", "label", "value", "onChange", "options", "placeholder", "required", "error", "helperText", "className", "disabled"]);
    var selectId = id || name;
    var _e = (0, react_1.useState)(false), isFocused = _e[0], setIsFocused = _e[1];
    var handleChange = function (e) {
        onChange === null || onChange === void 0 ? void 0 : onChange(e.target.value);
    };
    return (<form_field_1.FormField label={label} name={name} error={error} required={required} helperText={helperText} id={selectId}>
        <div className="relative">
          <select ref={ref} id={selectId} name={name} value={value} onChange={handleChange} onFocus={function () { return setIsFocused(true); }} onBlur={function () { return setIsFocused(false); }} disabled={disabled} className={(0, utils_1.cn)("flex h-9 w-full appearance-none rounded-md border border-input bg-background px-3 py-1 pr-8 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50", isFocused && "border-purple-500 ring-1 ring-purple-500", error && "border-red-300 focus-visible:ring-red-500", className)} aria-invalid={!!error} aria-describedby={error ? "".concat(selectId, "-error") : helperText ? "".concat(selectId, "-helper") : undefined} required={required} {...props}>
            {placeholder && (<option value="" disabled>
                {placeholder}
              </option>)}
            {options.map(function (option) { return (<option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </option>); })}
          </select>
          <lucide_react_1.ChevronDown className="absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none"/>
        </div>
      </form_field_1.FormField>);
});
exports.SelectField.displayName = "SelectField";
