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
exports.InputField = void 0;
var react_1 = require("react");
var form_field_1 = require("./form-field");
var input_1 = require("@/components/ui/input");
var utils_1 = require("@/lib/utils");
exports.InputField = (0, react_1.forwardRef)(function (_a, ref) {
    var id = _a.id, name = _a.name, label = _a.label, _b = _a.value, value = _b === void 0 ? "" : _b, onChange = _a.onChange, placeholder = _a.placeholder, _c = _a.type, type = _c === void 0 ? "text" : _c, _d = _a.required, required = _d === void 0 ? false : _d, error = _a.error, helperText = _a.helperText, className = _a.className, _e = _a.disabled, disabled = _e === void 0 ? false : _e, maxLength = _a.maxLength, autoComplete = _a.autoComplete, _f = _a.autoFocus, autoFocus = _f === void 0 ? false : _f, props = __rest(_a, ["id", "name", "label", "value", "onChange", "placeholder", "type", "required", "error", "helperText", "className", "disabled", "maxLength", "autoComplete", "autoFocus"]);
    var inputId = id || name;
    var _g = (0, react_1.useState)(false), isFocused = _g[0], setIsFocused = _g[1];
    var showCharCount = maxLength && type === "text";
    var handleChange = function (e) {
        onChange === null || onChange === void 0 ? void 0 : onChange(e.target.value);
    };
    return (<form_field_1.FormField label={label} name={name} error={error} required={required} helperText={helperText} id={inputId}>
        <div className="relative">
          <input_1.Input ref={ref} id={inputId} name={name} type={type} value={value} onChange={handleChange} onFocus={function () { return setIsFocused(true); }} onBlur={function () { return setIsFocused(false); }} placeholder={placeholder} disabled={disabled} maxLength={maxLength} autoComplete={autoComplete} autoFocus={autoFocus} className={(0, utils_1.cn)(isFocused && "border-purple-500 ring-1 ring-purple-500", error && "border-red-300 focus-visible:ring-red-500", showCharCount && "pr-16", className)} aria-invalid={!!error} aria-describedby={error ? "".concat(inputId, "-error") : helperText ? "".concat(inputId, "-helper") : undefined} required={required} {...props}/>
          {showCharCount && (<div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground pointer-events-none">
              {value.length}/{maxLength}
            </div>)}
        </div>
      </form_field_1.FormField>);
});
exports.InputField.displayName = "InputField";
