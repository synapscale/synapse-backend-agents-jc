"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.SidebarNavSection = SidebarNavSection;
var jsx_runtime_1 = require("react/jsx-runtime");
var React = __importStar(require("react"));
function SidebarNavSection(_a) {
    var title = _a.title, children = _a.children, _b = _a.collapsible, collapsible = _b === void 0 ? false : _b, _c = _a.defaultCollapsed, defaultCollapsed = _c === void 0 ? false : _c;
    var _d = React.useState(defaultCollapsed), isCollapsed = _d[0], setIsCollapsed = _d[1];
    var toggleCollapse = React.useCallback(function () {
        if (collapsible) {
            setIsCollapsed(function (prev) { return !prev; });
        }
    }, [collapsible]);
    return ((0, jsx_runtime_1.jsxs)("div", { style: { marginBottom: 16 }, children: [(0, jsx_runtime_1.jsxs)("div", { style: {
                    fontSize: 12,
                    fontWeight: 500,
                    color: "#888",
                    marginBottom: 4,
                    display: "flex",
                    alignItems: "center",
                    cursor: collapsible ? "pointer" : "default",
                }, onClick: toggleCollapse, children: [(0, jsx_runtime_1.jsx)("span", { style: { flex: 1 }, children: title }), collapsible && ((0, jsx_runtime_1.jsx)("span", { style: { fontSize: 10 }, children: isCollapsed ? "+" : "-" }))] }), (0, jsx_runtime_1.jsx)("div", { style: { display: isCollapsed ? "none" : "block" }, children: children })] }));
}
