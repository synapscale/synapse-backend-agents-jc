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
exports.Section = void 0;
var react_1 = require("react");
var utils_1 = require("@/lib/utils");
var lucide_react_1 = require("lucide-react");
/**
 * Section component
 *
 * A container for grouping related content with an optional title, description,
 * and actions. Can be made collapsible.
 *
 * @example
 * \`\`\`tsx
 * <Section
 *   title="User Information"
 *   description="Enter your personal details below"
 *   actions={<Button>Save</Button>}
 *   collapsible
 * >
 *   <form>...</form>
 * </Section>
 * \`\`\`
 */
var Section = function (_a) {
    var className = _a.className, children = _a.children, title = _a.title, description = _a.description, actions = _a.actions, _b = _a.collapsible, collapsible = _b === void 0 ? false : _b, _c = _a.defaultCollapsed, defaultCollapsed = _c === void 0 ? false : _c, onToggleCollapse = _a.onToggleCollapse, testId = _a.testId, props = __rest(_a, ["className", "children", "title", "description", "actions", "collapsible", "defaultCollapsed", "onToggleCollapse", "testId"]);
    var _d = (0, react_1.useState)(defaultCollapsed), isCollapsed = _d[0], setIsCollapsed = _d[1];
    var handleToggle = function () {
        var newState = !isCollapsed;
        setIsCollapsed(newState);
        onToggleCollapse === null || onToggleCollapse === void 0 ? void 0 : onToggleCollapse(newState);
    };
    return (<section className={(0, utils_1.cn)("rounded-lg border border-gray-200", className)} data-testid={testId} {...props}>
      {(title || description || actions) && (<div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
          <div>
            {title && <h2 className="text-lg font-medium text-gray-900">{title}</h2>}
            {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
          </div>
          <div className="flex items-center space-x-2">
            {actions}
            {collapsible && (<button type="button" onClick={handleToggle} className="ml-2 inline-flex h-8 w-8 items-center justify-center rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-600" aria-expanded={!isCollapsed} aria-label={isCollapsed ? "Expand section" : "Collapse section"}>
                {isCollapsed ? <lucide_react_1.ChevronDown className="h-5 w-5"/> : <lucide_react_1.ChevronUp className="h-5 w-5"/>}
              </button>)}
          </div>
        </div>)}
      <div className={(0, utils_1.cn)("p-4", isCollapsed && collapsible ? "hidden" : "block")}>{children}</div>
    </section>);
};
exports.Section = Section;
